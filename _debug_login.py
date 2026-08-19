"""Быстрая отладка формы входа."""
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

options = Options()
options.add_argument("--headless=new")
options.add_argument("--no-sandbox")
options.add_argument("--disable-gpu")
options.binary_location = "/usr/bin/sberbrowser-browser-stable"
drv = webdriver.Remote(command_executor="http://localhost:4444", options=options)

drv.get("https://zvuk.com/")

# Закрываем cookie
cookie_btns = drv.find_elements(By.XPATH, "//button[contains(text(), 'Принять')]")
for b in cookie_btns[:1]:
    b.click()

# Закрываем промо-попап
try:
    WebDriverWait(drv, 2).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, ".Standalone_closeCross__PonXe"))
    ).click()
except:
    pass

# JS-клик по кнопке 'Войти'
js = """
function findButton(root, text) {
    let buttons = root.querySelectorAll('button');
    for (let btn of buttons) {
        if (btn.textContent.trim() === text) { btn.click(); return true; }
        if (btn.shadowRoot && findButton(btn.shadowRoot, text)) return true;
    }
    return false;
}
return findButton(document, 'Войти');
"""
result = drv.execute_script(js)
print(f"Auth button clicked: {result}")
print(f"Current URL: {drv.current_url}")

# Ждём форму
try:
    phone = WebDriverWait(drv, 5).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, 'input[name="phone"]'))
    )
    print(f"Phone input found: placeholder={phone.get_attribute('placeholder')}")
except Exception as e:
    print(f"Phone input NOT found: {e}")

# Ищем все inputs
inputs = drv.find_elements(By.TAG_NAME, "input")
print(f"Total inputs: {len(inputs)}")
for i, inp in enumerate(inputs[:5]):
    print(f"  [{i}] type={inp.get_attribute('type')!r} name={inp.get_attribute('name')!r}")

drv.save_screenshot("/tmp/browser_test_screenshots/debug_quick.png")
drv.quit()
print("DONE")
