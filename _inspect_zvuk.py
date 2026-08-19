"""Исследование вёрстки Zvuk.com для подбора селекторов."""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

options = Options()
options.add_argument("--headless=new")
options.add_argument("--no-sandbox")
options.add_argument("--disable-gpu")
options.add_argument("--window-size=1920,1080")
drv = webdriver.Remote(command_executor="http://localhost:4444", options=options)
drv.implicitly_wait(5)

drv.get("https://zvuk.com/")

# 1. Посмотрим body text
body_text = drv.find_element(By.TAG_NAME, "body").text
print("=" * 80)
print("PAGE BODY TEXT (first 2000 chars):")
print("=" * 80)
print(body_text[:2000])
print()

# 2. Попробуем XPath по видимому тексту "телефон"
print("=" * 80)
print("TRYING XPATH BY VISIBLE TEXT:")
print("=" * 80)
for text_keyword in ["телефон", "Phone", "phone", "Введите номер"]:
    try:
        el = drv.find_element(By.XPATH, f"//*[contains(text(), '{text_keyword}')]")
        print(f"FOUND text='{text_keyword}' | tag={el.tag_name} | text={el.text[:200]}")
    except Exception as e:
        print(f"NOT FOUND text='{text_keyword}': {e}")

# 3. Попробуем все input-элементы на странице
print()
print("=" * 80)
print("ALL INPUT ELEMENTS:")
print("=" * 80)
inputs = drv.find_elements(By.TAG_NAME, "input")
for inp in inputs:
    attrs = {
        "type": inp.get_attribute("type"),
        "name": inp.get_attribute("name"),
        "id": inp.get_attribute("id"),
        "placeholder": inp.get_attribute("placeholder"),
        "class": inp.get_attribute("class")[:100] if inp.get_attribute("class") else "",
        "aria-label": inp.get_attribute("aria-label"),
    }
    print(f"  tag={inp.tag_name} | {attrs}")

# 4. Попробуем все textarea
print()
print("=" * 80)
print("ALL TEXTAREA ELEMENTS:")
print("=" * 80)
textareas = drv.find_elements(By.TAG_NAME, "textarea")
for ta in textareas:
    print(f"  tag={ta.tag_name} | id={ta.get_attribute('id')} | name={ta.get_attribute('name')}")

# 5. Поиск по классам, связанным с авторизацией
print()
print("=" * 80)
print("ELEMENTS WITH AUTH/LOGIN/PHONE IN CLASS:")
print("=" * 80)
for cls_kw in ["phone", "Phone", "Phone__", "phoneInput", "auth", "Auth", "login", "Login"]:
    try:
        els = drv.find_elements(By.CSS_SELECTOR, f"[class*={cls_kw}]")
        for el in els[:3]:
            print(f"  class*={cls_kw} | tag={el.tag_name} | text={el.text[:100]}")
    except:
        pass

# 6. Попробуем все кнопки
print()
print("=" * 80)
print("ALL BUTTONS:")
print("=" * 80)
buttons = drv.find_elements(By.TAG_NAME, "button")
for btn in buttons:
    attrs = {
        "type": btn.get_attribute("type"),
        "text": btn.text[:100],
        "class": btn.get_attribute("class")[:100] if btn.get_attribute("class") else "",
    }
    print(f"  {attrs}")

drv.quit()
