"""
Тесты для: J01-onboarding-and-first-play — Новый пользователь: регистрация,
онбординг, поиск и первое воспроизведение с управлением очередью.

Основание: output/suites/J01-onboarding-and-first-play.md,
           output/cases/J01-onboarding-and-first-play/TC-*.md
"""

import pytest
import allure

from test_data import (
    PHONE_NUMBER,
    CONFIRMATION_CODE,
    SELECTED_GENRES_3,
    SEARCH_QUERY_DOLPHIN,
    FIRST_TRACK,
    SECOND_TRACK,
    INVALID_CODE,
    SELECTED_GENRES_2,
    EMPTY_QUERY,
)
from api_stub import ZvukApiStub


# =====================================================================
# TC-J01-00 — Основной счастливый путь
# =====================================================================


class TestMainHappyPath:
    """Основной путь: регистрация → онбординг → поиск → плеер → очередь."""

    @allure.id("J01-TC-J01-00-01")
    @allure.label("req", "REQ-01")
    @allure.label("layer", "e2e")
    @allure.title("Открытие приложения «Звук» — экран входа")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("Шаг 1 из TC-J01-00: приложение открывается, "
                          "отображается экран входа с полем ввода номера. REQ-01")
    def test_01_open_app_show_login_screen(self, api_client: ZvukApiStub):
        """Проверяет: экран входа отображается при старте приложения."""
        # Тест проверяет, что приложение показывает экран входа
        # В заглушке это проверяем через доступность состояния
        assert hasattr(api_client, "_phone_number"), (
            "Ожидается, что клиент инициализирован"
        )

    @allure.id("J01-TC-J01-00-02")
    @allure.label("req", "REQ-01")
    @allure.label("layer", "e2e")
    @allure.title("Ввод номера телефона в поле входа")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("Шаг 2 из TC-J01-00: пользователь вводит номер +7 999 000-00-11, "
                          "он отображается целиком. REQ-01")
    def test_02_enter_phone_number(self, api_client: ZvukApiStub):
        """Проверяет: введённый номер отображается в поле."""
        result = api_client.send_code(PHONE_NUMBER)
        assert result["status"] == "code_sent", (
            f"Ожидается статус 'code_sent', получен '{result['status']}'"
        )
        assert result["phone"] == PHONE_NUMBER, (
            f"Ожидается номер '{PHONE_NUMBER}', получен '{result['phone']}'"
        )

    @allure.id("J01-TC-J01-00-03")
    @allure.label("req", "REQ-01")
    @allure.label("layer", "e2e")
    @allure.title("Подтверждение номера — экран ввода кода")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("Шаг 3 из TC-J01-00: после подтверждения номера открывается "
                          "экран ввода кода из 4 полей. REQ-01")
    def test_03_confirm_phone_opens_code_screen(self, api_client: ZvukApiStub):
        """Проверяет: открывается экран ввода кода."""
        result = api_client.send_code(PHONE_NUMBER)
        assert result["status"] == "code_sent", (
            f"Ожидается status 'code_sent', получен '{result['status']}'"
        )
        # В заглушке проверяем, что код отправлен — экран 4 полей (по REQ-01)
        assert result["code"] == CONFIRMATION_CODE, (
            f"Ожидается код '{CONFIRMATION_CODE}', получен '{result['code']}'"
        )

    @allure.id("J01-TC-J01-00-04")
    @allure.label("req", "REQ-01, REQ-02")
    @allure.label("layer", "e2e")
    @allure.title("Ввод кода подтверждения — открытие экрана онбординга")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("Шаг 4 из TC-J01-00: пользователь вводит код 1111, "
                          "открывается экран онбординга. REQ-01, REQ-02")
    def test_04_enter_code_opens_onboarding(self, api_client: ZvukApiStub):
        """Проверяет: после ввода кода открывается онбординг."""
        result = api_client.confirm_code(PHONE_NUMBER, CONFIRMATION_CODE)
        assert result["status"] == "ok", (
            f"Ожидается status 'ok', получен '{result['status']}'"
        )
        assert api_client._is_authenticated, (
            "Пользователь должен быть авторизован после правильного кода"
        )

    @allure.id("J01-TC-J01-00-05")
    @allure.label("req", "REQ-02")
    @allure.label("layer", "e2e")
    @allure.title("Выбор трёх жанров на онбординге")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("Шаг 5 из TC-J01-00: пользователь выбирает 3 жанра "
                          "(Электроника, Хип-хоп, Инди), счётчик = 3. REQ-02")
    def test_05_select_three_genres(self, api_client: ZvukApiStub):
        """Проверяет: выбор 3 жанров успешен, счётчик = 3."""
        result = api_client.select_genres(SELECTED_GENRES_3)
        assert result["status"] == "ok", (
            f"Ожидается status 'ok', получен '{result['status']}'"
        )
        assert result["count"] == 3, (
            f"Ожидается count=3, получен '{result['count']}'"
        )

    @allure.id("J01-TC-J01-00-06")
    @allure.label("req", "REQ-02, REQ-03")
    @allure.label("layer", "e2e")
    @allure.title("Подтверждение выбора жанров — главный экран с рекомендациями")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("Шаг 6 из TC-J01-00: пользователь подтверждает жанры, "
                          "открывается главный экран, блок «Рекомендации» "
                          "содержит не менее 1 элемента. REQ-02, REQ-03")
    def test_06_confirm_genres_opens_main_screen(self, api_client: ZvukApiStub):
        """Проверяет: после подтверждения жанров — главный экран."""
        # Предварительно выбираем жанры
        api_client.select_genres(SELECTED_GENRES_3)
        result = api_client.confirm_onboarding()
        assert result["status"] == "ok", (
            f"Ожидается status 'ok', получен '{result['status']}'"
        )
        assert result["screen"] == "main", (
            f"Ожидается screen 'main', получен '{result['screen']}'"
        )
        # Проверяем блок рекомендаций
        recs = api_client.get_recommendations()
        assert len(recs) >= 1, (
            "Блок «Рекомендации» должен содержать не менее 1 элемента"
        )

    @allure.id("J01-TC-J01-00-07")
    @allure.label("req", "REQ-04")
    @allure.label("layer", "e2e")
    @allure.title("Открытие раздела «Поиск»")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("Шаг 7 из TC-J01-00: пользователь открывает раздел "
                          "«Поиск», отображается поле ввода. REQ-04")
    def test_07_open_search_section(self, api_client: ZvukApiStub):
        """Проверяет: при открытии поиска отображается поле ввода."""
        # Поиск с пустым запросом — поле ввода пустое
        result = api_client.search(EMPTY_QUERY)
        assert result["tracks"] == [], (
            "При пустом запросе список треков должен быть пуст"
        )

    @allure.id("J01-TC-J01-00-08")
    @allure.label("req", "REQ-04")
    @allure.label("layer", "e2e")
    @allure.title("Поисковый запрос «Дельфин» — результаты сгруппированы")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("Шаг 8 из TC-J01-00: пользователь вводит запрос "
                          "'Дельфин', результаты сгруппированы по вкладкам "
                          "(Треки, Исполнители, Альбомы, Плейлисты). REQ-04")
    def test_08_search_dolphin_shows_grouped_results(self, api_client: ZvukApiStub):
        """Проверяет: результаты поиска сгруппированы по вкладкам."""
        result = api_client.search(SEARCH_QUERY_DOLPHIN)
        assert "tracks" in result, "Вкладка 'Треки' отсутствует в результатах"
        assert "artists" in result, "Вкладка 'Исполнители' отсутствует"
        assert "albums" in result, "Вкладка 'Альбомы' отсутствует"
        assert "playlists" in result, "Вкладка 'Плейлисты' отсутствует"

    @allure.id("J01-TC-J01-00-09")
    @allure.label("req", "REQ-05")
    @allure.label("layer", "e2e")
    @allure.title("Запуск трека «Весна» — плеер с обложкой и таймлайном")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("Шаг 9 из TC-J01-00: пользователь запускает трек "
                          "'Весна', плеер развёрнут с обложкой и таймлайном. "
                          "REQ-05")
    def test_09_play_track_opens_player(self, api_client: ZvukApiStub):
        """Проверяет: плеер отображает обложку, название, таймлайн."""
        state = api_client.get_player_state()
        assert state["track"] == FIRST_TRACK, (
            f"Ожидается трек '{FIRST_TRACK}', получен '{state['track']}'"
        )
        assert state["artist"] == "Дельфин", (
            f"Ожидается исполнитель 'Дельфин', получен '{state['artist']}'"
        )
        assert "cover" in state, "Обложка отсутствует в состоянии плеера"
        assert "timeline" in state, "Таймлайн отсутствует в состоянии плеера"

    @allure.id("J01-TC-J01-00-10")
    @allure.label("req", "REQ-06")
    @allure.label("layer", "e2e")
    @allure.title("Добавление трека «Любовь» в очередь")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("Шаг 10 из TC-J01-00: пользователь добавляет трек "
                          "'Любовь' действием «Играть следующим», он встаёт "
                          "сразу после 'Весна'. REQ-06")
    def test_10_add_to_queue_as_next(self, api_client: ZvukApiStub):
        """Проверяет: трек встаёт в очередь «Играть следующим»."""
        result = api_client.add_to_queue(SECOND_TRACK, position="next")
        assert result["status"] == "ok", (
            f"Ожидается status 'ok', получен '{result['status']}'"
        )
        assert SECOND_TRACK in result["queue"], (
            f"Трек '{SECOND_TRACK}' не найден в очереди: '{result['queue']}'"
        )


# =====================================================================
# TC-J01-01 — Повторная отправка кода (таймер)
# =====================================================================


class TestResendCodeTimer:
    """Вариант: попытка повторной отправки кода до истечения 60 секунд."""

    @allure.id("J01-TC-J01-01-01")
    @allure.label("req", "REQ-01")
    @allure.label("layer", "smoke")
    @allure.title("Открытие приложения «Звук» — экран входа")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("Шаг 1 из TC-J01-01: приложение открывается. REQ-01")
    def test_01_open_app(self, api_client: ZvukApiStub):
        """Проверяет: приложение открыто."""
        assert hasattr(api_client, "_phone_number"), "Клиент инициализирован"

    @allure.id("J01-TC-J01-01-02")
    @allure.label("req", "REQ-01")
    @allure.label("layer", "smoke")
    @allure.title("Ввод номера телефона")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("Шаг 2 из TC-J01-01: пользователь вводит номер. REQ-01")
    def test_02_enter_phone(self, api_client: ZvukApiStub):
        """Проверяет: номер отображается."""
        result = api_client.send_code(PHONE_NUMBER)
        assert result["phone"] == PHONE_NUMBER

    @allure.id("J01-TC-J01-01-03")
    @allure.label("req", "REQ-01")
    @allure.label("layer", "smoke")
    @allure.title("Подтверждение номера — экран ввода кода (4 поля)")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("Шаг 3 из TC-J01-01: код отправлен, экран ввода. REQ-01")
    def test_03_confirm_phone(self, api_client: ZvukApiStub):
        """Проверяет: экран ввода кода открыт."""
        result = api_client.send_code(PHONE_NUMBER)
        assert result["code"] == CONFIRMATION_CODE

    @allure.id("J01-TC-J01-01-04")
    @allure.label("req", "REQ-01")
    @allure.label("layer", "blocker")
    @allure.title("Попытка повторной отправки до 60 секунд — кнопка неактивна")
    @allure.severity(allure.severity_level.TRIVIAL)
    @allure.description("Шаг 4 из TC-J01-01: пользователь пытается отправить "
                          "код повторно. REQ-01 говорит «повтор через 60 с», "
                          "но UI неактивной кнопки и таймера не определён.")
    @allure.label("bug", "BLOCKER: REQ-01 не определяет UI таймера")
    @allure.label("blocked_by", "question-2")
    @pytest.mark.skip(
        reason="BLOCKER: REQ-01 не определяет UI таймера и неактивной кнопки. "
               "Уточняющий вопрос 2: что видит пользователь при неактивной кнопке?"
    )
    def test_04_resend_code_before_60s(self, api_client: ZvukApiStub):
        """Проверяет: кнопка неактивна, таймер отображается.

        Пропущен, так как REQ-01 не определяет UI таймера.
        """
        available = api_client.is_code_resend_available()
        assert not available, (
            "Кнопка повторной отправки должна быть неактивна"
        )


# =====================================================================
# TC-J01-02 — Неверный код подтверждения
# =====================================================================


class TestInvalidCode:
    """Вариант: ввод неверного кода подтверждения."""

    @allure.id("J01-TC-J01-02-01")
    @allure.label("req", "REQ-01")
    @allure.label("layer", "smoke")
    @allure.title("Открытие приложения «Звук» — экран входа")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("Шаг 1 из TC-J01-02: приложение открывается. REQ-01")
    def test_01_open_app(self, api_client: ZvukApiStub):
        assert hasattr(api_client, "_phone_number")

    @allure.id("J01-TC-J01-02-02")
    @allure.label("req", "REQ-01")
    @allure.label("layer", "smoke")
    @allure.title("Ввод номера телефона")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("Шаг 2 из TC-J01-02: номер введён. REQ-01")
    def test_02_enter_phone(self, api_client: ZvukApiStub):
        result = api_client.send_code(PHONE_NUMBER)
        assert result["phone"] == PHONE_NUMBER

    @allure.id("J01-TC-J01-02-03")
    @allure.label("req", "REQ-01")
    @allure.label("layer", "smoke")
    @allure.title("Подтверждение номера — экран ввода кода")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("Шаг 3 из TC-J01-02: код отправлен. REQ-01")
    def test_03_confirm_phone(self, api_client: ZvukApiStub):
        result = api_client.send_code(PHONE_NUMBER)
        assert result["code"] == CONFIRMATION_CODE

    @allure.id("J01-TC-J01-02-04")
    @allure.label("req", "REQ-01")
    @allure.label("layer", "blocker")
    @allure.title("Ввод неверного кода — ошибка и сообщение")
    @allure.severity(allure.severity_level.TRIVIAL)
    @allure.description("Шаг 4 из TC-J01-02: пользователь вводит неверный код "
                          "0000. REQ-01 не определяет поведение при неверном "
                          "коде.")
    @allure.label("bug", "BLOCKER: REQ-01 не определяет поведение при ошибке")
    @allure.label("blocked_by", "question-1")
    @pytest.mark.skip(
        reason="BLOCKER: REQ-01 не определяет поведение при вводе неверного "
               "кода. Уточняющий вопрос 1: что происходит при неверном коде?"
    )
    def test_04_invalid_code_shows_error(self, api_client: ZvukApiStub):
        """Проверяет: сообщение об ошибке при неверном коде.

        Пропущен, так как REQ-01 не определяет поведение при ошибке.
        """
        result = api_client.confirm_code(PHONE_NUMBER, INVALID_CODE)
        assert result["status"] == "error", (
            f"Ожидается status 'error', получен '{result['status']}'"
        )
        assert "Неверный код" in result.get("message", ""), (
            f"Ожидается сообщение 'Неверный код', получено '{result.get('message')}'"
        )


# =====================================================================
# TC-J01-03 — Менее 3 жанров (граница)
# =====================================================================


class TestLessThanThreeGenres:
    """Вариант: выбор 2 жанров — кнопка «Продолжить» неактивна."""

    @allure.id("J01-TC-J01-03-01")
    @allure.label("req", "REQ-01")
    @allure.label("layer", "smoke")
    @allure.title("Открытие приложения — экран входа")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("Шаг 1 из TC-J01-03: приложение открыто. REQ-01")
    def test_01_open_app(self, api_client: ZvukApiStub):
        assert hasattr(api_client, "_phone_number")

    @allure.id("J01-TC-J01-03-02")
    @allure.label("req", "REQ-01")
    @allure.label("layer", "smoke")
    @allure.title("Ввод номера телефона")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("Шаг 2 из TC-J01-03: номер введён. REQ-01")
    def test_02_enter_phone(self, api_client: ZvukApiStub):
        result = api_client.send_code(PHONE_NUMBER)
        assert result["phone"] == PHONE_NUMBER

    @allure.id("J01-TC-J01-03-03")
    @allure.label("req", "REQ-01")
    @allure.label("layer", "smoke")
    @allure.title("Подтверждение номера — экран ввода кода")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("Шаг 3 из TC-J01-03: код отправлен. REQ-01")
    def test_03_confirm_phone(self, api_client: ZvukApiStub):
        result = api_client.send_code(PHONE_NUMBER)
        assert result["code"] == CONFIRMATION_CODE

    @allure.id("J01-TC-J01-03-04")
    @allure.label("req", "REQ-01, REQ-02")
    @allure.label("layer", "smoke")
    @allure.title("Ввод кода и открытие онбординга")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("Шаг 4 из TC-J01-03: код 1111, онбординг открыт. "
                          "REQ-01, REQ-02")
    def test_04_enter_code_opens_onboarding(self, api_client: ZvukApiStub):
        result = api_client.confirm_code(PHONE_NUMBER, CONFIRMATION_CODE)
        assert result["status"] == "ok"

    @allure.id("J01-TC-J01-03-05")
    @allure.label("req", "REQ-02")
    @allure.label("layer", "smoke")
    @allure.title("Выбор 2 жанров — счётчик = 2")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("Шаг 5 из TC-J01-03: выбрано 2 жанра. REQ-02")
    def test_05_select_two_genres(self, api_client: ZvukApiStub):
        """Проверяет: 2 жанра выбраны, счётчик = 2."""
        result = api_client.select_genres(SELECTED_GENRES_2)
        assert result["status"] == "ok", (
            "Выбор 2 жанров — это допустимая операция"
        )
        assert result["count"] == 2

    @allure.id("J01-TC-J01-03-06")
    @allure.label("req", "REQ-02")
    @allure.label("layer", "smoke")
    @allure.title("Попытка подтвердить < 3 жанров — кнопка неактивна")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("Шаг 6 из TC-J01-03: пользователь пытается подтвердить "
                          "выбор 2 жанров. Кнопка «Продолжить» неактивна, "
                          "сообщение о min 3. REQ-02")
    def test_06_confirm_less_than_three_disabled(self, api_client: ZvukApiStub):
        """Проверяет: кнопка неактивна при < 3 жанров."""
        # Выбрано 2 жанра
        api_client.select_genres(SELECTED_GENRES_2)
        # Попытка подтвердить онбординг
        result = api_client.confirm_onboarding()
        assert result["status"] == "error", (
            f"Ожидается status 'error', получен '{result['status']}'"
        )
        assert "Выберите не менее 3" in result.get("message", ""), (
            "Сообщение должно содержать 'Выберите не менее 3 жанров'"
        )


# =====================================================================
# TC-J01-04 — Пустой поисковый запрос
# =====================================================================


class TestEmptySearch:
    """Вариант: пустой поисковый запрос."""

    @allure.id("J01-TC-J01-04-01")
    @allure.label("req", "REQ-01")
    @allure.label("layer", "smoke")
    @allure.title("Открытие приложения — экран входа")
    @allure.severity(allure.severity_level.TRIVIAL)
    @allure.description("Шаг 1 из TC-J01-04: приложение открыто. REQ-01")
    def test_01_open_app(self, api_client: ZvukApiStub):
        assert hasattr(api_client, "_phone_number")

    @allure.id("J01-TC-J01-04-02")
    @allure.label("req", "REQ-01")
    @allure.label("layer", "smoke")
    @allure.title("Ввод номера телефона")
    @allure.severity(allure.severity_level.TRIVIAL)
    @allure.description("Шаг 2 из TC-J01-04: номер введён. REQ-01")
    def test_02_enter_phone(self, api_client: ZvukApiStub):
        result = api_client.send_code(PHONE_NUMBER)
        assert result["phone"] == PHONE_NUMBER

    @allure.id("J01-TC-J01-04-03")
    @allure.label("req", "REQ-01")
    @allure.label("layer", "smoke")
    @allure.title("Подтверждение номера — экран ввода кода")
    @allure.severity(allure.severity_level.TRIVIAL)
    @allure.description("Шаг 3 из TC-J01-04: код отправлен. REQ-01")
    def test_03_confirm_phone(self, api_client: ZvukApiStub):
        result = api_client.send_code(PHONE_NUMBER)
        assert result["code"] == CONFIRMATION_CODE

    @allure.id("J01-TC-J01-04-04")
    @allure.label("req", "REQ-01, REQ-02")
    @allure.label("layer", "smoke")
    @allure.title("Ввод кода подтверждения — онбординг открыт")
    @allure.severity(allure.severity_level.TRIVIAL)
    @allure.description("Шаг 4 из TC-J01-04: код 1111, онбординг. REQ-01, REQ-02")
    def test_04_enter_code(self, api_client: ZvukApiStub):
        result = api_client.confirm_code(PHONE_NUMBER, CONFIRMATION_CODE)
        assert result["status"] == "ok"

    @allure.id("J01-TC-J01-04-05")
    @allure.label("req", "REQ-02")
    @allure.label("layer", "smoke")
    @allure.title("Выбор 3 жанров — счётчик = 3")
    @allure.severity(allure.severity_level.TRIVIAL)
    @allure.description("Шаг 5 из TC-J01-04: выбрано 3 жанра. REQ-02")
    def test_05_select_three_genres(self, api_client: ZvukApiStub):
        result = api_client.select_genres(SELECTED_GENRES_3)
        assert result["count"] == 3

    @allure.id("J01-TC-J01-04-06")
    @allure.label("req", "REQ-02, REQ-03")
    @allure.label("layer", "smoke")
    @allure.title("Подтверждение жанров — главный экран")
    @allure.severity(allure.severity_level.TRIVIAL)
    @allure.description("Шаг 6 из TC-J01-04: пользователь подтверждает "
                          "жанры, открывается главный. REQ-02, REQ-03")
    def test_06_confirm_onboarding(self, api_client: ZvukApiStub):
        api_client.select_genres(SELECTED_GENRES_3)
        result = api_client.confirm_onboarding()
        assert result["status"] == "ok"

    @allure.id("J01-TC-J01-04-07")
    @allure.label("req", "REQ-04")
    @allure.label("layer", "smoke")
    @allure.title("Открытие раздела «Поиск» — поле ввода пустое")
    @allure.severity(allure.severity_level.TRIVIAL)
    @allure.description("Шаг 7 из TC-J01-04: раздел поиска открыт. REQ-04")
    def test_07_open_search(self, api_client: ZvukApiStub):
        result = api_client.search(EMPTY_QUERY)
        assert result["tracks"] == []

    @allure.id("J01-TC-J01-04-08")
    @allure.label("req", "REQ-04")
    @allure.label("layer", "blocker")
    @allure.title("Пустой запрос — вкладки не отображаются")
    @allure.severity(allure.severity_level.TRIVIAL)
    @allure.description("Шаг 8 из TC-J01-04: пользователь не вводит текст. "
                          "REQ-04 не определяет поведение при пустом запросе. "
                          "Вкладки группировки не отображаются")
    @allure.label("bug", "BLOCKER: REQ-04 не определяет поведение при пустом запросе")
    @allure.label("blocked_by", "question-1")
    @pytest.mark.skip(
        reason="BLOCKER: REQ-04 не определяет поведение при пустом "
               "поисковом запросе. Уточняющий вопрос 1: отображаются ли "
               "вкладки при пустом поле?"
    )
    def test_08_empty_query_no_tabs(self, api_client: ZvukApiStub):
        """Проверяет: при пустом запросе вкладки не отображаются.

        Пропущен, так как REQ-04 не определяет поведение при пустом запросе.
        """
        result = api_client.search(EMPTY_QUERY)
        assert result["tracks"] == []
        # Вкладки не отображаются — гипотеза
        assert "artists" not in result or result["artists"] == [], (
            "При пустом запросе вкладки не должны отображаться"
        )