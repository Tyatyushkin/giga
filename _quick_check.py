"""Быстрый поиск селекторов."""
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

# Find auth button
auth_btns = drv.find_elements(By.XPATH, '//button[contains(text(), "Войти")]')
print(f"Found {len(auth_btns)} auth buttons")
for b in auth_btns[:3]:
    print(f"  class={b.get_attribute('class')[:100]}")

# Find phone input
phone = drv.find_element(By.CSS_SELECTOR, 'input[name="phone"]')
print(f"Phone input found: placeholder={phone.get_attribute('placeholder')}")

drv.quit()
print("DONE")
