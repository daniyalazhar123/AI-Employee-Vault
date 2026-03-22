@echo off
echo ============================================
echo 🚀 AI EMPLOYEE - QUICK TEST
echo ============================================
echo.

cd /d "C:\Users\CC\Documents\Obsidian Vault"

echo Installing dependencies...
pip install deep-translator langdetect -q

echo.
echo Starting Multi-Language Agent...
echo.
echo ============================================
echo Type your message (Urdu, Roman Urdu, English)
echo Type 'quit' to exit
echo ============================================
echo.

python multi_language_agent.py

pause
