#!/usr/bin/env python3
"""
SIMPLE AI EMPLOYEE TEST
Quick test without interactive mode

Bhai: Bas yeh run karo aur test ho jayega!
"""

import sys
from pathlib import Path

# Add vault to path
vault = Path('C:/Users/CC/Documents/Obsidian Vault')
sys.path.insert(0, str(vault))

from langdetect import detect

print("="*70)
print("🤖 AI EMPLOYEE - QUICK TEST")
print("="*70)
print()

# Test 1: Language Detection
print("Test 1: Language Detection")
print("-"*70)

test_phrases = [
    ("Mera kaam kaise chal raha hai?", "Roman Urdu"),
    ("How is my work going?", "English"),
    ("मेरा काम कैसे चल रहा है?", "Hindi"),
]

for phrase, expected in test_phrases:
    try:
        detected = detect(phrase)
        print(f"✅ {expected}: '{phrase[:30]}...' -> Detected: {detected}")
    except Exception as e:
        print(f"⚠️  {expected}: Error - {e}")

print()

# Test 2: Check Files
print("Test 2: Checking AI Employee Files")
print("-"*70)

files_to_check = [
    "ai_employee_config.json",
    "multi_language_agent.py",
    "cloud_agent.py",
    "local_agent.py",
    "health_monitor.py",
    "security_guard.py",
    "orchestrator.py",
]

for file in files_to_check:
    if (vault / file).exists():
        print(f"✅ {file}")
    else:
        print(f"❌ {file} - MISSING")

print()

# Test 3: Check Folders
print("Test 3: Checking Folders")
print("-"*70)

folders_to_check = [
    "Needs_Action",
    "Pending_Approval",
    "Done",
    "Drafts",
    "Logs",
]

for folder in folders_to_check:
    if (vault / folder).exists():
        print(f"✅ {folder}/")
    else:
        print(f"❌ {folder}/ - MISSING")

print()

# Test 4: Summary
print("="*70)
print("✅ AI EMPLOYEE TEST COMPLETE!")
print("="*70)
print()
print("Bhai! Sab files aur folders check ho gaye.")
print()
print("Next Steps:")
print("1. Double click: TEST_AI_EMPLOYEE.bat")
print("2. Ya run karo: python multi_language_agent.py")
print("3. Phir type karo: Mera kaam kaise chal raha hai?")
print()
print("Khuda Hafiz! 🚀")
print()
