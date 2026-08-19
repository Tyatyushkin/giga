"""Поиск реальных селекторов через XPath по тексту."""
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

# 1. Кнопка закрытия промо-попапа
print("=" * 60)
print("PROMO CLOSE BUTTON:")
print("=" * 60)
close_texts = ["Закрыть", "close", "×", "✕", "✖", "×", "✗"]
for kw in close_texts:
    try:
        els = drv.find_elements(By.XPATH, f"//button[contains(text(), '{kw}')]")
        if els:
            for el in els:
                print(f"  text='{kw}' | tag={el.tag_name} class={el.get_attribute('class')[:80]!r}")
    except:
        pass

# 2. Кнопка "Войти"
print()
print("AUTH / LOGIN BUTTON:")
print("=" * 60)
btns = drv.find_elements(By.XPATH, "//button[contains(text(), 'Войти')]")
for i, btn in enumerate(btns):
    print(f"  [{i}] text={btn.text!r} class={btn.get_attribute('class')[:100]!r}")

els = drv.find_elements(By.XPATH, "//*[contains(text(), 'Войти')]")
for el in els[:3]:
    print(f"  text='Войти' | tag={el.tag_name} class={el.get_attribute('class')[:80]!r}")

# 3. Промо попап (закрытие)
print()
print("PROMO POPUP CLOSE:")
print("=" * 60)
close_btns = drv.find_elements(By.XPATH, "//button[contains(text(), 'Закрыть')]")
for i, btn in enumerate(close_btns):
    print(f"  [{i}] text={btn.text!r} class={btn.get_attribute('class')[:100]!r}")

drv.quit()
