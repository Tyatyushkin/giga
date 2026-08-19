"""Кликаем кнопку 'Войти' и ищем форму входа."""
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

options = Options()
options.add_argument("--headless=new")
options.add_argument("--no-sandbox")
options.add_argument("--disable-gpu")
options.binary_location = "/usr/bin/sberbrowser-browser-stable"
drv = webdriver.Remote(command_executor="http://localhost:4444", options=options)
drv.implicitly_wait(3)

drv.get("https://zvuk.com/")

# Нажимаем кнопку "Принять" если есть
for _ in range(3):
    btns = drv.find_elements(By.XPATH, "//button[contains(text(), 'Принять')]")
    if btns:
        btns[0].click()
    else:
        break

# Ждём и нажимаем кнопку входа
print("Waiting for auth button...")
try:
    auth_btn = WebDriverWait(drv, 5).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, ".NavBar_authButton__SGtCI"))
    )
    print("Found auth button, clicking...")
    auth_btn.click()
except Exception as e:
    print(f"Auth button not found: {e}")
    # Пробуем по тексту
    btns = drv.find_elements(By.XPATH, "//button[contains(text(), 'Войти')]")
    if btns:
        print("Found 'Войти' button, clicking...")
        btns[0].click()
    else:
        print("No 'Войти' button found either")

# Ждём загрузки формы
print("Waiting for login form...")
import time
time.sleep(5)

# Ищем input элементы
inputs = drv.find_elements(By.TAG_NAME, "input")
print(f"\nInput elements after click: {len(inputs)}")
for i, inp in enumerate(inputs):
    print(f"  [{i}] type={inp.get_attribute('type')!r} id={inp.get_attribute('id')!r} "
          f"placeholder={inp.get_attribute('placeholder')!r} name={inp.get_attribute('name')!r}")

# Ищем textarea
textareas = drv.find_elements(By.TAG_NAME, "textarea")
print(f"\nTextarea elements: {len(textareas)}")

# Ищем aria-label
aria = drv.find_elements(By.CSS_SELECTOR, "[aria-label]")
print(f"\nElements with aria-label: {len(aria)}")
for i, el in enumerate(aria[:20]):
    print(f"  [{i}] tag={el.tag_name} aria-label={el.get_attribute('aria-label')!r}")

# Сохраняем HTML
html = drv.page_source
with open("/tmp/zvuk_login.html", "w", encoding="utf-8") as f:
    f.write(html)
print(f"\nHTML saved to /tmp/zvuk_login.html ({len(html)} bytes)")

drv.quit()
