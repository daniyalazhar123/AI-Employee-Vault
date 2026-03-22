"""
Orchestrator - AI Employee Vault

Main orchestrator script that triggers Qwen Code CLI for processing.
Replaces Claude Code with Qwen CLI for all automation tasks.

Usage:
    python orchestrator.py [command]
    
Commands:
    process_needs_action  - Process all files in Needs_Action folder
    process_email         - Process email action files
    process_whatsapp      - Process WhatsApp action files
    process_social        - Process social media drafts
    process_odoo          - Process Odoo lead files
    run_ralph_loop        - Start Ralph Wiggum persistent loop
    generate_briefing     - Generate CEO weekly briefing
"""

import os
import sys
import subprocess
from pathlib import Path
from datetime import datetime


# Paths
VAULT_PATH = Path(__file__).parent
NEEDS_ACTION = VAULT_PATH / "Needs_Action"
PENDING_APPROVAL = VAULT_PATH / "Pending_Approval"
DONE_FOLDER = VAULT_PATH / "Done"

# Qwen Code CLI Configuration
QWEN_COMMAND = os.getenv("QWEN_COMMAND", "qwen")  # Can be 'qwen' or 'qwen-code'
QWEN_ARGS = ["-y"]  # Auto-accept suggestions
QWEN_TIMEOUT = 180  # 3 minutes timeout


def ensure_folders():
    """Ensure required folders exist."""
    NEEDS_ACTION.mkdir(exist_ok=True)
    PENDING_APPROVAL.mkdir(exist_ok=True)
    DONE_FOLDER.mkdir(exist_ok=True)


def run_qwen(prompt: str, timeout: int = None) -> dict:
    """
    Run Qwen Code CLI with the given prompt.
    
    Args:
        prompt: The prompt to send to Qwen
        timeout: Timeout in seconds (default: QWEN_TIMEOUT)
    
    Returns:
        dict with success status, stdout, stderr, returncode
    """
    if timeout is None:
        timeout = QWEN_TIMEOUT
    
    print(f"\n🤖 Running Qwen Code CLI...")
    print(f"   Command: {QWEN_COMMAND} {' '.join(QWEN_ARGS)}")
    print(f"   Timeout: {timeout}s")
    
    try:
        result = subprocess.run(
            [QWEN_COMMAND] + QWEN_ARGS + [prompt],
            check=False,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',
            cwd=str(VAULT_PATH),
            timeout=timeout
        )
        
        return {
            'success': result.returncode == 0,
            'stdout': result.stdout.strip(),
            'stderr': result.stderr.strip(),
            'returncode': result.returncode
        }
        
    except subprocess.TimeoutExpired:
        print(f"⚠️  Qwen timeout ({timeout}s)")
        return {
            'success': False,
            'stdout': '',
            'stderr': f'Timeout after {timeout}s',
            'returncode': -1
        }
    except FileNotFoundError:
        print(f"❌ Qwen Code CLI not found: {QWEN_COMMAND}")
        print(f"   Install with: npm install -g @anthropic/qwen")
        return {
            'success': False,
            'stdout': '',
            'stderr': 'Qwen CLI not found',
            'returncode': -2
        }
    except Exception as e:
        print(f"❌ Error running Qwen: {e}")
        return {
            'success': False,
            'stdout': '',
            'stderr': str(e),
            'returncode': -3
        }


def process_needs_action():
    """Process all files in Needs_Action folder."""
    print("=" * 70)
    print("📥 PROCESSING NEEDS_ACTION FOLDER")
    print("=" * 70)
    
    ensure_folders()
    
    # Get all markdown files
    files = list(NEEDS_ACTION.glob("*.md"))
    
    if not files:
        print("ℹ️  No files in Needs_Action folder")
        return
    
    print(f"📊 Found {len(files)} file(s) to process")
    
    # Process each file
    for file in files:
        print(f"\n--- Processing: {file.name} ---")
        
        prompt = f"""Read the action file: {file.name} in Needs_Action folder.

Process this task completely:
1. Understand what needs to be done
2. Take appropriate actions (draft replies, update files, etc.)
3. Save any drafts in Pending_Approval folder
4. Move this file to Done/ folder when complete

Follow Company_Handbook.md rules for all actions.
"""
        
        result = run_qwen(prompt)
        
        if result['success']:
            print(f"✅ Successfully processed {file.name}")
        else:
            print(f"⚠️  Error processing {file.name}: {result['stderr']}")
    
    print("\n" + "=" * 70)
    print(f"✅ Processed {len(files)} file(s)")
    print("=" * 70)


def process_emails():
    """Process email action files specifically."""
    print("=" * 70)
    print("📧 PROCESSING EMAIL ACTION FILES")
    print("=" * 70)
    
    ensure_folders()
    
    # Get email files
    files = [f for f in NEEDS_ACTION.glob("EMAIL_*.md")]
    
    if not files:
        print("ℹ️  No email files to process")
        return
    
    print(f"📊 Found {len(files)} email(s)")
    
    for file in files:
        print(f"\n--- Processing: {file.name} ---")
        
        prompt = f"""Read the email action file: {file.name} in Needs_Action folder.

Draft a professional reply following Company_Handbook rules:
1. Read the email details carefully
2. Draft an appropriate response
3. Save the reply draft in Pending_Approval folder as REPLY_{file.stem}.md
4. Mark the original email as processed

Keep the tone professional and helpful.
"""
        
        result = run_qwen(prompt)
        
        if result['success']:
            print(f"✅ Reply draft created for {file.name}")
        else:
            print(f"⚠️  Error: {result['stderr']}")
    
    print("\n" + "=" * 70)
    print(f"✅ Processed {len(files)} email(s)")
    print("=" * 70)


def process_whatsapp_messages():
    """Process WhatsApp action files."""
    print("=" * 70)
    print("💬 PROCESSING WHATSAPP MESSAGES")
    print("=" * 70)
    
    ensure_folders()
    
    # Get WhatsApp files
    files = [f for f in NEEDS_ACTION.glob("WHATSAPP_*.md")]
    
    if not files:
        print("ℹ️  No WhatsApp files to process")
        return
    
    print(f"📊 Found {len(files)} message(s)")
    
    for file in files:
        print(f"\n--- Processing: {file.name} ---")
        
        prompt = f"""Read the WhatsApp message action file: {file.name} in Needs_Action folder.

Draft a professional response following Company_Handbook rules:
1. Read the message carefully
2. Identify the intent and urgency
3. Draft an appropriate response
4. Save the reply draft in Pending_Approval folder as REPLY_{file.stem}.md

Keep responses friendly yet professional. Use emojis when appropriate.
"""
        
        result = run_qwen(prompt)
        
        if result['success']:
            print(f"✅ Response drafted for {file.name}")
        else:
            print(f"⚠️  Error: {result['stderr']}")
    
    print("\n" + "=" * 70)
    print(f"✅ Processed {len(files)} message(s)")
    print("=" * 70)


def process_social_drafts():
    """Process social media drafts."""
    print("=" * 70)
    print("📱 PROCESSING SOCIAL MEDIA DRAFTS")
    print("=" * 70)
    
    ensure_folders()
    
    # Get social files
    files = [f for f in NEEDS_ACTION.glob("SOCIAL_*.md")]
    
    if not files:
        print("ℹ️  No social draft files to process")
        return
    
    print(f"📊 Found {len(files)} draft(s)")
    
    for file in files:
        print(f"\n--- Processing: {file.name} ---")
        
        prompt = f"""Read the social draft action file: {file.name} in Needs_Action folder.

Turn this into professional social media posts:
1. Create versions for LinkedIn, Facebook, Instagram, and Twitter
2. Add 3-5 relevant hashtags to each
3. Adjust tone for each platform
4. Save polished posts in Social_Drafts/Polished folder

Platform guidelines:
- LinkedIn: Professional, longer form
- Facebook: Friendly, engaging
- Instagram: Visual-focused, emoji-friendly
- Twitter: Concise (under 280 chars)
"""
        
        result = run_qwen(prompt)
        
        if result['success']:
            print(f"✅ Polished posts created from {file.name}")
        else:
            print(f"⚠️  Error: {result['stderr']}")
    
    print("\n" + "=" * 70)
    print(f"✅ Processed {len(files)} draft(s)")
    print("=" * 70)


def process_odoo_leads():
    """Process Odoo CRM lead files."""
    print("=" * 70)
    print("🎯 PROCESSING ODOO LEADS")
    print("=" * 70)
    
    ensure_folders()
    
    # Get Odoo files
    files = [f for f in NEEDS_ACTION.glob("ODOO_LEAD_*.md")]
    
    if not files:
        print("ℹ️  No Odoo lead files to process")
        return
    
    print(f"📊 Found {len(files)} lead(s)")
    
    for file in files:
        print(f"\n--- Processing: {file.name} ---")
        
        prompt = f"""Read the Odoo lead file: {file.name} in Needs_Action folder.

Process this CRM lead:
1. Review lead details and qualification status
2. Draft a personalized follow-up email
3. Save the reply draft in Pending_Approval folder as REPLY_{file.stem}.md
4. Update Dashboard.md with lead summary if relevant

Focus on converting the lead into a customer.
"""
        
        result = run_qwen(prompt)
        
        if result['success']:
            print(f"✅ Lead processed: {file.name}")
        else:
            print(f"⚠️  Error: {result['stderr']}")
    
    print("\n" + "=" * 70)
    print(f"✅ Processed {len(files)} lead(s)")
    print("=" * 70)


def run_ralph_loop(task_description: str):
    """Run Ralph Wiggum persistent loop."""
    print("=" * 70)
    print("🔁 STARTING RALPH LOOP")
    print("=" * 70)
    
    # Import and run ralph_loop
    ralph_script = VAULT_PATH / "ralph_loop.py"
    
    if not ralph_script.exists():
        print("❌ ralph_loop.py not found!")
        return
    
    try:
        result = subprocess.run(
            [sys.executable, str(ralph_script), task_description],
            check=False,
            text=True,
            encoding='utf-8',
            errors='replace'
        )
        
        print("\n" + "=" * 70)
        print("🏁 RALPH LOOP FINISHED")
        print("=" * 70)
        
    except Exception as e:
        print(f"❌ Error running Ralph Loop: {e}")


def generate_ceo_briefing():
    """Generate CEO weekly briefing."""
    print("=" * 70)
    print("📊 GENERATING CEO BRIEFING")
    print("=" * 70)
    
    briefing_script = VAULT_PATH / "ceo_briefing.py"
    
    if not briefing_script.exists():
        print("❌ ceo_briefing.py not found!")
        return
    
    try:
        result = subprocess.run(
            [sys.executable, str(briefing_script)],
            check=False,
            text=True,
            encoding='utf-8',
            errors='replace'
        )
        
        print("\n" + "=" * 70)
        print("🏁 BRIEFING GENERATED")
        print("=" * 70)
        
    except Exception as e:
        print(f"❌ Error generating briefing: {e}")


def show_help():
    """Show help information."""
    print("""
╔══════════════════════════════════════════════════════════════╗
║           AI EMPLOYEE ORCHESTRATOR - QWEN CODE               ║
╠══════════════════════════════════════════════════════════════╣
║  Usage: python orchestrator.py [command]                     ║
╠══════════════════════════════════════════════════════════════╣
║  Commands:                                                   ║
║    process_needs_action  - Process all files in Needs_Action ║
║    process_email         - Process email action files        ║
║    process_whatsapp      - Process WhatsApp messages         ║
║    process_social        - Process social media drafts       ║
║    process_odoo          - Process Odoo lead files           ║
║    run_ralph_loop        - Start Ralph Wiggum loop           ║
║    generate_briefing     - Generate CEO weekly briefing      ║
║    help                  - Show this help message            ║
╠══════════════════════════════════════════════════════════════╣
║  Environment Variables:                                      ║
║    QWEN_COMMAND        - Qwen CLI command (default: 'qwen')  ║
║    QWEN_TIMEOUT        - Timeout in seconds (default: 180)   ║
╚══════════════════════════════════════════════════════════════╝
""")


def main():
    """Main entry point."""
    print("\n" + "=" * 70)
    print("🤖 AI EMPLOYEE ORCHESTRATOR - QWEN CODE")
    print("=" * 70)
    print(f"   Vault Path: {VAULT_PATH}")
    print(f"   Qwen Command: {QWEN_COMMAND} {' '.join(QWEN_ARGS)}")
    print(f"   Timeout: {QWEN_TIMEOUT}s")
    print("=" * 70)
    
    # Get command from args
    if len(sys.argv) < 2:
        show_help()
        return
    
    command = sys.argv[1].lower()
    
    if command == "process_needs_action":
        process_needs_action()
    elif command == "process_email":
        process_emails()
    elif command == "process_whatsapp":
        process_whatsapp_messages()
    elif command == "process_social":
        process_social_drafts()
    elif command == "process_odoo":
        process_odoo_leads()
    elif command == "run_ralph_loop":
        if len(sys.argv) > 2:
            task = " ".join(sys.argv[2:])
            run_ralph_loop(task)
        else:
            print("❌ Task description required!")
            print("   Usage: python orchestrator.py run_ralph_loop \"Your task\"")
    elif command == "generate_briefing":
        generate_ceo_briefing()
    elif command == "help":
        show_help()
    else:
        print(f"❌ Unknown command: {command}")
        show_help()


if __name__ == "__main__":
    main()
