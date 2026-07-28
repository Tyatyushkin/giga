"""
conftest.py — глобальные фикстуры для Selenium-тестов J01

Основание: требования zvuk.md, zvuk-sample.md, _answers.md
"""

import pytest
import allure
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from api_stub import ZvukApiStub
import shutil

CHROME_PATH = shutil.which("google-chrome-stable") \
    or shutil.which("google-chrome") \
    or shutil.which("chromium") \
    or shutil.which("chrome") \
    or "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

BASE_URL: str = "https://zvuk.com/"


@pytest.fixture(scope="function")
def driver():
    options = Options()
    options.binary_location = CHROME_PATH
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_experimental_option("excludeSwitches", ["enable-logging"])
    options.set_capability("goog:loggingPrefs", {"browser": "ALL"})

    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(5)
    yield driver
    driver.quit()


@pytest.fixture(scope="function")
def base_url() -> str:
    return BASE_URL


@pytest.fixture(scope="function")
def api_client():
    """Фикстура для Selenium-тестов — эмуляция API «Звук».

    Возвращает предварительно авторизованный экземпляр ZvukApiStub.
    """
    from api_stub import ZvukApiStub
    client = ZvukApiStub()
    return client


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    if report.when == "call" and report.failed:
        if "driver" in item.funcargs:
            driver = item.funcargs["driver"]
            allure.attach(
                driver.get_screenshot_as_png(),
                name="screenshot_fail",
                attachment_type=allure.attachment_type.PNG,
            )