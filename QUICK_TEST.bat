@echo off
REM AI Employee - Quick Test
cd /d "C:\Users\CC\Documents\Obsidian Vault"
python -c "from datetime import datetime; print('Time:', datetime.now().strftime('%I:%M %p')); print('Date:', datetime.now().strftime('%d %B, %Y')); print('Test Complete!')"
pause
