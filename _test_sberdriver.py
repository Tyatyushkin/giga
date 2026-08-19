"""Проверка создания сессии с sberdriver."""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import json

# Способ 1: как в curl пользователя
caps = DesiredCapabilities.CHROME.copy()
caps.update({
    "goog:chromeOptions": {
        "binary": "/usr/bin/sberbrowser-browser-stable",
        "args": ["--headless=new", "--no-sandbox", "--disable-gpu", "--window-size=1920,1080"],
    }
})
print("Способ 1: DesiredCapabilities + binary")
print(f"Capabilities: {json.dumps(caps, indent=2)}")
try:
    drv = webdriver.Remote(
        command_executor="http://localhost:4444",
        capabilities=caps,
    )
    print(f"  SUCCESS: session_id={drv.session_id}")
    drv.quit()
except Exception as e:
    print(f"  FAILED: {e}")

# Способ 2: через options + set_capability
print()
print("Способ 2: Options + set_capability(binary)")
options = Options()
options.add_argument("--headless=new")
options.add_argument("--no-sandbox")
options.add_argument("--disable-gpu")
options.add_argument("--window-size=1920,1080")
options.binary_location = "/usr/bin/sberbrowser-browser-stable"
try:
    drv = webdriver.Remote(
        command_executor="http://localhost:4444",
        options=options,
    )
    print(f"  SUCCESS: session_id={drv.session_id}")
    drv.quit()
except Exception as e:
    print(f"  FAILED: {e}")
