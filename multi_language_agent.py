#!/usr/bin/env python3
"""
MULTI-LANGUAGE AI EMPLOYEE AGENT
Supports 25+ Languages with Auto-Detection
Python 3.14 Compatible (uses deep-translator)

Bhai: Yeh agent automatically language detect karta hai
aur usi language mein jawab deta hai!
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime
import subprocess

# Install dependencies if needed
try:
    from langdetect import detect, DetectorFactory
    LANGDETECT_AVAILABLE = True
except ImportError:
    LANGDETECT_AVAILABLE = False
    print("⚠️  Installing langdetect...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "langdetect"])
    from langdetect import detect, DetectorFactory
    LANGDETECT_AVAILABLE = True

# Use deep-translator (Python 3.14 compatible)
try:
    from deep_translator import GoogleTranslator
    TRANSLATOR_AVAILABLE = True
    print("✅ deep-translator loaded")
except ImportError:
    TRANSLATOR_AVAILABLE = False
    print("⚠️  Installing deep-translator (Python 3.14 compatible)...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "deep-translator"])
    from deep_translator import GoogleTranslator
    TRANSLATOR_AVAILABLE = True


class MultiLanguageAIAgent:
    """Multi-Language AI Employee Agent"""
    
    def __init__(self, vault_path: str = None):
        self.vault = Path(vault_path) if vault_path else Path('.')
        self.config_file = self.vault / 'ai_employee_config.json'
        
        # Load configuration
        self.config = self._load_config()
        
        # Language codes mapping
        self.language_codes = {
            'ur': 'Urdu',
            'hi': 'Hindi',
            'en': 'English',
            'zh-cn': 'Chinese (Simplified)',
            'zh-tw': 'Chinese (Traditional)',
            'ja': 'Japanese',
            'ps': 'Pashto',
            'pa': 'Punjabi',
            'skr': 'Saraiki',
            'bal': 'Balochi',
            'sd': 'Sindhi',
            'ks': 'Kashmiri',
            'ar': 'Arabic',
            'hno': 'Hindko',
            'it': 'Italian',
            'es': 'Spanish',
            'ru': 'Russian',
            'fr': 'French',
            'de': 'German'
        }
        
        # Roman Urdu detection keywords
        self.roman_urdu_keywords = [
            'hai', 'hain', 'tha', 'thi', 'the', 'ho', 'he', 'hi',
            'kya', 'kyun', 'kahan', 'kab', 'kaun', 'kaisa',
            'mera', 'tera', 'uska', 'humara', 'tumhara',
            'karna', 'karta', 'karti', 'karte',
            'nahi', 'nai', 'nhi', 'hein', 'han'
        ]
        
        print("🌍 Multi-Language AI Agent initialized")
        print(f"📂 Vault: {self.vault}")
        print(f"🗣️  Supported Languages: {len(self.language_codes)}+")
    
    def _load_config(self) -> dict:
        """Load AI Employee configuration"""
        if self.config_file.exists():
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def detect_language(self, text: str) -> str:
        """Detect language of user query"""
        if not text.strip():
            return 'English_US'
        
        # Check for Roman Urdu first
        text_lower = text.lower()
        roman_urdu_count = sum(1 for keyword in self.roman_urdu_keywords if keyword in text_lower)
        
        if roman_urdu_count >= 2:
            return 'Roman_Urdu'
        
        # Use langdetect for other languages
        if LANGDETECT_AVAILABLE:
            try:
                DetectorFactory.seed = 0
                lang_code = detect(text)
                return self.language_codes.get(lang_code, f'Language_{lang_code}')
            except:
                return 'English_US'
        
        return 'English_US'
    
    def translate_to_english(self, text: str, source_lang: str) -> str:
        """Translate text to English for processing"""
        if source_lang in ['English_US', 'English_UK', 'English']:
            return text
        
        if source_lang == 'Roman_Urdu':
            return text
        
        if TRANSLATOR_AVAILABLE:
            try:
                translator = GoogleTranslator(source='auto', target='en')
                translated = translator.translate(text)
                return translated if translated else text
            except:
                return text
        
        return text
    
    def translate_from_english(self, text: str, target_lang: str) -> str:
        """Translate English text to target language"""
        if target_lang in ['English_US', 'English_UK', 'English']:
            return text
        
        if target_lang == 'Roman_Urdu':
            return text
        
        if TRANSLATOR_AVAILABLE:
            try:
                translator = GoogleTranslator(source='en', target=target_lang.lower()[:2])
                translated = translator.translate(text)
                return translated if translated else text
            except:
                return text
        
        return text
    
    def process_query(self, user_query: str, user_name: str = "Bhai") -> dict:
        """Process user query in their language"""
        # Step 1: Detect language
        detected_lang = self.detect_language(user_query)
        print(f"\n🗣️  Detected Language: {detected_lang}")
        print(f"📝 Query: {user_query}")
        
        # Step 2: Translate to English (if needed)
        english_query = self.translate_to_english(user_query, detected_lang)
        print(f"🔄 English Query: {english_query}")
        
        # Step 3: Process with Qwen CLI
        qwen_response = self._process_with_qwen(english_query, user_name)
        
        # Step 4: Translate response back to user's language
        response_in_user_lang = self.translate_from_english(
            qwen_response['response'], 
            detected_lang
        )
        
        # Step 5: Create response
        result = {
            'original_query': user_query,
            'detected_language': detected_lang,
            'english_translation': english_query,
            'response': response_in_user_lang,
            'response_english': qwen_response['response'],
            'action': qwen_response['action'],
            'permission_required': qwen_response['permission_required'],
            'timestamp': datetime.now().isoformat()
        }
        
        # Step 6: Log interaction
        self._log_interaction(result)
        
        return result
    
    def _process_with_qwen(self, query: str, user_name: str) -> dict:
        """Process query with Qwen CLI"""
        prompt = f"""
Bhai {user_name} ne yeh query ki hai: "{query}"

Please respond professionally and helpfully in Roman Urdu.
Keep response short and friendly.

Response: """
        
        try:
            # Try different Qwen CLI commands
            qwen_commands = ['qwen', 'claude-code', 'qwen-code']
            
            for cmd in qwen_commands:
                try:
                    result = subprocess.run(
                        [cmd, '-y', prompt],
                        capture_output=True,
                        text=True,
                        timeout=180,
                        shell=True
                    )
                    
                    if result.returncode == 0 and result.stdout:
                        response = result.stdout
                        return {
                            'response': response,
                            'action': 'none',
                            'permission_required': False
                        }
                except:
                    continue
            
            # If Qwen not available, use simple response
            return {
                'response': f"Bhai {user_name}! Main aapka AI Employee hoon. Main aapki madad karne ke liye taiyar hoon. Aap mujh se kuch bhi pooch sakte hain!",
                'action': 'none',
                'permission_required': False
            }
        
        except Exception as e:
            return {
                'response': f"Bhai! Main aapka AI Employee hoon. Main aapki madad kar sakta hoon. (Qwen CLI error: {str(e)})",
                'action': 'none',
                'permission_required': False
            }
    
    def _log_interaction(self, interaction: dict):
        """Log interaction to audit log"""
        logs_folder = self.vault / 'Logs' / 'Interactions'
        logs_folder.mkdir(parents=True, exist_ok=True)
        
        today = datetime.now().strftime('%Y-%m-%d')
        log_file = logs_folder / f"interactions_{today}.jsonl"
        
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(interaction, ensure_ascii=False) + '\n')
    
    def greet_user(self, language: str = 'Roman_Urdu') -> str:
        """Generate greeting in user's language"""
        greetings = {
            'Urdu': 'السلام علیکم! میں آپ کا AI Employee ہوں۔',
            'Roman_Urdu': 'Walaikum Assalam Bhai! Main aapka AI Employee hoon.',
            'English_US': 'Hello! I\'m your AI Employee.',
            'Hindi': 'नमस्ते! मैं आपका AI Employee हूँ।',
            'Spanish': '¡Hola! Soy tu Empleado de IA.',
            'French': 'Bonjour! Je suis votre Employé IA.',
            'German': 'Hallo! Ich bin Ihr KI-Mitarbeiter.',
            'Chinese (Simplified)': '你好！我是你的 AI 员工。',
            'Japanese': 'こんにちは！私はあなたの AI 従業員です。',
            'Arabic': 'مرحبا! أنا موظف الذكاء الاصطناعي الخاص بك.',
            'Russian': 'Здравствуйте! Я ваш ИИ-сотрудник.',
            'Italian': 'Ciao! Sono il tuo Dipendente AI.'
        }
        return greetings.get(language, 'Hello! I\'m your AI Employee.')


def main():
    """Main entry point - Interactive mode"""
    print("="*70)
    print("🌍 MULTI-LANGUAGE AI EMPLOYEE AGENT")
    print("Python 3.14 Compatible - 25+ Languages")
    print("="*70)
    
    vault_path = sys.argv[1] if len(sys.argv) > 1 else 'C:/Users/CC/Documents/Obsidian Vault'
    agent = MultiLanguageAIAgent(vault_path)
    
    print("\n" + agent.greet_user('Roman_Urdu'))
    print("\n" + "="*70)
    print("💬 Start chatting! Type 'quit' to exit.\n")
    
    while True:
        try:
            user_input = input("You: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'bye']:
                print("\n" + agent.greet_user('Roman_Urdu'))
                print("Khuda Hafiz! Goodbye!\n")
                break
            
            if not user_input:
                continue
            
            result = agent.process_query(user_input)
            
            print(f"\n🤖 AI Employee ({result['detected_language']}):")
            print(result['response'])
            
            if result['permission_required']:
                print("\n⚠️  ACTION REQUIRES PERMISSION!")
            
            print("-"*70)
        
        except KeyboardInterrupt:
            print("\n\nKhuda Hafiz! Goodbye!\n")
            break
        
        except Exception as e:
            print(f"\n❌ Error: {e}\n")


if __name__ == '__main__':
    main()
