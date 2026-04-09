import time
import random
import string
import threading
from concurrent.futures import ThreadPoolExecutor
from seleniumbase import SB
from faker import Faker

file_lock = threading.Lock()

def generate_password(length=14):
    chars = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(random.choice(chars) for _ in range(length))

def register_account(task_id):
    # Плавный запуск (разница между стартами окон)
    time.sleep(task_id * 2.5)
    
    fake = Faker('en_US')
    username = f"{fake.first_name().lower()}{fake.last_name().lower()}{random.randint(100, 9999)}"
    password = generate_password()
    email = f"{username}@elektrine.com"
    
    print(f"[Поток {task_id}] 🚀 Старт: {email}")

    try:
        # На Linux сервере ОБЯЗАТЕЛЬНО используем xvfb=True 
        # Это создает виртуальный монитор, без которого Cloudflare забанит headless-браузер
        with SB(uc=True, xvfb=True) as sb:
            sb.open("https://z.org/register")
            sb.sleep(4)
            
            sb.type('#register-form_username', username)
            sb.type('#register-form_password', password)
            sb.type('#register-form_password_confirmation', password)
            sb.js_click('input[name="user[agree_to_terms]"]')
            
            print(f"[Поток {task_id}] ⏳ Жду Cloudflare...")
            
            for _ in range(15):
                try:
                    if sb.is_element_present('input[name="cf-turnstile-response"]'):
                        cf_token = sb.get_attribute('input[name="cf-turnstile-response"]', 'value')
                        if cf_token and len(cf_token) > 10:
                            print(f"[Поток {task_id}] ✅ Cloudflare пройден!")
                            break
                except: pass
                sb.sleep(2)
            
            sb.click('button:contains("Create account")')
            print(f"[Поток {task_id}] 🔄 Отправлено, жду 'Skip Setup'...")
            
            try:
                sb.wait_for_element('button[phx-click="skip_onboarding"]', timeout=20)
                sb.click('button[phx-click="skip_onboarding"]')
                print(f"[Поток {task_id}] ⏭️ 'Skip Setup' нажат.")
            except:
                pass
            
            sb.sleep(3)
            
            with file_lock:
                with open("accounts.txt", "a", encoding="utf-8") as f:
                    f.write(f"{email}:{password}\n")
                    
            print(f"[Поток {task_id}] 💾 СОХРАНЕН: {email}")
            return True
            
    except Exception as e:
        error_msg = str(e).splitlines()[0] if str(e) else "Неизвестная ошибка"
        print(f"[Поток {task_id}] ❌ Ошибка: {error_msg}")
        return False

def main():
    print("="*40)
    print("   Elektrine CLI AutoReger (Debian)   ")
    print("="*40)
    
    try:
        total_accounts = int(input("👉 Сколько аккаунтов создать?: "))
        threads_count = int(input("👉 Сколько потоков (1-5)?: "))
    except ValueError:
        print("❌ Ошибка: Вводите только цифры!")
        return

    print(f"\n🏁 Поехали! Потоков: {threads_count}, Аккаунтов: {total_accounts}\n")

    with ThreadPoolExecutor(max_workers=threads_count) as executor:
        futures = [executor.submit(register_account, i+1) for i in range(total_accounts)]
        for future in futures:
            future.result()

    print("\n🎉 Все готово! Результаты в файле accounts.txt")

if __name__ == "__main__":
    main()
