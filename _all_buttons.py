"""Все кнопки на странице Zvuk.com."""
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

options = Options()
options.add_argument("--headless=new")
options.add_argument("--no-sandbox")
options.add_argument("--disable-gpu")
options.binary_location = "/usr/bin/sberbrowser-browser-stable"
drv = webdriver.Remote(command_executor="http://localhost:4444", options=options)
drv.get("https://zvuk.com/")

# Close promo popup
for _ in range(3):
    btns = drv.find_elements(By.XPATH, '//button[contains(text(), "Закрыть")]')
    if btns:
        btns[0].click()
    else:
        break

# Все кнопки
btns = drv.find_elements(By.TAG_NAME, "button")
print(f"Total buttons: {len(btns)}")
for i, b in enumerate(btns):
    text = b.text.strip()
    cls = b.get_attribute("class")[:80]
    if text or cls:
        print(f"  [{i}] text={text!r} class={cls!r}")

drv.quit()
print("DONE")
