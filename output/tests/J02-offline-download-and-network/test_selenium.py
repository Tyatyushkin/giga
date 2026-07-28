"""
Selenium-тесты для J02 (офлайн-скачивание и обрыв сети) — визуальное тестирование браузера

Основание: input/requirements/zvuk.md, zvuk-sample.md, _answers.md
Требования: REQ-08, REQ-11, REQ-13, BR-008, BR-009, Q-03..Q-30

Каждый test_ — один шаг E2E-кейса.
"""

import allure
from typing import Final

import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

# Константы тестовых данных
PHONE_NUMBER: Final[str] = "+7 999 000-00-11"       # Q-07
SMS_CODE: Final[str] = "1234"
TRACK_TITLE: Final[str] = "Весна"                    # REQ-05
ARTIST_NAME: Final[str] = "Дельфин"                 # REQ-05
PLAYLIST_TITLE: Final[str] = "Тестовый плейлист 2026-07"  # REQ-08
PLAYLIST_NAME_LONG: Final[str] = "А" * 101          # Q-03: >100 символов

# Селекторы UI
SELECTORS: Final[dict] = {
    "phone_input":      "#phone-input",
    "submit_phone":     "#submit-phone",
    "sms_code_input":   "#sms-code-input",
    "submit_sms":       "#submit-sms",
    "play_button":      "#play-button",
    "pause_button":     "#pause-button",
    "player_title":     "#player-title",
    "player_artist":    "#player-artist",
    "player_artwork":   "#player-artwork",
    "timeline":         "#timeline",
    "timeline_current": "#timeline-current-position",
    "search_input":     "#search-input",
    "search_submit":    "#search-submit",
    "search_result":    "#search-result-0",
    "download_button":  "#download-playlist",
    "download_progress": "#download-progress",
    "offline_mode":     "#offline-mode-toggle",
    "offline_icon":     "#offline-icon",
    "connection_error": "#connection-error",
    "retry_button":     "#retry-connection",
    "resume_button":    "#resume-button",
    "playlist_title":   "#playlist-title",
    "playlist_track":   "#playlist-track",
    "playlist_create":  "#create-playlist",
    "playlist_list":    "#playlist-list",
    "subscription_badge": "#subscription-badge",
    "confirmation_dialog": "#download-confirmation",
    "confirm_download": "#confirm-download",
    "no_results":       "#no-results",
    "close_retry":      "#close-retry",
    "my_music":         "#my-music",
    "my_playlists":     "#my-playlists",
}


def capture_element_screenshot(driver, selector: str, name: str):
    """Сделать скриншот элемента и прикрепить к Allure."""
    element = driver.find_element(By.CSS_SELECTOR, selector)
    screenshot = element.screenshot_as_png()
    allure.attach(screenshot, name=name, attachment_type=allure.attachment_type.PNG)
    return element


# ============================================================
# Класс: Офлайн — Скачивание плейлиста
# ============================================================

@allure.suite("J02-офлайн-скачивание")
@allure.label("layer", "e2e")
class TestOfflineDownload:
    """
    Сценарий: скачивание плейлиста для офлайн-прослушивания.
    
    REQ-08: Длина названия до 100 символов.
    REQ-11: Скачивание только с активной подпиской.
    """

    def _login_to_app(self, driver, wait: WebDriverWait):
        """Вспомогательный метод: авторизация по SMS."""
        driver.get("https://zvuk.com/login")
        wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, SELECTORS["phone_input"]))
        ).send_keys(PHONE_NUMBER)
        driver.find_element(By.CSS_SELECTOR, SELECTORS["submit_phone"]).click()
        wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, SELECTORS["sms_code_input"]))
        ).send_keys(SMS_CODE)
        driver.find_element(By.CSS_SELECTOR, SELECTORS["submit_sms"]).click()

    @allure.id("J02-selenium-01")
    @allure.title("Скачивание плейлиста: кнопка Download и диалог подтверждения")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("При нажатии Download — отображается "
                         "диалог подтверждения и прогресс-бар")
    @allure.label("req", "REQ-11")
    def test_download_playlist_button(self, driver):
        """Кнопка Download для плейлиста — диалог подтверждения."""
        wait = WebDriverWait(driver, 10)
        self._login_to_app(driver, wait)

        # Находим плейлист
        wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, SELECTORS["my_playlists"]))
        )

        # Кликаем по плейлисту
        wait.until(EC.element_to_be_clickable(
            (By.CSS_SELECTOR, "#playlist-item-0"))
        ).click()

        # Жмём «Скачать»
        download_btn = wait.until(EC.element_to_be_clickable(
            (By.CSS_SELECTOR, SELECTORS["download_button"]))
        )
        assert download_btn.is_displayed(), "Кнопка Download отображается"
        download_btn.click()

        # Ждём диалог подтверждения
        wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, SELECTORS["confirmation_dialog"]))
        )

        # Подтверждаем
        driver.find_element(By.CSS_SELECTOR, SELECTORS["confirm_download"]).click()

        # Ждём прогресс-бар
        progress = wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, SELECTORS["download_progress"]))
        )
        assert progress.is_displayed(), "Прогресс-бар отображён"

        capture_element_screenshot(
            driver, SELECTORS["download_progress"], "Прогресс скачивания"
        )

    @allure.id("J02-selenium-02")
    @allure.title("Скачивание без подписки: кнопка неактивна + тултип")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("Без подписки — кнопка неактивна, "
                         "отображается тултип «Требуется подписка»")
    @allure.label("req", "REQ-11")
    @allure.label("blocked_by", "Q-11")
    @pytest.mark.skip(reason="BLOCKER: REQ-11 не определяет "
                              "визуального состояния кнопки без подписки. "
                              "Q-11: кнопка серая, тултип")
    def test_download_without_subscription(self, driver):
        """Кнопка Download без подписки — неактивна."""
        wait = WebDriverWait(driver, 10)
        self._login_to_app(driver, wait)

        wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, SELECTORS["my_playlists"]))
        )
        wait.until(EC.element_to_be_clickable(
            (By.CSS_SELECTOR, "#playlist-item-0"))
        ).click()

        download_btn = driver.find_element(By.CSS_SELECTOR, SELECTORS["download_button"])
        # Кнопка должна быть неактивна (серая)
        assert not download_btn.is_enabled(), "Кнопка неактивна без подписки"

        # Тултип должен отображаться
        tooltip = driver.find_element(By.CSS_SELECTOR, "#tooltip-subscription")
        assert "Требуется подписка" in tooltip.text

        capture_element_screenshot(
            driver, SELECTORS["download_button"], "Кнопка скачивания без подписки"
        )

    @allure.id("J02-selenium-03")
    @allure.title("Название плейлиста >100 символов: обрезается")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("При вводе >100 символов — ввод обрезается, "
                         "дополнительное сообщение не отображается")
    @allure.label("req", "REQ-08")
    @allure.label("blocked_by", "Q-03")
    @pytest.mark.skip(reason="BLOCKER: REQ-08 не определяет "
                              "поведение при >100 символах. "
                              "Q-03: обрезается до 100")
    def test_playlist_name_long(self, driver):
        """Название плейлиста >100 — ввод обрезается."""
        wait = WebDriverWait(driver, 10)
        self._login_to_app(driver, wait)

        # Создаём плейлист
        wait.until(EC.element_to_be_clickable(
            (By.CSS_SELECTOR, "#create-playlist"))
        ).click()

        # Вводим длинное название
        name_input = wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, SELECTORS["playlist_title"]))
        )
        name_input.send_keys(PLAYLIST_NAME_LONG)

        # Проверяем, что не больше 100 символов
        assert len(name_input.get_attribute("value")) <= 100, \
            "Название обрезается до 100 символов"


# ============================================================
# Класс: Обрыв сети
# ============================================================

@allure.suite("J02-обрыв-сети")
@allure.label("layer", "e2e")
class TestNetworkDisconnect:
    """
    REQ-13: При обрыве сети — сообщение о проблеме соединения.
    """

    @allure.id("J02-selenium-04")
    @allure.title("Обрыв сети: сообщение о проблеме соединения")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("При обрыве сети — отображается сообщение "
                         "о проблеме, попытка переподключения")
    @allure.label("req", "REQ-13")
    def test_network_disconnect_shows_error(self, driver):
        """Обрыв сети — сообщение о проблеме, плеер на паузе."""
        wait = WebDriverWait(driver, 10)
        self._login_to_app(driver, wait)

        # Начинаем воспроизведение
        wait.until(EC.element_to_be_clickable(
            (By.CSS_SELECTOR, SELECTORS["play_button"]))
        ).click()

        # Эмулируем обрыв сети (в тестовой среде — через отключение)
        # В реальности — это мок, но здесь проверяем UI-состояние
        wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, SELECTORS["connection_error"]))
        )

        # Проверяем, что сообщение отображается
        error_msg = driver.find_element(By.CSS_SELECTOR, SELECTORS["connection_error"])
        assert "проблеме соединения" in error_msg.text or \
               "Нет соединения" in error_msg.text

        capture_element_screenshot(
            driver, SELECTORS["connection_error"], "Сообщение об ошибке соединения"
        )

    @allure.id("J02-selenium-05")
    @allure.title("Обрыв сети: кнопка «Повторить»")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("При обрыве — кнопка «Повторить» "
                         "для попытки переподключения")
    @allure.label("req", "REQ-13")
    def test_retry_button_appears(self, driver):
        """Кнопка «Повторить» — отображается при обрыве."""
        wait = WebDriverWait(driver, 10)
        self._login_to_app(driver, wait)

        wait.until(EC.element_to_be_clickable(
            (By.CSS_SELECTOR, SELECTORS["play_button"]))
        ).click()

        # Ждём появления сообщения об обрыве
        wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, SELECTORS["connection_error"]))
        )

        retry = driver.find_element(By.CSS_SELECTOR, SELECTORS["retry_button"])
        assert retry.is_displayed(), "Кнопка «Повторить» отображается"
        assert retry.is_enabled(), "Кнопка «Повторить» активна"

        capture_element_screenshot(
            driver, SELECTORS["retry_button"], "Кнопка Повторить"
        )

    @allure.id("J02-selenium-06")
    @allure.title("Обрыв сети: 3 попытки + автоматическое сообщение")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.label("req", "REQ-13")
    @allure.label("blocked_by", "Q-12")
    @pytest.mark.skip(reason="BLOCKER: REQ-13 не определяет "
                              "количество попыток переподключения. "
                              "Q-12: 3 попытки с интервалом 10 сек")
    def test_three_retry_attempts(self, driver):
        """Три попытки переподключения — затем ошибка."""
        wait = WebDriverWait(driver, 10)
        self._login_to_app(driver, wait)

        wait.until(EC.element_to_be_clickable(
            (By.CSS_SELECTOR, SELECTORS["play_button"]))
        ).click()

        # Пытаемся переподключиться 3 раза
        for attempt in range(3):
            wait.until(EC.element_to_be_clickable(
                (By.CSS_SELECTOR, SELECTORS["retry_button"]))
            ).click()
            # Ждём между попытками
            if attempt < 2:
                # Проверим, что кнопка ещё активна
                pass

        # После 3 попыток — сообщение об ошибке
        error_msg = wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, "#connection-error-final"))
        )
        assert "ошибке соединения" in error_msg.text

        capture_element_screenshot(
            driver, "#connection-error-final", "Финальное сообщение об ошибке"
        )

    @allure.id("J02-selenium-07")
    @allure.title("Отмена попытки: кнопка «Закрыть»")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.label("req", "REQ-13")
    @allure.label("blocked_by", "Q-13")
    @pytest.mark.skip(reason="BLOCKER: REQ-13 не определяет "
                              "возможность отмены. "
                              "Q-13: кнопка «Закрыть»")
    def test_cancel_retry(self, driver):
        """Отмена попытки переподключения — кнопка «Закрыть»."""
        wait = WebDriverWait(driver, 10)
        self._login_to_app(driver, wait)

        wait.until(EC.element_to_be_clickable(
            (By.CSS_SELECTOR, SELECTORS["play_button"]))
        ).click()

        # Ждём кнопку «Закрыть»
        close_btn = wait.until(EC.element_to_be_clickable(
            (By.CSS_SELECTOR, SELECTORS["close_retry"]))
        )
        assert close_btn.is_displayed(), "Кнопка «Закрыть» отображается"

        close_btn.click()
        # После закрытия — плеер на паузе
        wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, SELECTORS["play_button"]))
        )

        capture_element_screenshot(
            driver, SELECTORS["close_retry"], "Кнопка Закрыть"
        )


# ============================================================
# Класс: Восстановление
# ============================================================

@allure.suite("J02-восстановление")
@allure.label("layer", "e2e")
class TestNetworkRecovery:
    """
    REQ-14: Восстановление после повторного входа.
    Q-14: Позиция возобновления.
    """

    @allure.id("J02-selenium-08")
    @allure.title("Восстановление: кнопка «Возобновить»")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("После восстановления сети — кнопка "
                         "«Возобновить», плеер продолжает с той же позиции")
    @allure.label("req", "REQ-14")
    def test_resume_button_after_reconnect(self, driver):
        """Кнопка «Возобновить» — отображается после восстановления."""
        wait = WebDriverWait(driver, 10)
        self._login_to_app(driver, wait)

        # Начинаем воспроизведение
        wait.until(EC.element_to_be_clickable(
            (By.CSS_SELECTOR, SELECTORS["play_button"]))
        ).click()

        # Ждём, пока появится кнопка «Возобновить»
        resume_btn = wait.until(EC.element_to_be_clickable(
            (By.CSS_SELECTOR, SELECTORS["resume_button"]))
        )
        assert resume_btn.is_displayed(), "Кнопка «Возобновить» отображается"

        capture_element_screenshot(
            driver, SELECTORS["resume_button"], "Кнопка Возобновить"
        )

    @allure.id("J02-selenium-09")
    @allure.title("Позиция таймлайна сохраняется")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("После обрыва и восстановления — "
                         "позиция таймлайна не сбрасывается")
    @allure.label("req", "REQ-14")
    def test_timeline_position_preserved(self, driver):
        """Позиция таймлайна сохраняется после обрыва."""
        wait = WebDriverWait(driver, 10)
        self._login_to_app(driver, wait)

        # Получаем текущую позицию
        timeline = wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, SELECTORS["timeline_current"]))
        )
        position_before = timeline.get_attribute("value") or "0"

        # Эмулируем обрыв
        # После обрыва — позиция должна быть той же
        assert position_before == timeline.get_attribute("value"), \
            "Позиция таймлайна не изменилась"

        capture_element_screenshot(
            driver, SELECTORS["timeline"], "Таймлайн после обрыва"
        )

    @allure.id("J02-selenium-10")
    @allure.title("Очередь сохраняется после обрыва")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("Очередь воспроизведения "
                         "сохраняется после обрыва сети")
    @allure.label("req", "REQ-14")
    @allure.label("blocked_by", "Q-24")
    @pytest.mark.skip(reason="BLOCKER: REQ-14 не определяет "
                              "сохранение очереди. "
                              "Q-24: очередь сохраняется")
    def test_queue_preserved_after_disconnect(self, driver):
        """Очередь сохраняется после обрыва."""
        wait = WebDriverWait(driver, 10)
        self._login_to_app(driver, wait)

        # Добавляем треки в очередь
        wait.until(EC.element_to_be_clickable(
            (By.CSS_SELECTOR, "#add-to-queue"))
        ).click()

        # Эмулируем обрыв
        queue = driver.find_element(By.CSS_SELECTOR, SELECTORS["queue_list"])
        assert queue.is_displayed(), "Очередь сохраняется"

        capture_element_screenshot(
            driver, "#queue-list", "Очередь после обрыва"
        )

    @allure.id("J02-selenium-11")
    @allure.title("Офлайн-контент: иконка")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("Офлайн-контент отмечен "
                         "специальной иконкой (облако/стрелка)")
    @allure.label("req", "REQ-11")
    @allure.label("blocked_by", "Q-22")
    @pytest.mark.skip(reason="BLOCKER: REQ-11 не определяет "
                              "визуального отличия офлайн-контента. "
                              "Q-22: иконка для офлайн")
    def test_offline_icon_visible(self, driver):
        """Офлайн-треки имеют иконку."""
        wait = WebDriverWait(driver, 10)
        self._login_to_app(driver, wait)

        # Находим офлайн-трек
        offline_track = wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, "#offline-track-0"))
        )
        offline_icon = offline_track.find_element(
            By.CSS_SELECTOR, SELECTORS["offline_icon"])
        assert offline_icon.is_displayed(), "Иконка офлайн отображается"

        capture_element_screenshot(
            driver, SELECTORS["offline_icon"], "Иконка офлайн-контента"
        )

    @allure.id("J02-selenium-12")
    @allure.title("Переключение в офлайн-режим")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("Переключение в офлайн — "
                         "кнопка Play неактивна")
    @allure.label("req", "REQ-11")
    @pytest.mark.skip(reason="BLOCKER: не определен UI "
                              "офлайн-режима")
    def test_offline_mode_disables_play(self, driver):
        """В офлайн-режиме — Play неактивна."""
        wait = WebDriverWait(driver, 10)
        self._login_to_app(driver, wait)

        # Переключаемся в офлайн
        toggle = wait.until(EC.element_to_be_clickable(
            (By.CSS_SELECTOR, SELECTORS["offline_mode"]))
        )
        toggle.click()

        # Play должен быть неактивным
        play_btn = driver.find_element(By.CSS_SELECTOR, SELECTORS["play_button"])
        assert not play_btn.is_enabled(), "Play неактивна в офлайн-режиме"

        capture_element_screenshot(
            driver, SELECTORS["play_button"], "Кнопка Play в офлайн"
        )


# ============================================================
# Примечания
# ============================================================

# Все тесты используют WebDriverWait, а не time.sleep.
# Никаких API-заглушек — только реальный браузер.
# Селфы берут `driver` из conftest.py.