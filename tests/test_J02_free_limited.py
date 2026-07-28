"""
Тесты для: J02-free-limited — Авторизация → Поиск → Воспроизведение (Free)
→ Выход → Повторный вход (Free) с тарифными ограничениями.

Основание: output/suites/J02-free-limited.md,
           output/cases/J02-free-limited/TC-J02-*.md + .json
"""

import pytest
import allure

from tests.helpers.test_data import (
    PHONE_NUMBER_FREE,
    SMS_CODE_VALID,
    SMS_CODE_INVALID,
    SEARCH_QUERY_VESNA,
    ARTIST_NAME_DOLPHIN,
    RECOMMENDATION_PLAYLIST,
    NONEXISTENT_SEARCH_QUERY,
    SKIP_LIMIT_COUNT,
)
from tests.helpers.api_stub import ZvukFreeApiStub


# =====================================================================
# TC-J02-00 — Основной счастливый путь Free
# =====================================================================


class TestTC_J02_00_MainHappyPath:
    """Основной путь: СМС-вход → Главная → Поиск → Заглушка →
    Исполнитель → Воспроизведение подборки → Лайк → Выход → Повторный вход."""

    @allure.id("J02-TC-J02-00-01")
    @allure.label("req", "REQ-15")
    @allure.label("layer", "e2e")
    @allure.title("Открытие приложения — экран входа с полем номера")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description(
        "Шаг 1 из TC-J02-00: пользователь открывает zvuk.sbrf.ru, "
        "видит экран входа с полем «Номер телефона». REQ-15"
    )
    def test_01_open_app_shows_login_screen(self, api_client: ZvukFreeApiStub):
        """Проверяет: приложение открыто, экран входа доступен."""
        # В заглушке проверяем, что клиент инициализирован
        assert hasattr(api_client, "_phone_number"), (
            "Ожидается, что клиент инициализирован"
        )

    @allure.id("J02-TC-J02-00-02")
    @allure.label("req", "REQ-15")
    @allure.label("layer", "e2e")
    @allure.title("Ввод номера телефона +7 999 000-00-22 — отправка СМС")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description(
        "Шаг 2 из TC-J02-00: пользователь вводит номер +7 999 000-00-22 "
        "в поле «Номер телефона», нажимает «Получить код». "
        "Кнопка заменяется на таймер 60 секунд. REQ-15"
    )
    def test_02_enter_phone_and_send_sms(self, api_client: ZvukFreeApiStub):
        """Проверяет: СМС отправлен, поле номера заполнено."""
        result = api_client.send_sms_code(PHONE_NUMBER_FREE)
        assert result["status"] == "ok", (
            f"Ожидается status 'ok', получен '{result['status']}'"
        )
        assert result["phone"] == PHONE_NUMBER_FREE, (
            f"Ожидается номер '{PHONE_NUMBER_FREE}', "
            f"получен '{result['phone']}'"
        )

    @allure.id("J02-TC-J02-00-03")
    @allure.label("req", "REQ-15")
    @allure.label("layer", "e2e")
    @allure.title("Ввод СМС-кода 111222 — вход выполнен, главная с рекомендациями")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description(
        "Шаг 3 из TC-J02-00: пользователь вводит 4-значный код 111222. "
        "После 4-й цифры — вход выполнен, открыта главная "
        "с блоками рекомендаций. REQ-15"
    )
    def test_03_enter_sms_code_and_login(self, api_client: ZvukFreeApiStub):
        """Проверяет: вход выполнен, главная страница с подборками."""
        result = api_client.confirm_sms_code(PHONE_NUMBER_FREE, SMS_CODE_VALID)
        assert result["status"] == "ok", (
            f"Ожидается status 'ok', получен '{result['status']}'"
        )
        assert result["session"] == "active", (
            "Сессия должна быть активна"
        )
        # Проверяем главную страницу
        main_page = api_client.get_main_page()
        assert main_page["screen"] == "main", (
            "Ожидается главная страница"
        )
        sections = main_page["sections"]
        assert any(
            s["title"] == "Рекомендации дня" for s in sections
        ), "Блок «Рекомендации дня» должен присутствовать на главной"

    @allure.id("J02-TC-J02-00-04")
    @allure.label("req", "REQ-03, REQ-17")
    @allure.label("layer", "e2e")
    @allure.title("Поиск трека «Весна» — заглушка «Доступно только с подпиской»")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description(
        "Шаг 4 из TC-J02-00: пользователь переходит в поиск, "
        "вводит запрос «Весна». Результаты: трек в разделе «Треки». "
        "При клике на трек — сообщение-заглушка "
        "«Доступно только с подпиской». REQ-03"
    )
    def test_04_search_vesna_shows_greylist(self, api_client: ZvukFreeApiStub):
        """Проверяет: результаты поиска видны, клик на трек — заглушка."""
        # Поиск трека
        search_result = api_client.search_track(SEARCH_QUERY_VESNA)
        assert search_result["play_button_blocked"], (
            "Кнопка воспроизведения трека должна быть заблокирована "
            "(play_button_blocked == True)"
        )
        # Клик на трек — заглушка
        click_result = api_client.click_track_free(SEARCH_QUERY_VESNA)
        assert click_result["status"] == "blocked", (
            f"Ожидается status 'blocked', получен '{click_result['status']}'"
        )
        assert "Доступно только с подпиской" in click_result.get("message", ""), (
            "Сообщение-заглушка должно содержать "
            "'Доступно только с подпиской'"
        )

    @allure.id("J02-TC-J02-00-05")
    @allure.label("req", "REQ-18")
    @allure.label("layer", "e2e")
    @allure.title("Страница исполнителя «Дельфин» — популярные треки и альбомы")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description(
        "Шаг 5 из TC-J02-00: пользователь нажимает на имя "
        "исполнителя «Дельфин». Открыта страница с популярными "
        "треками и альбомами. REQ-18"
    )
    def test_05_open_artist_page(self, api_client: ZvukFreeApiStub):
        """Проверяет: страница исполнителя отображает контент."""
        artist_page = api_client.get_artist_page(ARTIST_NAME_DOLPHIN)
        assert artist_page["artist"] == ARTIST_NAME_DOLPHIN, (
            f"Ожидается исполнитель '{ARTIST_NAME_DOLPHIN}', "
            f"получен '{artist_page['artist']}'"
        )
        assert len(artist_page["popular_tracks"]) > 0, (
            "Список популярных треков не должен быть пуст"
        )
        assert len(artist_page["albums"]) > 0, (
            "Список альбомов не должен быть пуст"
        )

    @allure.id("J02-TC-J02-00-06")
    @allure.label("req", "REQ-19, REQ-11")
    @allure.label("layer", "e2e")
    @allure.title("Воспроизведение подборки «Рекомендации дня» — плеер развёрнут")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description(
        "Шаг 6 из TC-J02-00: пользователь открывает вкладку "
        "«Главная», нажимает «Воспроизвести» на подборке "
        "«Рекомендации дня». Плеер развёрнут: обложка, "
        "название, исполнитель, таймлайн. REQ-19"
    )
    def test_06_play_from_playlist_opens_player(self, api_client: ZvukFreeApiStub):
        """Проверяет: плеер развёрнут, трек из подборки играет."""
        # Воспроизведение из подборки
        result = api_client.play_from_playlist(RECOMMENDATION_PLAYLIST)
        assert result["status"] == "playing", (
            f"Ожидается status 'playing', получен '{result['status']}'"
        )
        assert result["track"] == "Весна", (
            "Ожидается трек 'Весна' в плеере"
        )
        assert result["artist"] == "Дельфин", (
            "Ожидается исполнитель 'Дельфин'"
        )
        # Проверяем элементы плеера
        player_state = api_client.get_player_state()
        assert "cover" in player_state, (
            "Обложка должна отображаться в плеере"
        )
        assert "timeline" in player_state, (
            "Таймлайн должен отображаться в плеере"
        )

    @allure.id("J02-TC-J02-00-07")
    @allure.label("req", "REQ-20")
    @allure.label("layer", "e2e")
    @allure.title("Лайк трека — счётчик «Любимое» +1")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description(
        "Шаг 7 из TC-J02-00: пользователь нажимает кнопку "
        "«Сердечко» на играющем треке. Счётчик «Любимое» "
        "увеличивается на 1. REQ-20"
    )
    def test_07_like_track_increments_favorites(self, api_client: ZvukFreeApiStub):
        """Проверяет: лайк трека, счётчик +1."""
        # Предварительно открываем плеер
        api_client.play_from_playlist(RECOMMENDATION_PLAYLIST)
        # Лайкаем текущий трек
        like_result = api_client.like_track("Весна")
        assert like_result["status"] == "liked", (
            f"Ожидается status 'liked', получен '{like_result['status']}'"
        )
        assert like_result["liked"] is True, (
            "Кнопка лайка должна быть закрашена"
        )
        assert like_result["favorites_count"] == 1, (
            "Счётчик «Любимое» должен быть равен 1"
        )
        # Проверяем, что трек в списке
        assert "Весна" in like_result["favorites"], (
            "Трек 'Весна' должен быть в списке 'Мне нравится'"
        )

    @allure.id("J02-TC-J02-00-08")
    @allure.label("req", "REQ-28, REQ-30")
    @allure.label("layer", "e2e")
    @allure.title("Выход из аккаунта — сессия завершена, плеер остановлен")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description(
        "Шаг 8 из TC-J02-00: пользователь нажимает «Выход». "
        "Сессия завершена. Плеер остановлен. "
        "Персональные данные скрыты. REQ-28"
    )
    def test_08_logout_ends_session(self, api_client: ZvukFreeApiStub):
        """Проверяет: выход, сессия завершена."""
        result = api_client.logout()
        assert result["status"] == "logged_out", (
            f"Ожидается status 'logged_out', получен '{result['status']}'"
        )
        assert result["session"] == "ended", (
            "Сессия должна быть завершена"
        )
        assert result["player"] == "stopped", (
            "Плеер должен быть остановлен"
        )
        assert result["timeline"] == "0:00", (
            "Таймлайн должен быть на 0:00"
        )
        # Проверяем, что персональные данные скрыты
        main_page = api_client.get_main_page()
        assert main_page["screen"] == "public", (
            "После выхода должна отображаться публичная/стартовая страница, "
            "а не main"
        )

    @allure.id("J02-TC-J02-00-09")
    @allure.label("req", "REQ-29, REQ-24")
    @allure.label("layer", "e2e")
    @allure.title("Повторный вход — аккаунт Free восстановлен без очереди")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description(
        "Шаг 9 из TC-J02-00: пользователь повторно входит "
        "в аккаунт Free. «Моя музыка» и плейлисты сохранены. "
        "Очередь и позиция не восстановлены. REQ-29"
    )
    def test_09_second_login_restores_account_no_queue(
        self, api_client: ZvukFreeApiStub
    ):
        """Проверяет: повторный вход, библиотека сохранена,
        очередь не восстановлена."""
        # Перед повторным входом — выходим
        api_client.logout()
        # Повторный вход
        result = api_client.login_again(PHONE_NUMBER_FREE, SMS_CODE_VALID)
        assert result["status"] == "ok", (
            f"Ожидается status 'ok', получен '{result['status']}'"
        )
        # Проверяем, что библиотека и плейлисты сохранены
        restored = result.get("restored", {})
        assert "library" in restored, (
            "Библиотека должна быть восстановлена"
        )
        assert "favorites" in restored, (
            "Любимое должно быть восстановлено"
        )
        # Проверяем, что очередь и трек НЕ восстановлены
        not_restored = result.get("not_restored", {})
        assert not_restored.get("queue") == [], (
            "Очередь должна быть пуста (не восстановлена)"
        )
        assert not_restored.get("current_track") is None, (
            "Текущий трек не должен быть восстановлен"
        )
        assert not_restored.get("timeline") == "0:00", (
            "Таймлайн должен показывать 0:00"
        )


# =====================================================================
# TC-J02-01 — Неверный СМС-код
# =====================================================================


class TestTC_J02_01_InvalidSmsCode:
    """Вариант: ввод неверного СМС-кода — ошибка без входа."""

    @allure.id("J02-TC-J02-01-01")
    @allure.label("req", "REQ-26")
    @allure.label("layer", "smoke")
    @allure.title("Ввод неверного кода 0000 — сообщение об ошибке")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description(
        "Шаг 1 из TC-J02-01: пользователь вводит код 0000 "
        "(не существующий). Сервис показывает "
        "«Неверный код подтверждения». REQ-26"
    )
    def test_01_invalid_code_shows_error(self, api_client: ZvukFreeApiStub):
        """Проверяет: неверный код — ошибка, вход не выполнен."""
        # Отправляем запрос на СМС
        api_client.send_sms_code(PHONE_NUMBER_FREE)
        # Вводим неверный код
        result = api_client.confirm_sms_code(PHONE_NUMBER_FREE, SMS_CODE_INVALID)
        assert result["status"] == "error", (
            f"Ожидается status 'error', получен '{result['status']}'"
        )
        assert "Неверный код" in result.get("message", ""), (
            "Сообщение об ошибке должно содержать 'Неверный код'"
        )

    @allure.id("J02-TC-J02-01-02")
    @allure.label("req", "REQ-15")
    @allure.label("layer", "e2e")
    @allure.title("Ввод корректного кода 111222 — вход выполнен")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description(
        "Шаг 2 из TC-J02-01: после ошибочного кода пользователь "
        "вводит корректный 111222. Вход выполнен. REQ-15"
    )
    def test_02_correct_code_after_error(self, api_client: ZvukFreeApiStub):
        """Проверяет: после ошибки — корректный код позволяет войти."""
        # Сначала неверный код
        api_client.send_sms_code(PHONE_NUMBER_FREE)
        api_client.confirm_sms_code(PHONE_NUMBER_FREE, SMS_CODE_INVALID)
        # Затем верный
        result = api_client.confirm_sms_code(PHONE_NUMBER_FREE, SMS_CODE_VALID)
        assert result["status"] == "ok", (
            "После ввода верного кода должен быть успешный вход"
        )
        assert result["session"] == "active", (
            "Сессия должна быть активна"
        )


# =====================================================================
# TC-J02-02 — Поиск без результатов (Free)
# =====================================================================


class TestTC_J02_02_EmptySearch:
    """Вариант: поисковый запрос без результатов."""

    @allure.id("J02-TC-J02-02-01")
    @allure.label("req", "REQ-28")
    @allure.label("layer", "smoke")
    @allure.title("Поиск несуществующего запроса — пустой результат «Ничего не найдено»")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description(
        "Шаг 1 из TC-J02-02: пользователь вводит "
        "заведомо несуществующий запрос. "
        "Сервис показывает пустой результат "
        "с сообщением «По вашему запросу ничего не найдено». "
        "REQ-28"
    )
    def test_01_search_nonexistent_returns_empty(self, api_client: ZvukFreeApiStub):
        """Проверяет: пустой результат поиска."""
        result = api_client.search_track(NONEXISTENT_SEARCH_QUERY)
        assert result["tracks"] == [], (
            "Список треков должен быть пуст"
        )
        assert result["artists"] == [], (
            "Список исполнителей должен быть пуст"
        )
        # Проверяем сообщение
        assert "По вашему запросу ничего не найдено" in result.get(
            "message", ""
        ), (
            "Сообщение должно содержать "
            "'По вашему запросу ничего не найдено'"
        )


# =====================================================================
# TC-J02-03 — Достижение лимита пропусков (Free)
# =====================================================================


class TestTC_J02_03_SkipLimit:
    """Вариант: достижение лимита пропусков — кнопка «Далее» блокируется."""

    @allure.id("J02-TC-J02-03-01")
    @allure.label("req", "REQ-27, REQ-25")
    @allure.label("layer", "smoke")
    @allure.title("Нажатие «Далее» 5 раз — кнопка блокируется, трек доигрывает")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description(
        "Шаг 1 из TC-J02-03: пользователь нажимает "
        "«Далее» 5 раз. Кнопка «Далее» блокируется, "
        "трек продолжает играть до конца. "
        "Q-03: кнопка блокируется. REQ-27"
    )
    def test_01_skip_limit_reached_button_blocked(
        self, api_client: ZvukFreeApiStub
    ):
        """Проверяет: после 5 пропусков — кнопка 'Далее' блокируется."""
        # Сначала воспроизводим подборку
        api_client.play_from_playlist(RECOMMENDATION_PLAYLIST)

        # Нажимаем «Далее» 5 раз
        for i in range(SKIP_LIMIT_COUNT):
            result = api_client.skip_track()
            if i < SKIP_LIMIT_COUNT - 1:
                # До лимита — пропуск выполняется
                assert result["status"] == "skipped", (
                    f"На шаге {i + 1}: ожидается status 'skipped', "
                    f"получен '{result['status']}'"
                )
            else:
                # На последнем — лимит достигнут
                assert result["status"] == "blocked", (
                    f"На шаге {i + 1}: ожидается status 'blocked', "
                    f"получен '{result['status']}'"
                )
                assert result["track_continues"] is True, (
                    "Трек должен продолжать играть до конца, "
                    "а не прерываться"
                )

        # Финальная проверка состояния плеера
        player_state = api_client.get_player_state()
        assert player_state["skip_blocked"] is True, (
            "Поле skip_blocked должно быть True — кнопка 'Далее' "
            "заблокирована"
        )
        assert player_state["skip_count"] == SKIP_LIMIT_COUNT, (
            f"Счётчик пропусков должен быть равен {SKIP_LIMIT_COUNT}"
        )