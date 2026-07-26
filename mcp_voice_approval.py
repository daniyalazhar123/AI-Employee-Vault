"""
Voice Approval System — Twilio Voice API for Autonomous Approval Calls

Initiates an outbound Twilio Voice call when a task lands in
Pending_Approval/ with a confidence score below 75%. The administrator
hears the task details via TTS and presses:
    1 -> Approve  (file moves to Approved/)
    2 -> Reject   (file moves to Rejected/)
    3 -> Escalate (Ralph Wiggum fallback loop triggered)

Credentials (loaded from secrets_config / env):
    TWILIO_ACCOUNT_SID
    TWILIO_AUTH_TOKEN
    TWILIO_PHONE_NUMBER   (the Twilio-owned outbound number)
    ADMIN_PHONE_NUMBER     (the admin's mobile to call)

Usage:
    python mcp_voice_approval.py check       # Scan Pending_Approval once, trigger calls
    python mcp_voice_approval.py server      # Run FastAPI webhook server (default)
    python mcp_voice_approval.py watch       # Poll Pending_Approval every 30s
"""

import asyncio
import json
import logging
import os
import re
import sys
import time
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, List, Tuple

from audit_logger import setup_logging
logger = setup_logging('VoiceApproval')

sys.path.insert(0, str(Path(__file__).parent))
from secrets_config import SECRETS_DIR, load_secrets, get_secret_path
load_secrets()

from dependency_fallback_guard import (
    TwilioClientProxy,
    FastAPIProxy,
    UvicornProxy,
    Response,
    Request,
    TWILIO_AVAILABLE,
    FASTAPI_AVAILABLE,
    UVICORN_AVAILABLE,
)

VAULT_PATH = Path(__file__).parent
PENDING = VAULT_PATH / 'Pending_Approval'
APPROVED = VAULT_PATH / 'Approved'
REJECTED = VAULT_PATH / 'Rejected'
SIGNALS = VAULT_PATH / 'Signals'
DLQ = VAULT_PATH / 'Dead_Letter_Queue'
LOGS = VAULT_PATH / 'Logs'
PROCESSED_FILE = VAULT_PATH / 'data' / 'voice_approval_processed.txt'

CONFIDENCE_THRESHOLD = 75
DEFAULT_PORT = 8083
POLL_INTERVAL = 30


def _twiml_say(text: str) -> str:
    return f'<?xml version="1.0" encoding="UTF-8"?><Response><Say voice="alice" language="en-US">{_xml_escape(text)}</Say></Response>'


def _twiml_hangup() -> str:
    return '<?xml version="1.0" encoding="UTF-8"?><Response><Hangup/></Response>'


def _twiml_say_and_hangup(text: str) -> str:
    return f'<?xml version="1.0" encoding="UTF-8"?><Response><Say voice="alice" language="en-US">{_xml_escape(text)}</Say><Hangup/></Response>'


def _twiml_gather(text: str, action: str) -> str:
    return (
        f'<?xml version="1.0" encoding="UTF-8"?>'
        f'<Response><Gather input="dtmf" timeout="10" numDigits="1" action="{_xml_escape(action)}" method="POST">'
        f'<Say voice="alice" language="en-US">{_xml_escape(text)}</Say>'
        f'</Gather>'
        f'<Redirect>{_xml_escape(action)}</Redirect></Response>'
    )


def _twiml_redirect(action: str) -> str:
    return f'<?xml version="1.0" encoding="UTF-8"?><Response><Redirect>{_xml_escape(action)}</Redirect></Response>'


def _xml_escape(text: str) -> str:
    return text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;').replace("'", '&apos;')

app = FastAPIProxy(title='Voice Approval Webhook')


class VoiceApprovalSystem:
    """Autonomous voice approval system using Twilio Voice API."""

    def __init__(self, vault_path: Optional[Path] = None, webhook_base_url: Optional[str] = None):
        self.vault = Path(vault_path) if vault_path else VAULT_PATH
        self.pending = self.vault / 'Pending_Approval'
        self.approved = self.vault / 'Approved'
        self.rejected = self.vault / 'Rejected'
        self.signals = self.vault / 'Signals'
        self.dlq = self.vault / 'Dead_Letter_Queue'
        self.logs = self.vault / 'Logs'
        for d in [self.pending, self.approved, self.rejected, self.signals, self.dlq, self.logs]:
            d.mkdir(parents=True, exist_ok=True)

        self.webhook_base = webhook_base_url or os.environ.get(
            'VOICE_WEBHOOK_BASE', 'http://localhost:8083'
        )

        self.twilio_sid = os.environ.get('TWILIO_ACCOUNT_SID', '')
        self.twilio_token = os.environ.get('TWILIO_AUTH_TOKEN', '')
        self.twilio_number = os.environ.get('TWILIO_PHONE_NUMBER', '')
        self.admin_number = os.environ.get('ADMIN_PHONE_NUMBER', '')

        self._twilio_client = None
        self.processed_ids = self._load_processed()

    # ---- Credential Validation ----

    def credentials_ok(self) -> bool:
        missing = []
        if not self.twilio_sid:
            missing.append('TWILIO_ACCOUNT_SID')
        if not self.twilio_token:
            missing.append('TWILIO_AUTH_TOKEN')
        if not self.twilio_number:
            missing.append('TWILIO_PHONE_NUMBER')
        if not self.admin_number:
            missing.append('ADMIN_PHONE_NUMBER')
        if missing:
            logger.warning(f"Missing Twilio credentials: {', '.join(missing)}")
            return False
        return True

    @property
    def twilio_client(self):
        if self._twilio_client is None and self.credentials_ok():
            self._twilio_client = TwilioClientProxy(self.twilio_sid, self.twilio_token)
        return self._twilio_client

    # ---- Pending Approval Scanning ----

    def scan_pending_approvals(self) -> List[Dict]:
        """Return all pending approval files with confidence < threshold."""
        if not self.pending.exists():
            return []
        tasks = []
        for f in sorted(self.pending.glob('*.md')):
            if f.name in self.processed_ids:
                continue
            meta = self._parse_frontmatter(f)
            confidence = meta.get('confidence', 0)
            try:
                confidence = float(confidence)
            except (ValueError, TypeError):
                confidence = 0.0

            if confidence >= CONFIDENCE_THRESHOLD:
                logger.info(f"Skipping {f.name} (confidence={confidence} >= {CONFIDENCE_THRESHOLD})")
                continue

            tasks.append({
                'file': f,
                'filename': f.name,
                'confidence': confidence,
                'metadata': meta,
                'summary': self._summarize_task(f, meta),
            })
        return tasks

    def _parse_frontmatter(self, file_path: Path) -> Dict:
        """Parse YAML-like frontmatter from an .md file."""
        meta = {}
        try:
            content = file_path.read_text(encoding='utf-8')
        except Exception:
            return meta
        m = re.match(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
        if not m:
            return meta
        for line in m.group(1).splitlines():
            if ':' in line:
                key, _, val = line.partition(':')
                meta[key.strip().lower()] = val.strip()
        return meta

    def _summarize_task(self, file_path: Path, meta: Dict) -> str:
        """Build a short speech-friendly summary of the task."""
        content = file_path.read_text(encoding='utf-8')
        body = content.split('---', 2)[-1].strip() if content.count('---') >= 2 else content
        body = re.sub(r'[#*_`>|\[\]]+', '', body).strip()
        lines = [l for l in body.splitlines() if l.strip()]
        summary = ' '.join(lines[:5])[:500]
        task_type = meta.get('type', 'approval request')
        created_by = meta.get('created_by', 'the cloud agent')
        draft_file = meta.get('draft_file', '')
        return (
            f"You have a {task_type} from {created_by}. "
            f"{'The draft is: ' + draft_file + '. ' if draft_file else ''}"
            f"Details: {summary}"
        )

    # ---- Processed ID Tracking ----

    def _load_processed(self) -> set:
        if PROCESSED_FILE.exists():
            try:
                return set(PROCESSED_FILE.read_text(encoding='utf-8').splitlines())
            except Exception:
                return set()
        return set()

    def _save_processed(self):
        PROCESSED_FILE.parent.mkdir(parents=True, exist_ok=True)
        PROCESSED_FILE.write_text('\n'.join(sorted(self.processed_ids)), encoding='utf-8')

    # ---- Twilio Outbound Call ----

    def initiate_call(self, task: Dict) -> bool:
        """Place an outbound Twilio call for a given task."""
        if not self.credentials_ok():
            logger.error("Cannot initiate call: missing credentials")
            return False
        if not TWILIO_AVAILABLE:
            logger.error("Cannot initiate call: twilio package not installed")
            return False
        if not self.twilio_client:
            logger.error("Cannot initiate call: twilio client not initialized")
            return False

        call_id = str(uuid.uuid4())[:8]
        task_id = task['filename']
        voice_url = f"{self.webhook_base.rstrip('/')}/twilio/voice/{task_id}/{call_id}"

        try:
            call = self.twilio_client.calls.create(
                url=voice_url,
                to=self.admin_number,
                from_=self.twilio_number,
                timeout=30,
                machine_detection='DetectMessageEnd',
            )
            logger.info(f"Call initiated: SID={call.sid}, to={self.admin_number}, task={task_id}")
            self._log_call(call_id, task_id, 'initiated', call.sid)
            return True
        except Exception as e:
            logger.error(f"Failed to initiate call: {e}")
            self._log_call(call_id, task_id, 'failed', error=str(e))
            return False

    def _log_call(self, call_id: str, task_id: str, status: str,
                  call_sid: str = '', error: str = ''):
        log_file = self.logs / 'voice_approval_calls.jsonl'
        entry = {
            'timestamp': datetime.now().isoformat(),
            'call_id': call_id,
            'task_id': task_id,
            'status': status,
            'call_sid': call_sid,
            'error': error,
        }
        try:
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(entry) + '\n')
        except Exception as e:
            logger.error(f"Failed to write call log: {e}")

    # ---- File Movement ----

    def approve_task(self, filename: str) -> bool:
        """Move file from Pending_Approval to Approved."""
        src = self.pending / filename
        if not src.exists():
            logger.warning(f"Task not found for approval: {filename}")
            return False
        dst = self.approved / filename
        try:
            content = src.read_text(encoding='utf-8')
            content = re.sub(
                r'^status:\s*\S+', 'status: approved', content, count=1, flags=re.MULTILINE
            )
            dst.write_text(content, encoding='utf-8')
            src.unlink()
            logger.info(f"Approved: {filename} -> Approved/")
            self.processed_ids.add(filename)
            self._save_processed()
            return True
        except Exception as e:
            logger.error(f"Failed to approve {filename}: {e}")
            return False

    def reject_task(self, filename: str) -> bool:
        """Move file from Pending_Approval to Rejected."""
        src = self.pending / filename
        if not src.exists():
            logger.warning(f"Task not found for rejection: {filename}")
            return False
        dst = self.rejected / filename
        try:
            content = src.read_text(encoding='utf-8')
            content = re.sub(
                r'^status:\s*\S+', 'status: rejected', content, count=1, flags=re.MULTILINE
            )
            dst.write_text(content, encoding='utf-8')
            src.unlink()
            logger.info(f"Rejected: {filename} -> Rejected/")
            self.processed_ids.add(filename)
            self._save_processed()
            return True
        except Exception as e:
            logger.error(f"Failed to reject {filename}: {e}")
            return False

    def escalate_task(self, filename: str) -> bool:
        """Trigger Ralph Wiggum fallback loop by writing a signal file."""
        src = self.pending / filename
        if not src.exists():
            logger.warning(f"Task not found for escalation: {filename}")
            return False
        signal_file = self.signals / f'ESCALATE_RALPH_{datetime.now():%Y%m%d_%H%M%S}_{filename}'
        try:
            content = src.read_text(encoding='utf-8')
            signal_file.write_text(
                f"---\ntype: ralph_wiggum_escalation\n"
                f"original_file: {filename}\n"
                f"escalated_at: {datetime.now().isoformat()}\n"
                f"source: voice_approval\n"
                f"status: pending_ralph\n"
                f"---\n\n"
                f"# Ralph Wiggum Escalation\n\n"
                f"Voice approval requested escalation for: {filename}\n\n"
                f"--- Original Content ---\n\n{content}\n",
                encoding='utf-8'
            )
            logger.info(f"Escalated to Ralph Wiggum: {filename}")
            self.processed_ids.add(filename)
            self._save_processed()
            return True
        except Exception as e:
            logger.error(f"Failed to escalate {filename}: {e}")
            return False

    # ---- TwiML Generation ----

    def generate_twiml_voice(self, task_id: str, call_id: str) -> str:
        """Generate TwiML that reads task details and gathers DTMF input."""
        task_path = self.pending / task_id
        if not task_path.exists():
            return _twiml_say("The approval request is no longer available. Goodbye.")

        meta = self._parse_frontmatter(task_path)
        summary = self._summarize_task(task_path, meta)
        task_type = meta.get('type', 'approval request')
        confidence = meta.get('confidence', 'unknown')

        text = (
            f"You have a {task_type}. Confidence score is {confidence} percent. "
            f"{summary} "
            f"Press 1 to approve. Press 2 to reject. Press 3 to escalate to Ralph Wiggum. "
            f"Press any other key to repeat."
        )
        action = f'/twilio/gather/{task_id}/{call_id}'
        return _twiml_gather(text, action)

    def handle_gather(self, task_id: str, call_id: str, digits: str) -> str:
        """Process DTMF input and return response TwiML."""
        if digits == '1':
            ok = self.approve_task(task_id)
            msg = "Task approved. Goodbye." if ok else f"Failed to approve {task_id}."
        elif digits == '2':
            ok = self.reject_task(task_id)
            msg = "Task rejected. Goodbye." if ok else f"Failed to reject {task_id}."
        elif digits == '3':
            ok = self.escalate_task(task_id)
            msg = "Task escalated to Ralph Wiggum. Goodbye." if ok else f"Failed to escalate {task_id}."
        else:
            msg = "Invalid option. Goodbye."

        logger.info(f"Call {call_id}: digit={digits}, task={task_id}, result={msg}")
        self._log_call(call_id, task_id, f'completed_digit_{digits}')
        return _twiml_say_and_hangup(msg)

    # ---- High-Level Orchestration ----

    def check_and_call(self) -> int:
        """Scan Pending_Approval and initiate calls for all low-confidence tasks."""
        tasks = self.scan_pending_approvals()
        if not tasks:
            logger.info("No low-confidence tasks found in Pending_Approval")
            return 0

        logger.info(f"Found {len(tasks)} low-confidence task(s) requiring voice approval")
        initiated = 0
        for task in tasks:
            logger.info(f"  -> {task['filename']} (confidence={task['confidence']})")
            ok = self.initiate_call(task)
            if ok:
                initiated += 1
            else:
                self._move_to_dlq(task['file'], 'call_initiation_failed')
        return initiated

    def _move_to_dlq(self, file_path: Path, reason: str):
        try:
            dst = self.dlq / file_path.name
            file_path.rename(dst)
            logger.warning(f"Moved {file_path.name} to Dead_Letter_Queue ({reason})")
        except Exception as e:
            logger.error(f"Failed to move {file_path.name} to DLQ: {e}")

    def watch_loop(self):
        """Continuously poll Pending_Approval."""
        logger.info(f"Starting watch loop (poll every {POLL_INTERVAL}s)")
        while True:
            try:
                self.check_and_call()
            except Exception as e:
                logger.error(f"Watch loop error: {e}")
            time.sleep(POLL_INTERVAL)


# ---- FastAPI Routes (always registered; FastAPIProxy handles real vs fallback) ----

@app.on_event('startup')
async def startup():
    logger.info(f"Voice Approval webhook server starting on port {DEFAULT_PORT}")

@app.get('/health')
async def health():
    return {'status': 'ok', 'service': 'voice-approval', 'timestamp': datetime.now().isoformat()}

@app.post('/twilio/voice/{task_id}/{call_id}')
async def twilio_voice(task_id: str, call_id: str):
    vs = VoiceApprovalSystem()
    twiml = vs.generate_twiml_voice(task_id, call_id)
    return Response(content=twiml, media_type='application/xml')

@app.post('/twilio/gather/{task_id}/{call_id}')
async def twilio_gather(task_id: str, call_id: str, request: Request):
    form = await request.form()
    digits = form.get('Digits', '')
    vs = VoiceApprovalSystem()
    twiml = vs.handle_gather(task_id, call_id, digits)
    return Response(content=twiml, media_type='application/xml')


# ---- CLI ----

def main():
    if len(sys.argv) < 2 or sys.argv[1] in ('server', 'serve'):
        if not FASTAPI_AVAILABLE:
            logger.error("fastapi/uvicorn required for server mode. pip install fastapi uvicorn")
            sys.exit(1)
        port = int(os.environ.get('VOICE_PORT', DEFAULT_PORT))
        logger.info(f"Starting Voice Approval webhook server on 0.0.0.0:{port}")
        UvicornProxy.run(app, host='0.0.0.0', port=port, log_level='info')

    elif sys.argv[1] == 'check':
        vs = VoiceApprovalSystem()
        count = vs.check_and_call()
        logger.info(f"Initiated {count} call(s)")
        sys.exit(0 if count > 0 else 0)

    elif sys.argv[1] == 'watch':
        vs = VoiceApprovalSystem()
        vs.watch_loop()

    elif sys.argv[1] == 'status':
        vs = VoiceApprovalSystem()
        tasks = vs.scan_pending_approvals()
        creds_ok = vs.credentials_ok()
        print(f"Voice Approval System Status")
        print(f"  Credentials configured: {'YES' if creds_ok else 'NO'}")
        print(f"  Twilio available:       {'YES' if TWILIO_AVAILABLE else 'NO'}")
        print(f"  FastAPI available:      {'YES' if FASTAPI_AVAILABLE else 'NO'}")
        print(f"  Pending_Approval files: {len(list(vs.pending.glob('*.md')))}")
        print(f"  Low-confidence tasks:   {len(tasks)}")
        print(f"  Processed IDs tracked:  {len(vs.processed_ids)}")
        if tasks:
            for t in tasks:
                print(f"    - {t['filename']} (confidence={t['confidence']})")
        print(f"  Webhook base: {vs.webhook_base}")

    else:
        print(f"Usage: python mcp_voice_approval.py <command>")
        print(f"  server  - Run FastAPI webhook server (default)")
        print(f"  check   - Scan Pending_Approval and trigger calls once")
        print(f"  watch   - Continuously poll Pending_Approval")
        print(f"  status  - Show system status")
        sys.exit(1)


if __name__ == '__main__':
    main()
