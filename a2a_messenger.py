#!/usr/bin/env python3
"""
📬 A2A MESSENGER - Platinum Tier (Optional Phase 2)
Agent-to-Agent Communication
Personal AI Employee Hackathon 0 - Platinum Tier

Optional upgrade from file-based handoffs to direct messaging.
Vault remains the audit record.
"""

import os
import sys
import json
import time
import requests
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional
import logging
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('a2a_messenger.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('A2AMessenger')


class A2AMessenger:
    """
    A2A Messenger - Direct agent-to-agent communication
    
    Optional upgrade from file-based handoffs.
    Falls back to file-based if HTTP fails.
    """
    
    def __init__(self, agent_type: str, config: Dict):
        self.agent_type = agent_type  # 'cloud' or 'local'
        self.config = config
        self.vault = Path(config.get('vault_path', '.'))
        self.signals = self.vault / 'Signals'
        
        # Ensure signals folder exists
        self.signals.mkdir(parents=True, exist_ok=True)
        
        # A2A endpoints
        self.cloud_endpoint = config.get('cloud_endpoint', 'http://localhost:8081')
        self.local_endpoint = config.get('local_endpoint', 'http://localhost:8082')
        
        # Statistics
        self.stats = {
            'messages_sent': 0,
            'messages_received': 0,
            'http_success': 0,
            'file_fallback': 0
        }
        
        logger.info(f"📬 A2A Messenger initialized ({agent_type})")
    
    def send_to_cloud(self, message_type: str, payload: Dict) -> bool:
        """Send message to Cloud Agent"""
        if self.agent_type != 'local':
            logger.warning("⚠️ Only Local Agent can send to Cloud")
            return False
        
        return self._send_message(self.cloud_endpoint, message_type, payload)
    
    def send_to_local(self, message_type: str, payload: Dict) -> bool:
        """Send message to Local Agent"""
        if self.agent_type != 'cloud':
            logger.warning("⚠️ Only Cloud Agent can send to Local")
            return False
        
        return self._send_message(self.local_endpoint, message_type, payload)
    
    def _send_message(self, endpoint: str, message_type: str, payload: Dict) -> bool:
        """Send message via HTTP or fallback to file"""
        message = {
            'from': self.agent_type,
            'type': message_type,
            'payload': payload,
            'timestamp': datetime.now().isoformat()
        }
        
        try:
            # Try HTTP first
            response = requests.post(
                f"{endpoint}/message",
                json=message,
                timeout=10
            )
            response.raise_for_status()
            
            self.stats['messages_sent'] += 1
            self.stats['http_success'] += 1
            logger.info(f"✅ Sent {message_type} via HTTP to {endpoint}")
            return True
            
        except Exception as e:
            logger.warning(f"⚠️ HTTP failed, using file fallback: {e}")
            self._write_signal_file(message_type, payload)
            self.stats['messages_sent'] += 1
            self.stats['file_fallback'] += 1
            return True
    
    def _write_signal_file(self, message_type: str, payload: Dict):
        """Fallback: Write to /Signals/ folder"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        signal_file = self.signals / f"{message_type}_{timestamp}.md"
        
        content = f"""---
type: a2a_signal
message_type: {message_type}
from: {self.agent_type}
timestamp: {datetime.now().isoformat()}
---

# 📬 A2A Signal (File Fallback)

**Type:** {message_type}  
**From:** {self.agent_type}  
**Timestamp:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

**Payload:**
```json
{json.dumps(payload, indent=2)}
```

---
*Note: HTTP delivery failed, using file-based fallback*
"""
        signal_file.write_text(content, encoding='utf-8')
        logger.info(f"✅ Signal written: {signal_file.name}")
    
    def receive_message(self, message: Dict) -> Dict:
        """Process received message"""
        from_agent = message.get('from', 'unknown')
        message_type = message.get('type', 'unknown')
        payload = message.get('payload', {})
        
        logger.info(f"📬 Received {message_type} from {from_agent}")
        self.stats['messages_received'] += 1
        
        # Handle message based on type
        response = {
            'status': 'received',
            'type': message_type,
            'timestamp': datetime.now().isoformat()
        }
        
        if message_type == 'approval_completed':
            response = self._handle_approval_completed(payload)
        elif message_type == 'draft_created':
            response = self._handle_draft_created(payload)
        elif message_type == 'health_check':
            response = self._handle_health_check(payload)
        else:
            logger.warning(f"⚠️ Unknown message type: {message_type}")
        
        return response
    
    def _handle_approval_completed(self, payload: Dict) -> Dict:
        """Handle approval completed notification"""
        logger.info(f"✅ Approval completed: {payload.get('approval_file', 'unknown')}")
        return {'status': 'processed', 'action': 'approval_completed'}
    
    def _handle_draft_created(self, payload: Dict) -> Dict:
        """Handle draft created notification"""
        logger.info(f"📝 Draft created: {payload.get('draft_file', 'unknown')}")
        return {'status': 'processed', 'action': 'draft_created'}
    
    def _handle_health_check(self, payload: Dict) -> Dict:
        """Handle health check message"""
        logger.info("💓 Health check received")
        return {'status': 'healthy', 'agent': self.agent_type}
    
    def get_stats(self) -> Dict:
        """Get messenger statistics"""
        return {
            'agent_type': self.agent_type,
            'timestamp': datetime.now().isoformat(),
            'stats': self.stats
        }


class A2AHTTPHandler(BaseHTTPRequestHandler):
    """HTTP handler for A2A messages"""
    
    messenger = None
    
    def do_POST(self):
        """Handle POST requests"""
        if self.path == '/message':
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            
            try:
                message = json.loads(post_data.decode('utf-8'))
                response = self.messenger.receive_message(message)
                
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(response).encode('utf-8'))
                
            except Exception as e:
                self.send_response(400)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'error': str(e)}).encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_GET(self):
        """Handle GET requests"""
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'status': 'healthy'}).encode('utf-8'))
        elif self.path == '/stats':
            stats = self.messenger.get_stats()
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(stats).encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        """Suppress default logging"""
        pass


def run_http_server(messenger: A2AMessenger, port: int):
    """Run HTTP server for A2A messages"""
    A2AHTTPHandler.messenger = messenger
    
    server = HTTPServer(('0.0.0.0', port), A2AHTTPHandler)
    logger.info(f"📬 A2A HTTP server starting on port {port}")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info("📬 A2A HTTP server stopped")
        server.shutdown()


def main():
    """Main entry point"""
    print("="*60)
    print("📬 PLATINUM TIER - A2A MESSENGER (Optional)")
    print("="*60)
    
    # Get agent type from argument
    agent_type = sys.argv[1] if len(sys.argv) > 1 else 'cloud'
    if agent_type not in ['cloud', 'local']:
        print("Usage: python a2a_messenger.py [cloud|local] [port] [vault_path]")
        sys.exit(1)
    
    # Get port
    port = int(sys.argv[2]) if len(sys.argv) > 2 else (8081 if agent_type == 'cloud' else 8082)
    
    # Get vault path
    vault_path = sys.argv[3] if len(sys.argv) > 3 else 'C:/Users/CC/Documents/Obsidian Vault'
    
    print(f"🎯 Agent Type: {agent_type}")
    print(f"🔌 Port: {port}")
    print(f"📂 Vault Path: {vault_path}")
    
    # Configuration
    config = {
        'vault_path': vault_path,
        'cloud_endpoint': 'http://localhost:8081',
        'local_endpoint': 'http://localhost:8082'
    }
    
    messenger = A2AMessenger(agent_type, config)
    
    print(f"\n🚀 Starting A2A Messenger in 3 seconds...")
    time.sleep(3)
    
    # Start HTTP server in background thread
    server_thread = threading.Thread(
        target=run_http_server,
        args=(messenger, port),
        daemon=True
    )
    server_thread.start()
    
    print(f"✅ A2A Messenger running on port {port}")
    print("📬 Press Ctrl+C to stop\n")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n⏹️  A2A Messenger stopped")


if __name__ == '__main__':
    main()
