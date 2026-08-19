"""Отладка: какие варианты входа появляются."""
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
drv.execute_script(js)
import time
time.sleep(3)

# Сохраняем скриншот
drv.save_screenshot("/tmp/browser_test_screenshots/debug_login_variants.png")
print("Screenshot saved to /tmp/browser_test_screenshots/debug_login_variants.png")

# Ищем все элементы на странице
print("\n=== Все видимые элементы ===")
all_elements = drv.find_elements(By.XPATH, "//*[not(self::script) and not(self::style) and not(self::link)]")
for el in all_elements[:50]:
    tag = el.tag_name
    text = el.text.strip()[:50]
    attrs = {}
    for attr in ['class', 'id', 'name', 'type', 'placeholder', 'data-testid']:
        val = el.get_attribute(attr)
        if val:
            attrs[attr] = val[:80]
    if text or attrs:
        print(f"  {tag} text={text!r} attrs={attrs}")

# Ищем input элементы
print("\n=== Input элементы ===")
inputs = drv.find_elements(By.TAG_NAME, "input")
for i, inp in enumerate(inputs):
    print(f"  [{i}] type={inp.get_attribute('type')!r} name={inp.get_attribute('name')!r} placeholder={inp.get_attribute('placeholder')!r}")

# Ищем кнопки
print("\n=== Кнопки ===")
buttons = drv.find_elements(By.TAG_NAME, "button")
for i, btn in enumerate(buttons):
    text = btn.text.strip()
    cls = btn.get_attribute('class')[:60]
    if text or cls:
        print(f"  [{i}] text={text!r} class={cls!r}")

# Сохраняем HTML
html = drv.find_element(By.TAG_NAME, "body").get_attribute("innerHTML")
with open("/tmp/browser_test_screenshots/login_html.txt", "w") as f:
    f.write(html[:5000])
print(f"\nHTML saved to /tmp/browser_test_screenshots/login_html.txt ({len(html)} chars)")

drv.quit()
print("DONE")
