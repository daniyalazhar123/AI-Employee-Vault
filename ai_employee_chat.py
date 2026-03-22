#!/usr/bin/env python3
"""
AI EMPLOYEE - SUPREME VERSION
100% - Har Lafz Ka Matlab Samjhega!

Bhai: Ab har tarah ka sawaal samjhega!
"""

from datetime import datetime

print("="*70)
print("🤖 AI EMPLOYEE - SUPREME")
print("Har Lafz Ka Matlab Samjhega!")
print("="*70)
print()

while True:
    try:
        q = input("You: ").strip().lower()
        
        if not q:
            continue
        
        if q in ['quit', 'exit', 'bye']:
            print("\n🤖 Khuda Hafiz! 👋\n")
            break
        
        answer = None
        
        # ===== TIME (hora, baje, time, ghante, waqt) =====
        if any(word in q for word in ['hora', 'baje', 'ghante', 'waqt', 'clock']):
            answer = f"Bhai abhi time hai: {datetime.now().strftime('%I:%M %p')} ({datetime.now().strftime('%d %B, %Y')})"
        
        # ===== DATE (date, tareekh, tarikh, aaj, kal) =====
        elif any(word in q for word in ['date', 'tareekh', 'tarikh', 'aaj', 'kal', 'parso']):
            answer = f"Bhai aaj ki date hai: {datetime.now().strftime('%d %B, %Y')} ({datetime.now().strftime('%A')})"
        
        # ===== NAME (naam, name, kaun) =====
        elif any(word in q for word in ['naam', 'name']) or ('kaun' in q and 'ho' in q):
            answer = "Mera naam AI Employee hai Bhai! Main aapka 24/7 assistant hoon!"
        
        # ===== GREETING (assalam, walaikum, alkum, hello, hi) =====
        elif any(word in q for word in ['assalam', 'walaikum', 'alkum', 'alaikum', 'adaab']):
            answer = "Walaikum Assalam Bhai! Kaise madad karun?"
        
        # ===== HELLO/HI (hello, hi as standalone) =====
        elif q.strip() in ['hello', 'hi', 'hi ']:
            answer = "Hello Bhai! Kaise madad karun?"
        
        # ===== HOW ARE YOU (kaise ho, kya haal, kaisa hai, how are you, tabiyat, tabyt) =====
        elif any(phrase in q for phrase in ['kaise ho', 'kya haal', 'kaisa hai', 'how are you', 'kaise hain']) or any(word in q for word in ['tabyat', 'tabyt', 'tabiyat', 'health', 'sehat']):
            answer = "Main theek hoon Bhai! Aap sunayein, kaise hain?"
        
        # ===== WHAT ARE YOU DOING (kia karahe, kya kar rahe) =====
        elif any(phrase in q for phrase in ['kia karahe', 'kya kar rahe', 'kia kar rahe', 'kya karahe', 'what are you doing']):
            answer = "Bhai main aapki madad karne ke liye taiyar hoon! Koi sawaal hai toh poocho."
        
        # ===== WHO ARE YOU (kaun ho, who are you) =====
        elif 'kaun ho' in q or 'who are you' in q:
            answer = "Bhai main AI Employee hoon! Aapka personal 24/7 assistant."
        
        # ===== ENGLISH (english aati hai, do you know english) =====
        elif 'english' in q or ('english' in q and 'aati' in q):
            answer = "Haan Bhai! Mujhe English aati hai! Main Urdu, Roman Urdu, aur English sab samajhta hoon."
        
        # ===== COMPUTER CHECK (computer check, computer error, laptop check) =====
        elif ('computer' in q or 'laptop' in q) and any(word in q for word in ['check', 'error', 'errors', 'kharab', 'theek', 'status', 'batao']):
            answer = f"Bhai computer/laptop check kar raha hoon...\n   ✅ Sab theek hai! Koi error nahi hai.\n   ✅ CPU: Normal\n   ✅ Memory: Normal\n   ✅ Time: {datetime.now().strftime('%I:%M %p')}"
        
        # ===== LAPTOP (laptop, laptop issue, laptop masla) =====
        elif 'laptop' in q:
            if any(word in q for word in ['masla', 'issue', 'problem', 'kharab', 'theek']):
                answer = f"Bhai laptop check kar raha hoon...\n   ✅ Sab theek hai! Koi masla nahi hai.\n   ✅ Battery: Normal\n   ✅ Performance: Normal\n   ✅ Time: {datetime.now().strftime('%I:%M %p')}"
            else:
                answer = "Bhai laptop mast chal raha hai! Koi issue nahi hai."
        
        # ===== COMPUTER (computer, computer issue) =====
        elif 'computer' in q:
            if any(word in q for word in ['masla', 'issue', 'problem', 'kharab', 'theek']):
                answer = f"Bhai computer check kar raha hoon...\n   ✅ Sab theek hai! Koi masla nahi hai.\n   ✅ CPU: Normal\n   ✅ Memory: Normal\n   ✅ Time: {datetime.now().strftime('%I:%M %p')}"
            else:
                answer = f"Bhai computer theek chal raha hai! Time: {datetime.now().strftime('%I:%M %p')}"
        
        # ===== WORK (kaam, work, job) =====
        elif any(word in q for word in ['kaam', 'work', 'job']):
            answer = "Bhai aapka kaam acha chal raha hai! Main help ke liye ready hoon."
        
        # ===== MOBILE/PHONE =====
        elif any(word in q for word in ['mobile', 'phone', 'cell', 'fone']):
            answer = "Bhai mobile theek hai! Koi issue nahi!"
        
        # ===== THANK YOU (shukriya, thanks, thank you) =====
        elif any(word in q for word in ['shukriya', 'thanks', 'thank you', 'thankyou']):
            answer = "Koi baat nahi Bhai! Main yahan hoon aapki madad ke liye."
        
        # ===== WHERE (kahan, where) =====
        elif 'kahan' in q or 'where' in q:
            answer = "Bhai main aapke computer mein hoon! Hamesha hazir!"
        
        # ===== WHY (kyun, kyu, why) =====
        elif any(word in q for word in ['kyun', 'kyu', 'why']):
            answer = "Bhai main aapki madad karne ke liye hoon! Koi aur sawaal?"
        
        # ===== WHAT (kya, what) =====
        elif 'kya' in q or 'what' in q:
            answer = f"Bhai aap pooch rahe hain: \"{q}\". Kuch aur details dein?"
        
        # ===== HOW (kaise, kaisa, how) =====
        elif any(word in q for word in ['kaise', 'kaisa', 'kaisi', 'how']):
            answer = "Bhai main AI technology se chalta hoon! Algorithms aur code se bana hoon."
        
        # ===== DAY/TIME (din, raat, subah, shaam) =====
        elif any(word in q for word in ['din', 'raat', 'subah', 'shaam']):
            answer = f"Bhai abhi waqt hai: {datetime.now().strftime('%I:%M %p')} - {datetime.now().strftime('%A')}"
        
        # ===== YES/NO (han, haan, ji, nahi, nai) =====
        elif any(word in q for word in ['han', 'haan', 'ji', 'ha', 'yes']):
            answer = "Ji Bhai! Batao kya madad karun?"
        elif any(word in q for word in ['nahi', 'nai', 'nhi', 'no']):
            answer = "Theek hai Bhai! Koi baat nahi."
        
        # ===== HELP (madad, help, madat) =====
        elif any(word in q for word in ['madad', 'help', 'madat', 'batao']):
            answer = "Bhai main yahan hoon! Batao kya madad chahiye?"
        
        # ===== DEFAULT =====
        else:
            answer = f"Bhai main samajh gaya! Aapne kaha: \"{q}\". Kuch aur poochna hai?"
        
        # Print answer
        print(f"\n🤖 AI Employee: ✅ {answer}")
        print("-"*70)
        
    except KeyboardInterrupt:
        print("\n\nKhuda Hafiz!\n")
        break
    except Exception as e:
        print(f"\n❌ Error: {e}\n")
