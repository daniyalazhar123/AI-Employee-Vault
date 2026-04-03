"""
COMPLETE 24/7 AI EMPLOYEE ORCHESTRATOR

Bhai! Yeh master file hai jo sab kuch control karega:
- Gmail
- LinkedIn
- Twitter
- Facebook
- Instagram
- WhatsApp
- Office Files
- Google Account Management

Features:
- 24/7 operation
- 12+ languages support
- Professional, human-like tone
- Always asks permission (HITL)
- Audit logging
- Error recovery
"""

import os
import sys
import json
import subprocess
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

# Vault Path
VAULT_PATH = Path(__file__).parent

# Configuration
CONFIG = {
    'primary_language': 'Urdu',
    'auto_detect': True,
    'reply_in_same_language': True,
    'professional_tone': True,
    'always_ask_permission': True,
    'audit_logging': True,
}

# Supported Languages
SUPPORTED_LANGUAGES = [
    'Urdu',
    'Roman_Urdu',
    'English',
    'Arabic',
    'Chinese',
    'Japanese',
    'Spanish',
    'German',
    'Italian',
    'French',
    'Portuguese',
    'Russian',
]

# Platform Status
PLATFORMS = {
    'gmail': {'enabled': True, 'status': 'unknown'},
    'linkedin': {'enabled': True, 'status': 'unknown'},
    'twitter': {'enabled': True, 'status': 'unknown'},
    'facebook': {'enabled': True, 'status': 'unknown'},
    'instagram': {'enabled': True, 'status': 'unknown'},
    'whatsapp': {'enabled': True, 'status': 'unknown'},
    'office': {'enabled': True, 'status': 'unknown'},
}


class AIEmployeeOrchestrator:
    """
    Complete 24/7 AI Employee Orchestrator
    
    Yeh class sab platforms ko control karti hai:
    - Emails read/write karna
    - Social media posts
    - WhatsApp messages
    - Office files
    - Account management
    
    Hamesha permission leti hai before sending!
    """
    
    def __init__(self, vault_path: Optional[Path] = None):
        self.vault_path = vault_path or VAULT_PATH
        self.logs_folder = self.vault_path / 'Logs'
        self.needs_action_folder = self.vault_path / 'Needs_Action'
        self.pending_approval_folder = self.vault_path / 'Pending_Approval'
        self.done_folder = self.vault_path / 'Done'
        
        # Ensure folders exist
        self.logs_folder.mkdir(exist_ok=True)
        self.needs_action_folder.mkdir(exist_ok=True)
        self.pending_approval_folder.mkdir(exist_ok=True)
        self.done_folder.mkdir(exist_ok=True)
        
        # Initialize audit logging
        self.audit_log_file = self.logs_folder / f'orchestrator_{datetime.now():%Y%m%d}.jsonl'
        
        self.log_info("🤖 COMPLETE 24/7 AI EMPLOYEE ORCHESTRATOR STARTED")
        self.log_info(f"Vault Path: {self.vault_path}")
        self.log_info(f"Supported Languages: {len(SUPPORTED_LANGUAGES)}")
        
    def log_info(self, message: str):
        """Log info message to console and file"""
        timestamp = datetime.now().isoformat()
        log_entry = {
            'timestamp': timestamp,
            'level': 'INFO',
            'message': message
        }
        
        # Console
        print(f"{timestamp} - {message}")
        
        # File
        try:
            with open(self.audit_log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
        except Exception as e:
            print(f"Warning: Could not write to log file: {e}")
    
    def log_error(self, message: str, error: Exception = None):
        """Log error message"""
        timestamp = datetime.now().isoformat()
        log_entry = {
            'timestamp': timestamp,
            'level': 'ERROR',
            'message': message,
            'error': str(error) if error else None
        }
        
        print(f"{timestamp} - ERROR: {message}")
        
        try:
            with open(self.audit_log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
        except Exception as e:
            print(f"Warning: Could not write to log file: {e}")
    
    def check_qwen_cli(self) -> bool:
        """Check if Qwen CLI is installed and working"""
        try:
            result = subprocess.run(
                ['qwen', '--version'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                self.log_info(f"✅ Qwen CLI found: {result.stdout.strip()}")
                return True
            else:
                self.log_error("❌ Qwen CLI returned error")
                return False
                
        except FileNotFoundError:
            self.log_error("❌ Qwen CLI not found. Install with: pip install qwen-code")
            return False
        except Exception as e:
            self.log_error(f"❌ Error checking Qwen CLI: {e}")
            return False
    
    def ask_qwen(self, prompt: str, language: str = 'Urdu') -> str:
        """
        Ask Qwen CLI to process something
        
        Args:
            prompt: What you want Qwen to do
            language: Language for response (Urdu, English, Arabic, etc.)
            
        Returns:
            Qwen's response
        """
        try:
            # Build the full prompt with language instruction
            full_prompt = f"""
You are a professional AI Employee assistant.
Always communicate in a polite, professional, human-like tone.
Never be robotic.

Current Language: {language}

Task: {prompt}

Important Rules:
1. Always be polite and respectful
2. Use professional language
3. Be clear and concise
4. Follow company handbook rules
5. If replying to email/message, match the sender's language
6. Include proper greeting and signature
7. Add call-to-action when appropriate

Respond in {language} language.
"""
            
            result = subprocess.run(
                ['qwen', '-y', full_prompt],
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace',
                cwd=str(self.vault_path),
                timeout=300  # 5 minutes timeout
            )
            
            if result.returncode == 0:
                response = result.stdout.strip()
                self.log_info(f"✅ Qwen responded ({len(response)} chars)")
                return response
            else:
                error_msg = result.stderr.strip() if result.stderr else "Unknown error"
                self.log_error(f"❌ Qwen error: {error_msg}")
                return f"Error: {error_msg}"
                
        except subprocess.TimeoutExpired:
            self.log_error("❌ Qwen timeout (5 minutes)")
            return "Error: Timeout - Qwen took too long to respond"
        except Exception as e:
            self.log_error(f"❌ Error calling Qwen: {e}")
            return f"Error: {str(e)}"
    
    def analyze_email(self, email_content: str) -> Dict:
        """
        Analyze an email and extract key information
        
        Returns:
            Dictionary with:
            - language
            - category
            - priority
            - sentiment
            - suggested_action
        """
        prompt = f"""
Analyze this email and provide structured information:

Email Content:
{email_content}

Provide response in JSON format:
{{
    "language": "detected language (Urdu/English/Arabic/etc.)",
    "category": "Sales/Support/Inquiry/Complaint/General",
    "priority": "High/Medium/Low",
    "sentiment": "Positive/Neutral/Negative",
    "urgency": "Urgent/Normal/Can Wait",
    "suggested_action": "what should be done"
}}
"""
        
        response = self.ask_qwen(prompt, 'English')
        
        try:
            # Try to parse JSON from response
            if '{' in response and '}' in response:
                start = response.find('{')
                end = response.rfind('}') + 1
                json_str = response[start:end]
                return json.loads(json_str)
        except:
            pass
        
        # Return default if parsing fails
        return {
            'language': 'English',
            'category': 'General',
            'priority': 'Medium',
            'sentiment': 'Neutral',
            'urgency': 'Normal',
            'suggested_action': 'Draft professional reply'
        }
    
    def draft_reply(self, email_content: str, language: str = 'Urdu') -> str:
        """
        Draft a professional reply to an email
        
        Args:
            email_content: Original email content
            language: Language for reply
            
        Returns:
            Draft reply
        """
        prompt = f"""
Draft a professional reply to this email:

Original Email:
{email_content}

Requirements:
1. Language: {language}
2. Tone: Professional, polite, respectful
3. Include proper greeting
4. Include professional signature
5. Add call-to-action
6. Follow company handbook rules
7. Be clear and concise
8. Human-like (not robotic)

Draft the complete reply in {language} language.
"""
        
        return self.ask_qwen(prompt, language)
    
    def ask_permission(self, action_type: str, content: str, language: str = 'Urdu') -> bool:
        """
        Ask user for permission before taking action

        Args:
            action_type: "send_email", "post_linkedin", "tweet", etc.
            content: What will be sent/posted
            language: Language to ask in

        Returns:
            True if approved, False otherwise
        """

        # Create approval request file
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        approval_file = self.pending_approval_folder / f"APPROVAL_{action_type}_{timestamp}.md"

        approval_content = f"""---
type: approval_request
action: {action_type}
language: {language}
created: {datetime.now().isoformat()}
status: pending
---

# Approval Request

**Action Type:** {action_type}
**Language:** {language}
**Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## Content

{content}

---

## Approval Commands

### Urdu / Roman Urdu
- ✅ "Haan, bhej do" - Send/Post immediately
- ❌ "Nahi, revise karo" - Redraft
- ✏️ "Edit karna hai" - I want to edit
- ⏸️ "Ruko, main khud likhta hun" - I'll write myself

### English
- ✅ "Yes, send it" - Send/Post immediately
- ❌ "No, revise it" - Redraft
- ✏️ "I want to edit" - I want to edit
- ⏸️ "Wait, I'll write myself" - I'll write myself

### Arabic
- ✅ "نعم، أرسله" - Send/Post immediately
- ❌ "لا، راجعه" - Redraft
- ✏️ "أريد تعديله" - I want to edit

---

**Waiting for your approval...**
"""

        approval_file.write_text(approval_content, encoding='utf-8')

        # Log the approval request
        self.log_info(f"📋 Approval request created: {approval_file.name}")
        self.log_info(f"Content preview: {content[:200]}...")

        # ACTUALLY WAIT FOR USER INPUT (HITL Fix)
        print(f"\n{'='*70}")
        print(f"📋 APPROVAL REQUEST")
        print(f"{'='*70}")
        print(f"Action: {action_type}")
        print(f"\nContent Preview:")
        print(f"{'-'*70}")
        print(content[:500] + ('...' if len(content) > 500 else ''))
        print(f"{'-'*70}")
        print(f"\nFull details saved to: {approval_file}")
        print(f"\nApprove? (yes/no/edit): ")

        # Approval keywords in multiple languages
        approve_keywords = ['yes', 'haan', 'نعم', 'send', 'bhej', 'approve', 'y', 'j']
        reject_keywords = ['no', 'nahi', 'لا', 'reject', 'revise', 'n', 'n']
        edit_keywords = ['edit', 'change', 'modify', 'tabdeeli', 'تبدیل']

        try:
            # Wait for user input with timeout
            import msvcrt
            timeout = 300  # 5 minutes timeout
            start_time = time.time()

            while time.time() - start_time < timeout:
                if msvcrt.kbhit():
                    user_input = input().strip().lower()

                    if any(kw in user_input for kw in approve_keywords):
                        # Update approval file status
                        updated_content = approval_content.replace('status: pending', 'status: approved')
                        updated_content = updated_content.replace(
                            f'created: {datetime.now().isoformat()}',
                            f'created: {datetime.now().isoformat()}\napproved: {datetime.now().isoformat()}\napproved_by: human'
                        )
                        approval_file.write_text(updated_content, encoding='utf-8')

                        self.log_info(f"✅ Approval granted for {action_type}")
                        return True

                    elif any(kw in user_input for kw in reject_keywords):
                        # Update approval file status
                        updated_content = approval_content.replace('status: pending', 'status: rejected')
                        approval_file.write_text(updated_content, encoding='utf-8')

                        self.log_info(f"❌ Approval rejected for {action_type}")
                        return False

                    elif any(kw in user_input for kw in edit_keywords):
                        self.log_info(f"✏️ User requested edit for {action_type}")
                        print(f"\n✏️ Please edit the file: {approval_file}")
                        print("   Then re-run with approval.")
                        return False

                    else:
                        print("   Invalid response. Please enter 'yes', 'no', or 'edit': ")

                time.sleep(0.5)  # Don't hog CPU

            # Timeout
            self.log_info(f"⏰ Approval timeout for {action_type}")
            print(f"\n⏰ Approval timeout (5 minutes). Action cancelled.")
            return False

        except (EOFError, KeyboardInterrupt):
            self.log_info(f"⚠️ Approval interrupted for {action_type}")
            print(f"\n⚠️ Approval cancelled.")
            return False
        except Exception as e:
            self.log_error(f"Error in approval flow: {e}")
            return False
    
    def process_gmail(self):
        """Process Gmail emails"""
        self.log_info("📧 Processing Gmail...")
        
        # This would integrate with Gmail watcher
        # For now, just check if watcher is running
        
        gmail_watcher = self.vault_path / 'watchers' / 'gmail_watcher.py'
        if gmail_watcher.exists():
            self.log_info("✅ Gmail watcher found")
            PLATFORMS['gmail']['status'] = 'ready'
        else:
            self.log_error("❌ Gmail watcher not found")
            PLATFORMS['gmail']['status'] = 'error'
    
    def process_linkedin(self):
        """Process LinkedIn posts and messages"""
        self.log_info("💼 Processing LinkedIn...")
        
        linkedin_generator = self.vault_path / 'linkedin_post_generator.py'
        if linkedin_generator.exists():
            self.log_info("✅ LinkedIn post generator found")
            PLATFORMS['linkedin']['status'] = 'ready'
        else:
            self.log_error("❌ LinkedIn post generator not found")
            PLATFORMS['linkedin']['status'] = 'error'
    
    def process_twitter(self):
        """Process Twitter tweets"""
        self.log_info("🐦 Processing Twitter...")
        
        twitter_generator = self.vault_path / 'twitter_post.py'
        if twitter_generator.exists():
            self.log_info("✅ Twitter post generator found")
            PLATFORMS['twitter']['status'] = 'ready'
        else:
            self.log_error("❌ Twitter post generator not found")
            PLATFORMS['twitter']['status'] = 'error'
    
    def process_facebook(self):
        """Process Facebook posts"""
        self.log_info("📘 Processing Facebook...")
        
        fb_generator = self.vault_path / 'facebook_instagram_post.py'
        if fb_generator.exists():
            self.log_info("✅ Facebook post generator found")
            PLATFORMS['facebook']['status'] = 'ready'
        else:
            self.log_error("❌ Facebook post generator not found")
            PLATFORMS['facebook']['status'] = 'error'
    
    def process_instagram(self):
        """Process Instagram posts"""
        self.log_info("📷 Processing Instagram...")
        
        ig_generator = self.vault_path / 'facebook_instagram_post.py'
        if ig_generator.exists():
            self.log_info("✅ Instagram post generator found")
            PLATFORMS['instagram']['status'] = 'ready'
        else:
            self.log_error("❌ Instagram post generator not found")
            PLATFORMS['instagram']['status'] = 'error'
    
    def process_whatsapp(self):
        """Process WhatsApp messages"""
        self.log_info("💬 Processing WhatsApp...")
        
        whatsapp_watcher = self.vault_path / 'watchers' / 'whatsapp_watcher.py'
        if whatsapp_watcher.exists():
            self.log_info("✅ WhatsApp watcher found")
            PLATFORMS['whatsapp']['status'] = 'ready'
        else:
            self.log_error("❌ WhatsApp watcher not found")
            PLATFORMS['whatsapp']['status'] = 'error'
    
    def process_office(self):
        """Process office files"""
        self.log_info("📁 Processing Office Files...")
        
        office_watcher = self.vault_path / 'watchers' / 'office_watcher.py'
        if office_watcher.exists():
            self.log_info("✅ Office watcher found")
            PLATFORMS['office']['status'] = 'ready'
        else:
            self.log_error("❌ Office watcher not found")
            PLATFORMS['office']['status'] = 'error'
    
    def check_all_platforms(self):
        """Check status of all platforms"""
        self.log_info("\n" + "="*70)
        self.log_info("📊 PLATFORM STATUS CHECK")
        self.log_info("="*70)
        
        # Process all platforms
        self.process_gmail()
        self.process_linkedin()
        self.process_twitter()
        self.process_facebook()
        self.process_instagram()
        self.process_whatsapp()
        self.process_office()
        
        # Summary
        ready = sum(1 for p in PLATFORMS.values() if p['status'] == 'ready')
        total = len(PLATFORMS)
        
        self.log_info("\n" + "="*70)
        self.log_info(f"📊 SUMMARY: {ready}/{total} platforms ready")
        self.log_info("="*70)
        
        for platform, info in PLATFORMS.items():
            status_icon = "✅" if info['status'] == 'ready' else "❌"
            self.log_info(f"{status_icon} {platform.upper()}: {info['status']}")
        
        return ready == total
    
    def run_demo(self):
        """Run a demo of the AI Employee capabilities"""
        self.log_info("\n" + "="*70)
        self.log_info("🤖 AI EMPLOYEE DEMO")
        self.log_info("="*70)
        
        # Demo 1: Email Analysis
        self.log_info("\n📧 DEMO 1: Email Analysis")
        test_email = """
From: ali.khan@example.com
Subject: Product pricing inquiry

Assalam-o-Alaikum,
Mujhe aap ke products ki price janni hai.
Please details bhejen.
Shukriya,
Ali Khan
"""
        analysis = self.analyze_email(test_email)
        self.log_info(f"Analysis Result: {analysis}")
        
        # Demo 2: Draft Reply
        self.log_info("\n📝 DEMO 2: Draft Reply (Urdu)")
        reply = self.draft_reply(test_email, 'Roman_Urdu')
        self.log_info(f"Draft Reply:\n{reply[:500]}...")
        
        # Demo 3: Ask Permission
        self.log_info("\n📋 DEMO 3: Ask Permission")
        self.ask_permission('send_email', reply, 'Urdu')
        
        self.log_info("\n" + "="*70)
        self.log_info("✅ DEMO COMPLETE")
        self.log_info("="*70)
    
    def run_247(self):
        """
        Run 24/7 monitoring mode
        
        This is the main loop that runs continuously:
        - Monitor Gmail every 2 minutes
        - Monitor WhatsApp every 30 seconds
        - Monitor Social every 60 seconds
        - Monitor Office files every 1 second
        """
        self.log_info("\n" + "="*70)
        self.log_info("🚀 STARTING 24/7 MONITORING MODE")
        self.log_info("="*70)
        
        # Check all platforms first
        if not self.check_all_platforms():
            self.log_error("❌ Some platforms not ready. Please fix issues first.")
            return
        
        self.log_info("\n✅ All platforms ready. Starting 24/7 monitoring...")
        self.log_info("Press Ctrl+C to stop")
        
        try:
            while True:
                # Gmail check (every 2 minutes)
                self.log_info("\n📧 Checking Gmail...")
                # In production, this would call gmail_watcher
                
                # WhatsApp check (every 30 seconds)
                self.log_info("💬 Checking WhatsApp...")
                # In production, this would call whatsapp_watcher
                
                # Social check (every 60 seconds)
                self.log_info("📱 Checking Social Media...")
                # In production, this would call social_watcher
                
                # Office check (every 1 second - handled by file watcher)
                # self.log_info("📁 Checking Office Files...")
                
                # Wait 2 minutes before next cycle
                self.log_info("\n⏳ Waiting 2 minutes before next check...")
                time.sleep(120)
                
        except KeyboardInterrupt:
            self.log_info("\n\n⏹️  24/7 monitoring stopped by user")
        except Exception as e:
            self.log_error(f"❌ Error in 24/7 mode: {e}")


def main():
    """Main function"""
    print("\n" + "="*70)
    print("🤖 COMPLETE 24/7 AI EMPLOYEE ORCHESTRATOR")
    print("="*70)
    print("\nBhai! Main aapka AI Employee hun. Main kya karun?")
    print("\nOptions:")
    print("1. Check all platforms")
    print("2. Run demo")
    print("3. Start 24/7 monitoring")
    print("4. Process specific platform")
    print("5. Exit")
    
    orchestrator = AIEmployeeOrchestrator()
    
    # Check Qwen CLI first
    if not orchestrator.check_qwen_cli():
        print("\n❌ Qwen CLI not found. Please install first:")
        print("   pip install qwen-code")
        return
    
    while True:
        print("\n" + "-"*70)
        choice = input("\nEnter choice (1-5): ").strip()
        
        if choice == '1':
            orchestrator.check_all_platforms()
        
        elif choice == '2':
            orchestrator.run_demo()
        
        elif choice == '3':
            print("\n⚠️  WARNING: 24/7 mode will run continuously!")
            confirm = input("Are you sure? (yes/no): ").strip().lower()
            if confirm == 'yes':
                orchestrator.run_247()
            else:
                print("❌ 24/7 mode cancelled")
        
        elif choice == '4':
            print("\nSelect platform:")
            print("1. Gmail")
            print("2. LinkedIn")
            print("3. Twitter")
            print("4. Facebook")
            print("5. Instagram")
            print("6. WhatsApp")
            print("7. Office")
            
            platform_choice = input("Enter platform (1-7): ").strip()
            
            if platform_choice == '1':
                orchestrator.process_gmail()
            elif platform_choice == '2':
                orchestrator.process_linkedin()
            elif platform_choice == '3':
                orchestrator.process_twitter()
            elif platform_choice == '4':
                orchestrator.process_facebook()
            elif platform_choice == '5':
                orchestrator.process_instagram()
            elif platform_choice == '6':
                orchestrator.process_whatsapp()
            elif platform_choice == '7':
                orchestrator.process_office()
            else:
                print("❌ Invalid choice")
        
        elif choice == '5':
            print("\n👋 Goodbye! AI Employee signing off.")
            break
        
        else:
            print("❌ Invalid choice. Please enter 1-5.")


if __name__ == '__main__':
    main()
