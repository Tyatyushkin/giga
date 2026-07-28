"""
conftest.py — глобальные фикстуры для Selenium-тестов J02 (офлайн)

Основание: требования zvuk.md, zvuk-sample.md, _answers.md
"""

import pytest
import allure
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

BASE_URL: str = "https://zvuk.com/"


@pytest.fixture(scope="function")
def driver():
    """
    Фикстура Headless Chrome для офлайн-тестов.

    Использует webdriver-manager для автоматической установки ChromeDriver.
    Окно 1920x1080 для детерминированного рендеринга.
    """
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.set_capability("goog:loggingPrefs", {"browser": "ALL"})

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )
    driver.implicitly_wait(5)
    yield driver
    driver.quit()


@pytest.fixture(scope="function")
def base_url() -> str:
    return BASE_URL


# --- Хук для скриншота на FAIL ---
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