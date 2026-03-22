@echo off
echo ============================================
echo 🤖 AI EMPLOYEE - TEST RESPONSES
echo ============================================
echo.

cd /d "C:\Users\CC\Documents\Obsidian Vault"

python -c "
from ai_employee_chat import WorkingAIAgent
agent = WorkingAIAgent()

tests = [
    ('kai hora hai', 'Time'),
    ('ap ka naam kya hai', 'Name'),
    ('assalam o alaikum', 'Greeting'),
    ('aaj ki date kya hai', 'Date'),
    ('computer kaisa hai', 'Computer'),
    ('laptop kaisa hai', 'Laptop'),
]

print('Testing Response Matching:')
print('='*70)
for query, expected in tests:
    response = agent.get_response(query)
    print(f'Q: {query}')
    print(f'A: {response}')
    print('-'*70)

print()
print('✅ All tests complete!')
print()
print('Now starting chat...')
print()
"

echo Starting Chat Mode...
python ai_employee_chat.py

pause
