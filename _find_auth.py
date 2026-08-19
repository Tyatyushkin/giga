"""Поиск кнопки 'Войти' по тексту."""
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

options = Options()
options.add_argument("--headless=new")
options.add_argument("--no-sandbox")
options.add_argument("--disable-gpu")
options.binary_location = "/usr/bin/sberbrowser-browser-stable"
drv = webdriver.Remote(command_executor="http://localhost:4444", options=options)
drv.implicitly_wait(3)

drv.get("https://zvuk.com/")

# Кнопка "Принять"
for _ in range(3):
    btns = drv.find_elements(By.XPATH, "//button[contains(text(), 'Принять')]")
    if btns:
        btns[0].click()
    else:
        break

# Кнопка "Войти"
btns = drv.find_elements(By.XPATH, "//button[contains(text(), 'Войти')]")
print(f"Found 'Войти' buttons: {len(btns)}")
for i, btn in enumerate(btns):
    print(f"  [{i}] text={btn.text!r} class={btn.get_attribute('class')[:100]!r}")

# Элемент с текстом "Войти"
els = drv.find_elements(By.XPATH, "//*[contains(text(), 'Войти')]")
print(f"\nElements with text 'Войти': {len(els)}")
for i, el in enumerate(els[:5]):
    print(f"  [{i}] tag={el.tag_name} text={el.text[:50]!r} class={el.get_attribute('class')[:80]!r}")

drv.quit()
