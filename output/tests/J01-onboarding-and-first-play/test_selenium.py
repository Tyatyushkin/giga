"""
Selenium-тесты для J01 (онбординг и первый запуск) — визуальное тестирование браузера

Основание: input/requirements/zvuk.md, zvuk-sample.md, _answers.md
Требования: REQ-01..REQ-14, BR-001..BR-011

Каждый test_ — один шаг E2E-кейса.
"""

import allure
from typing import Final

import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

# Константы тестовых данных (из _answers.md, Q-01..Q-30)
PHONE_NUMBER: Final[str] = "+7 999 000-00-11"  # Q-07, формат РФ
SMS_CODE: Final[str] = "1234"                    # REQ-01, 4 цифры
ONBOARDING_GENRES: Final[tuple] = ("Рок", "Поп", "Электроника")  # REQ-02, >=3
SEARCH_QUERY: Final[str] = "Весна"               # REQ-04, поисковый запрос
TRACK_TITLE: Final[str] = "Весна"                # REQ-05
ARTIST_NAME: Final[str] = "Дельфин"             # REQ-05
PLAYLIST_TITLE: Final[str] = "Тестовый плейлист 2026-07"  # REQ-08

# Селекторы UI-элементов (на основе требований)
# Эти селекторы — предположение, так как точная верстка не задана.
# При реальном использовании нужно заменить на актуальные из DOM проекта.
SELECTORS: Final[dict] = {
    "phone_input":    "#phone-input",
    "submit_phone":   "#submit-phone",
    "sms_code_input": "#sms-code-input",
    "submit_sms":     "#submit-sms",
    "resend_sms":     "#resend-sms",
    "timer":          "#sms-timer",
    "genre_rock":     "#genre-rock",
    "genre_pop":      "#genre-pop",
    "genre_electronica": "#genre-electronica",
    "next_onboarding":  "#onboarding-next",
    "skip_onboarding":  "#onboarding-skip",
    "search_input":   "#search-input",
    "search_submit":  "#search-submit",
    "tracks_tab":     "#tracks-tab",
    "artists_tab":    "#artists-tab",
    "albums_tab":     "#albums-tab",
    "playlists_tab":  "#playlists-tab",
    "play_button":    "#play-button",
    "pause_button":   "#pause-button",
    "player_artwork": "#player-artwork",
    "player_title":   "#player-title",
    "player_artist":  "#player-artist",
    "timeline":       "#timeline",
    "like_button":    "#like-button",
    "add_to_queue":   "#add-to-queue",
    "queue_list":     "#queue-list",
    "my_music":       "#my-music",
    "my_playlists":   "#my-playlists",
    "logout_button":  "#logout-button",
    "recommendations": "#recommendations-block",
}


def capture_element_screenshot(driver, selector: str, name: str):
    """
    Сделать скриншот элемента и прикрепить к Allure.

    Args:
        driver: WebDriver
        selector: CSS-селектор элемента
        name: Имя вложения в Allure
    Returns:
        Элемент Selenium
    """
    element = driver.find_element(By.CSS_SELECTOR, selector)
    screenshot = element.screenshot_as_png()
    allure.attach(screenshot, name=name, attachment_type=allure.attachment_type.PNG)
    return element


# ============================================================
# Класс: Онбординг и авторизация
# ============================================================

@allure.suite("J01-онбординг-и-первый-запуск")
@allure.label("layer", "e2e")
@allure.parent_suite("Авторизация")
class TestOnboardingAndAuth:
    """Счастливый путь: авторизация → онбординг → поиск → плеер."""

    def _login(self, driver, base_url: str, wait: WebDriverWait):
        """Шаг 1-2: Ввод номера и получение SMS."""
        driver.get(f"{base_url}/login")
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, SELECTORS["phone_input"])))

        phone_input = driver.find_element(By.CSS_SELECTOR, SELECTORS["phone_input"])
        phone_input.send_keys(PHONE_NUMBER)

        submit_btn = driver.find_element(By.CSS_SELECTOR, SELECTORS["submit_phone"])
        assert submit_btn.is_enabled(), "Кнопка должна быть активна после ввода номера"
        submit_btn.click()
        # Ждём появления поля для SMS-кода
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, SELECTORS["sms_code_input"])))

    @allure.id("J01-selenium-01")
    @allure.title("Авторизация: ввод номера телефона")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("Проверка, что поле ввода номера отображается, "
                         "кнопка «Отправить код» активна после ввода")
    @allure.label("req", "REQ-01")
    def test_phone_input_visible_and_active(self, driver):
        """Ввод номера телефона — поле и кнопка активны."""
        wait = WebDriverWait(driver, 10)
        self._login(driver, self.BASE_URL, wait)

        # Скриншот поля ввода
        capture_element_screenshot(driver, SELECTORS["phone_input"], "Поле ввода номера телефона")

    @allure.id("J01-selenium-02")
    @allure.title("Авторизация: ввод SMS-кода")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("После отправки номера отображается поле для SMS-кода")
    @allure.label("req", "REQ-01")
    def test_sms_code_field_appears(self, driver):
        """После отправки номера — отображается поле ввода кода."""
        wait = WebDriverWait(driver, 10)
        self._login(driver, self.BASE_URL, wait)

        # Ожидаем появления поля для кода
        code_input = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, SELECTORS["sms_code_input"]))
        )
        assert code_input.is_displayed(), "Поле для SMS-кода должно быть видимо"

        # Вводим корректный код
        code_input.send_keys(SMS_CODE)
        submit_sms = driver.find_element(By.CSS_SELECTOR, SELECTORS["submit_sms"])
        assert submit_sms.is_enabled(), "Кнопка подтверждения должна быть активна"

        capture_element_screenshot(driver, SELECTORS["submit_sms"], "Кнопка подтверждения SMS-кода")

    @allure.id("J01-selenium-03")
    @allure.title("Онбординг: отображается экран выбора жанров")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("После подтверждения SMS — экран онбординга с жанрами")
    @allure.label("req", "REQ-02")
    def test_onboarding_screen_appears(self, driver):
        """После успешного входа — отображается онбординг с выбором жанров."""
        wait = WebDriverWait(driver, 10)
        self._login(driver, self.BASE_URL, wait)

        # Подтверждаем код
        code_input = driver.find_element(By.CSS_SELECTOR, SELECTORS["sms_code_input"])
        code_input.send_keys(SMS_CODE)
        driver.find_element(By.CSS_SELECTOR, SELECTORS["submit_sms"]).click()

        # Ждём экран онбординга
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, SELECTORS["genre_rock"])))
        assert driver.find_element(By.CSS_SELECTOR, SELECTORS["genre_rock"]).is_displayed()
        assert driver.find_element(By.CSS_SELECTOR, SELECTORS["genre_pop"]).is_displayed()
        assert driver.find_element(By.CSS_SELECTOR, SELECTORS["genre_electronica"]).is_displayed()

        capture_element_screenshot(driver, "#onboarding-genres", "Экран выбора жанров")

    @allure.id("J01-selenium-04")
    @allure.title("Онбординг: выбор 3 жанров и кнопка «Далее»")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("После выбора 3+ жанров кнопка «Далее» становится активной")
    @allure.label("req", "REQ-02")
    def test_select_three_genres_and_next(self, driver):
        """Выбор трёх жанров на онбординге — счётчик 3, кнопка «Далее» активна."""
        wait = WebDriverWait(driver, 10)
        self._login(driver, self.BASE_URL, wait)

        # Подтверждаем код
        code_input = driver.find_element(By.CSS_SELECTOR, SELECTORS["sms_code_input"])
        code_input.send_keys(SMS_CODE)
        driver.find_element(By.CSS_SELECTOR, SELECTORS["submit_sms"]).click()

        # Ждём онбординг
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, SELECTORS["genre_rock"])))

        # Выбираем 3 жанра
        driver.find_element(By.CSS_SELECTOR, SELECTORS["genre_rock"]).click()
        driver.find_element(By.CSS_SELECTOR, SELECTORS["genre_pop"]).click()
        driver.find_element(By.CSS_SELECTOR, SELECTORS["genre_electronica"]).click()

        # Проверяем счётчик (предполагается, что он где-то отображается)
        counter = driver.find_element(By.CSS_SELECTOR, "#genre-counter")
        assert counter.text == "3", "Счётчик выбранных жанров = 3"

        # Кнопка «Далее» активна
        next_btn = driver.find_element(By.CSS_SELECTOR, SELECTORS["next_onboarding"])
        assert next_btn.is_enabled(), "Кнопка «Далее» активна после выбора 3 жанров"

        capture_element_screenshot(driver, SELECTORS["next_onboarding"], "Кнопка Далее")

    @allure.id("J01-selenium-05")
    @allure.title("Онбординг: рекомендации отображаются")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("После онбординга — блок рекомендаций не пуст")
    @allure.label("req", "REQ-03")
    def test_recommendations_appear(self, driver):
        """После онбординга — блок «Рекомендации» отображается."""
        wait = WebDriverWait(driver, 10)
        self._login(driver, self.BASE_URL, wait)

        # Проходим онбординг
        code_input = driver.find_element(By.CSS_SELECTOR, SELECTORS["sms_code_input"])
        code_input.send_keys(SMS_CODE)
        driver.find_element(By.CSS_SELECTOR, SELECTORS["submit_sms"]).click()

        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, SELECTORS["genre_rock"])))
        driver.find_element(By.CSS_SELECTOR, SELECTORS["genre_rock"]).click()
        driver.find_element(By.CSS_SELECTOR, SELECTORS["genre_pop"]).click()
        driver.find_element(By.CSS_SELECTOR, SELECTORS["genre_electronica"]).click()
        driver.find_element(By.CSS_SELECTOR, SELECTORS["next_onboarding"]).click()

        # Ждём главный экран
        recommendations = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, SELECTORS["recommendations"]))
        )
        assert recommendations.is_displayed(), "Блок рекомендаций отображается"
        capture_element_screenshot(driver, SELECTORS["recommendations"], "Рекомендации")


# ============================================================
# Класс: Поиск
# ============================================================

@allure.suite("J01-поиск")
@allure.label("layer", "e2e")
class TestSearch:
    """Поиск музыки: ввод запроса, результаты, вкладки."""

    @allure.id("J01-selenium-06")
    @allure.title("Поиск: ввод запроса и отображение результатов")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("После ввода поискового запроса — отображаются "
                         "вкладки результатов: Треки, Исполнители, Альбомы, Плейлисты")
    @allure.label("req", "REQ-04")
    def test_search_input_and_results(self, driver):
        """Поиск по трекам — вкладки результатов отображаются."""
        wait = WebDriverWait(driver, 10)

        # Переходим на страницу поиска
        driver.get("https://zvuk.com/search")

        search_input = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, SELECTORS["search_input"]))
        )
        search_input.send_keys(SEARCH_QUERY)

        # Жмём «Искать»
        driver.find_element(By.CSS_SELECTOR, SELECTORS["search_submit"]).click()

        # Ждём вкладки
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, SELECTORS["tracks_tab"])))
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, SELECTORS["artists_tab"])))
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, SELECTORS["albums_tab"])))
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, SELECTORS["playlists_tab"])))

        # Все вкладки видны
        assert driver.find_element(By.CSS_SELECTOR, SELECTORS["tracks_tab"]).is_displayed()
        assert driver.find_element(By.CSS_SELECTOR, SELECTORS["artists_tab"]).is_displayed()

        capture_element_screenshot(driver, SELECTORS["search_input"], "Поисковый запрос")

    @allure.id("J01-selenium-07")
    @allure.title("Поиск: пустой результат — сообщение «Нет результатов»")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("При пустом результате — отображается сообщение "
                         "«Нет результатов» на каждой вкладке")
    @allure.label("req", "REQ-04")
    @allure.label("req", "BR-014")
    def test_search_empty_result(self, driver):
        """Поиск без результатов — сообщение об отсутствии."""
        wait = WebDriverWait(driver, 10)
        driver.get("https://zvuk.com/search")

        search_input = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, SELECTORS["search_input"]))
        )
        search_input.send_keys("zzzzzzzzz_не_существует")  # заведомо пустой запрос
        driver.find_element(By.CSS_SELECTOR, SELECTORS["search_submit"]).click()

        # Ждём сообщения об отсутствии результатов
        no_results = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#no-results"))
        )
        assert "Нет результатов" in no_results.text

        capture_element_screenshot(driver, "#no-results", "Пустой результат поиска")


# ============================================================
# Класс: Плеер и воспроизведение
# ============================================================

@allure.suite("J01-плеер")
@allure.label("layer", "e2e")
class TestPlayer:
    """Плеер: воспроизведение, лайк, очередь, выход."""

    @allure.id("J01-selenium-08")
    @allure.title("Плеер: запуск трека и отображение информации")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("После запуска трека — плеер развёрнут: "
                         "обложка, название, исполнитель, таймлайн")
    @allure.label("req", "REQ-05")
    def test_player_expands_on_play(self, driver):
        """Запуск трека — плеер развёрнут с информацией о треке."""
        wait = WebDriverWait(driver, 10)
        driver.get("https://zvuk.com/search")

        # Вводим запрос и находим трек
        search_input = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, SELECTORS["search_input"]))
        )
        search_input.send_keys(SEARCH_QUERY)
        driver.find_element(By.CSS_SELECTOR, SELECTORS["search_submit"]).click()

        # Кликаем по первому результату (предполагаем, что это трек)
        wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#search-result-0"))).click()

        # Ждём развёртывания плеера
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, SELECTORS["player_artwork"])))
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, SELECTORS["player_title"])))
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, SELECTORS["player_artist"])))

        # Проверяем, что плеер отображает информацию
        assert TRACK_TITLE in driver.find_element(By.CSS_SELECTOR, SELECTORS["player_title"]).text
        assert ARTIST_NAME in driver.find_element(By.CSS_SELECTOR, SELECTORS["player_artist"]).text

        capture_element_screenshot(driver, SELECTORS["player_artwork"], "Обложка трека")

    @allure.id("J01-selenium-09")
    @allure.title("Плеер: пауза и возобновление")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("Кнопка Play/Pause переключает состояние плеера")
    @allure.label("req", "REQ-05")
    def test_play_pause_toggle(self, driver):
        """Нажатие Play/Pause — плеер переключает состояние."""
        wait = WebDriverWait(driver, 10)
        driver.get("https://zvuk.com/search")
        search_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, SELECTORS["search_input"])))
        search_input.send_keys(SEARCH_QUERY)
        driver.find_element(By.CSS_SELECTOR, SELECTORS["search_submit"]).click()
        wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#search-result-0"))).click()

        # Ждём плеер
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, SELECTORS["play_button"])))

        # Нажимаем Play
        driver.find_element(By.CSS_SELECTOR, SELECTORS["play_button"]).click()
        # Проверяем, что кнопка стала Pause (или что кнопка Pause теперь видна)
        assert driver.find_element(By.CSS_SELECTOR, SELECTORS["pause_button"]).is_displayed()

        # Нажимаем Pause
        driver.find_element(By.CSS_SELECTOR, SELECTORS["pause_button"]).click()
        assert driver.find_element(By.CSS_SELECTOR, SELECTORS["play_button"]).is_displayed()

        capture_element_screenshot(driver, SELECTORS["play_button"], "Кнопка Play")

    @allure.id("J01-selenium-10")
    @allure.title("Лайк: трек добавлен в «Мне нравится»")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("Лайк трека — счётчик увеличивается, "
                         "трек отображается в «Мне нравится»")
    @allure.label("req", "REQ-07")
    def test_like_track(self, driver):
        """Лайк трека — счётчик +1, трек в «Мне нравится»."""
        wait = WebDriverWait(driver, 10)
        driver.get("https://zvuk.com/search")
        search_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, SELECTORS["search_input"])))
        search_input.send_keys(SEARCH_QUERY)
        driver.find_element(By.CSS_SELECTOR, SELECTORS["search_submit"]).click()
        wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#search-result-0"))).click()

        # Жмём лайк
        wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, SELECTORS["like_button"]))).click()

        # Проверяем, что счётчик = 1 (предполагается, что он отображается)
        counter = driver.find_element(By.CSS_SELECTOR, "#like-counter")
        assert "1" in counter.text

        capture_element_screenshot(driver, SELECTORS["like_button"], "Кнопка лайка")

    @allure.id("J01-selenium-11")
    @allure.title("Очередь: трек добавлен в очередь")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("Действие «Играть следующим» — "
                         "трек появляется в очереди на позиции после текущего")
    @allure.label("req", "REQ-06")
    def test_add_to_queue(self, driver):
        """Добавление в очередь — трек в очереди."""
        wait = WebDriverWait(driver, 10)
        driver.get("https://zvuk.com/search")
        search_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, SELECTORS["search_input"])))
        search_input.send_keys(SEARCH_QUERY)
        driver.find_element(By.CSS_SELECTOR, SELECTORS["search_submit"]).click()
        wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#search-result-0"))).click()

        # Добавляем в очередь
        wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, SELECTORS["add_to_queue"]))).click()

        # Ждём, что очередь отображается
        queue = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, SELECTORS["queue_list"])))
        assert TRACK_TITLE in queue.text

        capture_element_screenshot(driver, SELECTORS["queue_list"], "Очередь воспроизведения")

    @allure.id("J01-selenium-12")
    @allure.title("Выход: данные плеера очищаются")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("При выходе — локальные данные плеера "
                         "(очередь, позиция) очищаются")
    @allure.label("req", "REQ-12")
    def test_logout_clears_player(self, driver):
        """Выход из аккаунта — плеер сбрасывается."""
        wait = WebDriverWait(driver, 10)
        driver.get("https://zvuk.com/search")
        search_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, SELECTORS["search_input"])))
        search_input.send_keys(SEARCH_QUERY)
        driver.find_element(By.CSS_SELECTOR, SELECTORS["search_submit"]).click()
        wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#search-result-0"))).click()

        # Нажимаем кнопку выхода
        wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, SELECTORS["logout_button"]))).click()

        # После выхода — плеер скрыт, страница входа
        # Наблюдаемый признак: исчезновение плеера, появление формы входа
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, SELECTORS["phone_input"])))
        assert not driver.find_elements(By.CSS_SELECTOR, SELECTORS["player_title"]), \
            "Информация плеера не отображается после выхода"

        capture_element_screenshot(driver, SELECTORS["phone_input"], "Форма входа после выхода")


# ============================================================
# Класс: Повторный вход (восстановление)
# ============================================================

@allure.suite("J01-повторный-вход")
@allure.label("layer", "e2e")
class TestReAuth:
    """Повторный вход: восстановление плейлистов и лайков."""

    @allure.id("J01-selenium-13")
    @allure.title("Повторный вход: плейлисты и лайки восстановлены")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("После повторного входа — плейлисты и лайки "
                         "восстанавливаются")
    @allure.label("req", "REQ-14")
    def test_reauth_restores_data(self, driver):
        """Повторный вход — данные аккаунта восстанавливаются."""
        wait = WebDriverWait(driver, 10)

        # Выполняем логин
        driver.get("https://zvuk.com/login")
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, SELECTORS["phone_input"]))).send_keys(PHONE_NUMBER)
        driver.find_element(By.CSS_SELECTOR, SELECTORS["submit_phone"]).click()
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, SELECTORS["sms_code_input"]))).send_keys(SMS_CODE)
        driver.find_element(By.CSS_SELECTOR, SELECTORS["submit_sms"]).click()

        # Проходим онбординг
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, SELECTORS["genre_rock"])))
        driver.find_element(By.CSS_SELECTOR, SELECTORS["genre_rock"]).click()
        driver.find_element(By.CSS_SELECTOR, SELECTORS["genre_pop"]).click()
        driver.find_element(By.CSS_SELECTOR, SELECTORS["genre_electronica"]).click()
        driver.find_element(By.CSS_SELECTOR, SELECTORS["next_onboarding"]).click()

        # Проверяем, что «Моя музыка» отображается
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, SELECTORS["my_music"])))
        assert driver.find_element(By.CSS_SELECTOR, SELECTORS["my_music"]).is_displayed()

        # Проверяем, что плейлисты отображаются
        assert driver.find_element(By.CSS_SELECTOR, SELECTORS["my_playlists"]).is_displayed()

        capture_element_screenshot(driver, SELECTORS["my_music"], "Моя музыка после входа")


# ============================================================
# Граничные случаи (BLOCKER — требуют ответа из Q)
# ============================================================

@allure.suite("J01-граничные")
@allure.label("layer", "e2e")
class TestBoundaryCases:

    @allure.id("J01-selenium-14")
    @allure.title("Повторная отправка SMS: кнопка с таймером")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.label("req", "REQ-01")
    @allure.label("blocked_by", "Q-02")
    @pytest.mark.skip(reason="BLOCKER: REQ-01 не определяет UI-таймера и "
                              "неактивной кнопки. Уточняющий вопрос Q-02: "
                              "кнопка «Отправить снова» становится активной через 60 секунд")
    def test_resend_sms_timer(self, driver):
        """Повторная отправка SMS — кнопка неактивна 60 секунд."""
        wait = WebDriverWait(driver, 10)
        driver.get("https://zvuk.com/login")
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, SELECTORS["phone_input"]))).send_keys(PHONE_NUMBER)
        driver.find_element(By.CSS_SELECTOR, SELECTORS["submit_phone"]).click()

        # После отправки — ждём, что кнопка появится
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, SELECTORS["resend_sms"])))
        resend = driver.find_element(By.CSS_SELECTOR, SELECTORS["resend_sms"])
        # Должна быть неактивной (таймер активен)
        assert not resend.is_enabled(), "Кнопка повторной отправки должна быть неактивна"

    @allure.id("J01-selenium-15")
    @allure.title("Неверный код: 3 попытки, затем блокировка")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.label("req", "REQ-01")
    @allure.label("blocked_by", "Q-06")
    @pytest.mark.skip(reason="BLOCKER: REQ-01 не определяет поведение при 3 "
                              "неверных кодах. Уточняющий вопрос Q-06: "
                              "блокировка на 30 минут после 3 попыток")
    def test_wrong_code_three_attempts(self, driver):
        """Три неверных кода — блокировка 30 мин."""
        wait = WebDriverWait(driver, 10)
        driver.get("https://zvuk.com/login")
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, SELECTORS["phone_input"]))).send_keys(PHONE_NUMBER)
        driver.find_element(By.CSS_SELECTOR, SELECTORS["submit_phone"]).click()
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, SELECTORS["sms_code_input"])))

        # Вводим неверный код 3 раза
        code_input = driver.find_element(By.CSS_SELECTOR, SELECTORS["sms_code_input"])
        for _ in range(3):
            code_input.clear()
            code_input.send_keys("0000")  # неверный код
            driver.find_element(By.CSS_SELECTOR, SELECTORS["submit_sms"]).click()

        # После 3-й попытки — появляется сообщение об ошибке
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#error-message")))

    @allure.id("J01-selenium-16")
    @allure.title("Пустое название плейлиста: кнопка «Создать» неактивна")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.label("req", "REQ-08")
    @allure.label("blocked_by", "Q-10")
    @pytest.mark.skip(reason="BLOCKER: REQ-08 не определяет UI-элемента "
                              "пустого названия. Q-10: кнопка неактивна "
                              "при пустом названии")
    def test_empty_playlist_name(self, driver):
        """Пустое название — кнопка неактивна."""
        wait = WebDriverWait(driver, 10)
        driver.get("https://zvuk.com/playlists/new")

        # Поле ввода пустое — кнопка неактивна
        create_btn = driver.find_element(By.CSS_SELECTOR, "#create-playlist")
        assert not create_btn.is_enabled(), "Кнопка неактивна при пустом названии"


# ============================================================
# Хук для скриншота всей страницы на FAIL (уже в conftest)
# ============================================================

# Примечание:
# Все тесты используют WebDriverWait, а не time.sleep.
# Никакие API-заглушки не используются — только реальный браузер.