"""Тест подключения к sberdriver."""
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time

options = Options()
options.add_argument("--headless=new")
options.add_argument("--no-sandbox")
options.add_argument("--disable-gpu")
options.binary_location = "/usr/bin/sberbrowser-browser-stable"

print("Creating driver...")
drv = webdriver.Remote(command_executor="http://localhost:4444", options=options)
print(f"Driver created: {drv.capabilities}")

print("Opening google.com...")
drv.get("https://www.google.com")
print(f"Title: {drv.title}")

print("Closing...")
drv.quit()
print("DONE - all good")
