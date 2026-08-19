"""Извлечение селекторов из HTML страницы Zvuk."""
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

options = Options()
options.add_argument("--headless=new")
options.add_argument("--no-sandbox")
options.add_argument("--disable-gpu")
options.binary_location = "/usr/bin/sberbrowser-browser-stable"
drv = webdriver.Remote(command_executor="http://localhost:4444", options=options)
drv.implicitly_wait(5)

drv.get("https://zvuk.com/")

# Сохраняем HTML
html = drv.page_source
with open("/tmp/zvuk_home.html", "w", encoding="utf-8") as f:
    f.write(html)
print(f"HTML saved to /tmp/zvuk_home.html ({len(html)} bytes)")

# Ищем все input элементы
inputs = drv.find_elements(By.TAG_NAME, "input")
print(f"\nInput elements: {len(inputs)}")
for i, inp in enumerate(inputs):
    print(f"  [{i}] type={inp.get_attribute('type')!r} id={inp.get_attribute('id')!r} "
          f"name={inp.get_attribute('name')!r} placeholder={inp.get_attribute('placeholder')!r} "
          f"class={inp.get_attribute('class')[:80]!r}")

# Ищем все элементы с aria-label
aria_inputs = drv.find_elements(By.CSS_SELECTOR, "[aria-label]")
print(f"\nElements with aria-label: {len(aria_inputs)}")
for i, el in enumerate(aria_inputs[:20]):
    print(f"  [{i}] tag={el.tag_name} aria-label={el.get_attribute('aria-label')!r}")

drv.quit()
