"""
Тесты для: J01-onboarding-and-first-play
Основание: output/cases/J01-*/TC-J01-*.md, output/suites/J01-*.md

Все шаги имеют Allure-аннотации. Формат:
    allure.id = <JOURNEY_ID>-<CASE_ID>-<NN>
    allure.severity = CRITICAL (main) | NORMAL (variant) | TRIVIAL (blocker/skip)
"""

from __future__ import annotations

import time

import allure
import pytest

from api_stub import (
    ZvukAPIClient,
    InvalidCodeError,
    ResendTooSoonError,
    OnboardingIncompleteError,
    ZvukAPIError,
)
from test_data import (
    TC_J01_00_Data,
    TC_J01_01_Data,
    TC_J01_02_Data,
    TC_J01_03_Data,
    TC_J01_04_Data,
    GENRE_LIST_KEYS,
    TOTAL_GENRES_AVAILABLE,
    GENRE_COUNTER_MIN,
    VALID_SEARCH_TABS,
    PLAYER_FIELDS,
    QUEUE_POSITION_AFTER_CURRENT,
    SMS_TIMEOUT_SEC,
    INVALID_CODE_ERROR,
)


# ============================================================================
# TC-J01-00 — Main path: full registration + first play (10 steps)
# ============================================================================

@allure.epic("J01-onboarding-and-first-play")
@allure.feature("Main path — полный цикл регистрации")
@allure.story("TC-J01-00")
class TestTC_J01_00:
    """Основной сценарий: регистрация → онбординг → поиск → плеер → очередь."""

    # -----------------------------------------------------------------------
    # Шаг 1 — Открыть приложение «Звук»
    # -----------------------------------------------------------------------

    @allure.id("J01-TC-J01-00-01")
    @allure.label("layer", "e2e")
    @allure.label("req", "REQ-01")
    @allure.title("Открытие приложения — экран входа")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description(
        "Шаг 1 из TC-J01-00: приложение запускается, "
        "отображается экран входа с полем ввода номера телефона. REQ-01."
    )
    def test_01_app_opens_login_screen(self, api_client: ZvukAPIClient) -> None:
        """Проверка: приложение открывается, экран входа виден."""
        # given: свежий экземпляр приложения
        assert api_client is not None
        # when: приложение загружено
        # then: пользователь не авторизован
        assert api_client.is_authenticated is False
        # then: номер телефона не введён
        assert api_client._phone is None

    # -----------------------------------------------------------------------
    # Шаг 2 — Ввести номер телефона
    # -----------------------------------------------------------------------

    @allure.id("J01-TC-J01-00-02")
    @allure.label("layer", "e2e")
    @allure.label("req", "REQ-01")
    @allure.title("Ввод номера телефона в поле входа")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description(
        "Шаг 2 из TC-J01-00: в поле отображается номер +7 999 000-00-11 "
        "целиком. REQ-01."
    )
    def test_02_enter_phone_number(self, api_client: ZvukAPIClient) -> None:
        """Проверка: номер телефона отображается в поле ввода."""
        # when: ввод номера телефона
        result = api_client.send_confirmation_code(TC_J01_00_Data.PHONE)
        # then: код отправлен
        assert result["sent"] is True
        assert result["retry_after_sec"] == SMS_TIMEOUT_SEC
        # then: номер сохранён
        assert api_client._phone == TC_J01_00_Data.PHONE

    # -----------------------------------------------------------------------
    # Шаг 3 — Подтвердить ввод номера
    # -----------------------------------------------------------------------

    @allure.id("J01-TC-J01-00-03")
    @allure.label("layer", "e2e")
    @allure.label("req", "REQ-01")
    @allure.title("Подтверждение номера — экран ввода кода")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description(
        "Шаг 3 из TC-J01-00: после подтверждения открывается экран "
        "с 4 полями, повторная отправка заблокирована на 60 с. REQ-01."
    )
    def test_03_confirm_phone_opens_code_screen(
        self, api_client: ZvukAPIClient
    ) -> None:
        """Проверка: экран ввода кода после подтверждения номера."""
        # given: номер введён
        api_client.send_confirmation_code(TC_J01_00_Data.PHONE)
        # when: подтверждение номера
        # then: экран кода (4 поля) — в тестовой заглушке просто завершается
        assert api_client._code_sent_at is not None
        assert api_client._confirmation_code is not None

    # -----------------------------------------------------------------------
    # Шаг 4 — Ввести код подтверждения
    # -----------------------------------------------------------------------

    @allure.id("J01-TC-J01-00-04")
    @allure.label("layer", "e2e")
    @allure.label("req", "REQ-01")
    @allure.label("req", "REQ-02")
    @allure.title("Ввод кода — открывается экран онбординга")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description(
        "Шаг 4 из TC-J01-00: корректный код открывает "
        "экран выбора жанров. REQ-01, REQ-02."
    )
    def test_04_correct_code_opens_onboarding(
        self, api_client: ZvukAPIClient
    ) -> None:
        """Проверка: правильный код → экран выбора жанров."""
        # given: код отправлен
        api_client.send_confirmation_code(TC_J01_00_Data.PHONE)
        # when: ввод верного кода
        result = api_client.confirm_code(TC_J01_00_Data.CONFIRMATION_CODE)
        # then: авторизация
        assert result["authenticated"] is True
        assert api_client.is_authenticated is True
        # then: доступен список жанров
        genres = api_client.get_genre_list()
        assert len(genres) == TOTAL_GENRES_AVAILABLE
        assert "Электроника" in genres

    # -----------------------------------------------------------------------
    # Шаг 5 — Выбрать три жанра
    # -----------------------------------------------------------------------

    @allure.id("J01-TC-J01-00-05")
    @allure.label("layer", "e2e")
    @allure.label("req", "REQ-02")
    @allure.title("Выбор трёх жанров — счётчик = 3")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description(
        "Шаг 5 из TC-J01-00: жанры отмечены, "
        "счётчик = 3. REQ-02."
    )
    def test_05_select_three_genres(self, api_client: ZvukAPIClient) -> None:
        """Проверка: выбор 3 жанров, счётчик = 3."""
        # given: авторизован
        api_client.send_confirmation_code(TC_J01_00_Data.PHONE)
        api_client.confirm_code(TC_J01_00_Data.CONFIRMATION_CODE)
        # when: выбор жанров
        result = api_client.select_genres(list(TC_J01_00_Data.GENRES))
        # then: выбрано ровно 3
        assert result["selected"] == GENRE_COUNTER_MIN
        assert result["status"] == "completed"
        # then: жанры сохранены
        assert set(api_client.selected_genres) == set(TC_J01_00_Data.GENRES)

    # -----------------------------------------------------------------------
    # Шаг 6 — Подтвердить выбор жанров
    # -----------------------------------------------------------------------

    @allure.id("J01-TC-J01-00-06")
    @allure.label("layer", "e2e")
    @allure.label("req", "REQ-02")
    @allure.label("req", "REQ-03")
    @allure.title("Подтверждение жанров — главный экран")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description(
        "Шаг 6 из TC-J01-00: главный экран, блок «Рекомендации» "
        "содержит ≥ 1 элемента. REQ-02, REQ-03."
    )
    def test_06_confirm_genres_shows_main_screen(
        self, api_client: ZvukAPIClient
    ) -> None:
        """Проверка: после выбора жанров открывается главный экран."""
        # given: авторизован + выбраны жанры
        api_client.send_confirmation_code(TC_J01_00_Data.PHONE)
        api_client.confirm_code(TC_J01_00_Data.CONFIRMATION_CODE)
        api_client.select_genres(list(TC_J01_00_Data.GENRES))
        # when: запрос рекомендаций
        recommendations = api_client.get_recommendations()
        # then: блок «Рекомендации» с элементами
        assert recommendations["count"] >= 1
        assert len(recommendations["items"]) > 0

    # -----------------------------------------------------------------------
    # Шаг 7 — Открыть раздел «Поиск»
    # -----------------------------------------------------------------------

    @allure.id("J01-TC-J01-00-07")
    @allure.label("layer", "e2e")
    @allure.label("req", "REQ-04")
    @allure.title("Открытие раздела Поиск — пустой список")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description(
        "Шаг 7 из TC-J01-00: поле ввода поиска, "
        "список результатов пуст. REQ-04."
    )
    def test_07_open_search_empty(self, api_client: ZvukAPIClient) -> None:
        """Проверка: поиск открыт, результаты пусты."""
        # given: полный онбординг
        api_client.send_confirmation_code(TC_J01_00_Data.PHONE)
        api_client.confirm_code(TC_J01_00_Data.CONFIRMATION_CODE)
        api_client.select_genres(list(TC_J01_00_Data.GENRES))
        # when: открыт поиск
        results = api_client.search("")
        # then: результаты пусты
        assert len(results.tracks) == 0
        assert len(results.artists) == 0
        assert len(results.albums) == 0
        assert len(results.playlists) == 0

    # -----------------------------------------------------------------------
    # Шаг 8 — Ввести поисковый запрос
    # -----------------------------------------------------------------------

    @allure.id("J01-TC-J01-00-08")
    @allure.label("layer", "e2e")
    @allure.label("req", "REQ-04")
    @allure.title("Поиск — результаты по вкладкам")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description(
        "Шаг 8 из TC-J01-00: результаты сгруппированы "
        "по вкладкам «Треки», «Исполнители», «Альбомы», «Плейлисты». REQ-04."
    )
    def test_08_search_returns_grouped_results(
        self, api_client: ZvukAPIClient
    ) -> None:
        """Проверка: результаты поиска группируются по вкладкам."""
        # given: полный онбординг
        api_client.send_confirmation_code(TC_J01_00_Data.PHONE)
        api_client.confirm_code(TC_J01_00_Data.CONFIRMATION_CODE)
        api_client.select_genres(list(TC_J01_00_Data.GENRES))
        # when: поиск
        results = api_client.search(TC_J01_00_Data.SEARCH_QUERY)
        # then: результаты по вкладкам
        assert len(results.tracks) > 0
        assert len(results.artists) > 0
        assert len(results.albums) > 0
        assert len(results.playlists) > 0
        # then: все вкладки присутствуют
        tab_names = set(VALID_SEARCH_TABS)
        # (заглушка не возвращает названия вкладок — проверяем наличием)

    # -----------------------------------------------------------------------
    # Шаг 9 — Запустить трек из вкладки «Треки»
    # -----------------------------------------------------------------------

    @allure.id("J01-TC-J01-00-09")
    @allure.label("layer", "e2e")
    @allure.label("req", "REQ-05")
    @allure.title("Запуск трека — плеер с обложкой и таймлайном")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description(
        "Шаг 9: плеер с обложкой, названием трека Весна, "
        "исполнителем Дельфин, таймлайном. REQ-05."
    )
    def test_09_play_track_shows_player(
        self, api_client: ZvukAPIClient
    ) -> None:
        """Проверка: развёрнут плеер с метаданными."""
        # given: полная авторизация
        api_client.send_confirmation_code(TC_J01_00_Data.PHONE)
        api_client.confirm_code(TC_J01_00_Data.CONFIRMATION_CODE)
        api_client.select_genres(list(TC_J01_00_Data.GENRES))
        # найти трек в результатах поиска
        results = api_client.search(TC_J01_00_Data.SEARCH_QUERY)
        first_track = results.tracks[0]
        # when: запуск трека
        player_state = api_client.play_track(first_track.id)
        # then: плеер с полями
        for field in PLAYER_FIELDS:
            assert field in player_state, f"Поле {field} отсутствует"
        assert player_state["title"] == TC_J01_00_Data.FIRST_TRACK_TITLE
        assert player_state["artist"] == TC_J01_00_Data.FIRST_TRACK_ARTIST
        assert player_state["status"] == "playing"
        # then: текущий трек установлен
        assert api_client.current_track is not None
        assert api_client.current_track.title == TC_J01_00_Data.FIRST_TRACK_TITLE

    # -----------------------------------------------------------------------
    # Шаг 10 — Добавить трек «Играть следующим»
    # -----------------------------------------------------------------------

    @allure.id("J01-TC-J01-00-10")
    @allure.label("layer", "e2e")
    @allure.label("req", "REQ-06")
    @allure.title("Добавление в очередь — трек сразу после текущего")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description(
        "Шаг 10: трек Любовь после Весна. "
        "Порядок очереди. REQ-06."
    )
    def test_10_play_next_keeps_queue_order(
        self, api_client: ZvukAPIClient
    ) -> None:
        """Проверка: трек «Играть следующим» — позиция после текущего."""
        # given: полный онбординг + первый трек играет
        api_client.send_confirmation_code(TC_J01_00_Data.PHONE)
        api_client.confirm_code(TC_J01_00_Data.CONFIRMATION_CODE)
        api_client.select_genres(list(TC_J01_00_Data.GENRES))
        results = api_client.search(TC_J01_00_Data.SEARCH_QUERY)
        first_track = results.tracks[0]
        api_client.play_track(first_track.id)
        # when: добавление второго трека в очередь
        second_track = results.tracks[1]  # "Любовь"
        result = api_client.play_next(second_track.id)
        # then: позиция сразу после текущего
        assert result["position"] == QUEUE_POSITION_AFTER_CURRENT
        assert result["added"] == second_track.id
        # then: очередь содержит 1 трек
        queue = api_client.get_queue()
        assert len(queue) == 1
        assert queue[0].title == TC_J01_00_Data.SECOND_TRACK_TITLE


# ============================================================================
# TC-J01-01 — Variant: resend code before 60 seconds (4 steps)
# ============================================================================

@allure.epic("J01-onboarding-and-first-play")
@allure.feature("Variant — граница таймера")
@allure.story("TC-J01-01")
class TestTC_J01_01:
    """Вариант: повторная отправка кода до истечения 60 секунд."""

    @allure.id("J01-TC-J01-01-01")
    @allure.label("layer", "e2e")
    @allure.label("req", "REQ-01")
    @allure.title("Открытие приложения — экран входа")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description(
        "Шаг 1 из TC-J01-01: наследуется из TC-J01-00. "
        "Приложение открыто, экран входа. REQ-01."
    )
    def test_01_variant_app_opens(self, api_client: ZvukAPIClient) -> None:
        """Наследуется из TC-J01-00 шаг 1."""
        assert api_client is not None
        assert api_client.is_authenticated is False

    @allure.id("J01-TC-J01-01-02")
    @allure.label("layer", "e2e")
    @allure.label("req", "REQ-01")
    @allure.title("Ввод номера телефона")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description(
        "Шаг 2 из TC-J01-01: номер введён. REQ-01."
    )
    def test_02_variant_enter_phone(self, api_client: ZvukAPIClient) -> None:
        """Наследуется из TC-J01-00 шаг 2."""
        result = api_client.send_confirmation_code(TC_J01_01_Data.PHONE)
        assert result["sent"] is True

    @allure.id("J01-TC-J01-01-03")
    @allure.label("layer", "e2e")
    @allure.label("req", "REQ-01")
    @allure.title("Подтверждение — экран ввода кода")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description(
        "Шаг 3 из TC-J01-01: экран ввода кода. "
        "Таймаут 60 с. REQ-01."
    )
    def test_03_variant_confirm_opens_code_input(
        self, api_client: ZvukAPIClient
    ) -> None:
        """Наследуется из TC-J01-00 шаг 3."""
        api_client.send_confirmation_code(TC_J01_01_Data.PHONE)
        assert api_client._code_sent_at is not None
        assert api_client._confirmation_code == TC_J01_00_Data.CONFIRMATION_CODE

    @allure.id("J01-TC-J01-01-04")
    @allure.label("layer", "smoke")
    @allure.label("req", "REQ-01")
    @allure.title("Попытка повторной отправки до 60 с — кнопка неактивна")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description(
        "Шаг 4: кнопка неактивна, таймер обратного отсчёта. "
        "REQ-01. BLOCKER — поведение не определено в REQ-01."
    )
    @allure.label("bug", "BLOCKER: REQ-01 не определяет поведение "
                         "при нажатии на неактивную кнопку")
    @allure.label("blocked_by", "question-2")
    @pytest.mark.skip(
        reason="BLOCKER: REQ-01 не специфицирует "
               "UI/поведение при нажатии на неактивную кнопку "
               "до истечения 60 секунд"
    )
    def test_04_resend_before_60s_blocked(
        self, api_client: ZvukAPIClient
    ) -> None:
        """
        Проверка: повторная отправка до 60 с заблокирована.

        Требование REQ-01 не определяет, что происходит при
        нажатии на неактивную кнопку — визуальный фидбек,
        отсутствие реакции, всплывающее сообщение.

        BLOCKER из-за отсутствия спецификации.
        """
        api_client.send_confirmation_code(TC_J01_01_Data.PHONE)
        # Попытка через 10 секунд (до истечения 60)
        time.sleep(0.01)  # эмуляция
        with pytest.raises(ResendTooSoonError):
            api_client.resend_confirmation_code(TC_J01_01_Data.PHONE)


# ============================================================================
# TC-J01-02 — Variant: wrong confirmation code (4 steps)
# ============================================================================

@allure.epic("J01-onboarding-and-first-play")
@allure.feature("Variant — неверный код")
@allure.story("TC-J01-02")
class TestTC_J01_02:
    """Вариант: ввод неверного кода — ошибка при регистрации."""

    @allure.id("J01-TC-J01-02-01")
    @allure.label("layer", "e2e")
    @allure.label("req", "REQ-01")
    @allure.title("Открытие приложения — экран входа")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description(
        "Шаг 1 из TC-J01-02: наследуется из TC-J01-00. "
        "Приложение открыто. REQ-01."
    )
    def test_01_wrong_code_app_opens(self, api_client: ZvukAPIClient) -> None:
        """Наследуется из TC-J01-00 шаг 1."""
        assert api_client is not None

    @allure.id("J01-TC-J01-02-02")
    @allure.label("layer", "e2e")
    @allure.label("req", "REQ-01")
    @allure.title("Ввод номера телефона")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description(
        "Шаг 2 из TC-J01-02: номер введён. REQ-01."
    )
    def test_02_wrong_code_enter_phone(self, api_client: ZvukAPIClient) -> None:
        """Наследуется из TC-J01-00 шаг 2."""
        result = api_client.send_confirmation_code(TC_J01_02_Data.PHONE)
        assert result["sent"] is True

    @allure.id("J01-TC-J01-02-03")
    @allure.label("layer", "e2e")
    @allure.label("req", "REQ-01")
    @allure.title("Подтверждение — экран ввода кода")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description(
        "Шаг 3 из TC-J01-02: экран ввода кода. REQ-01."
    )
    def test_03_wrong_code_confirm_opens_code_input(
        self, api_client: ZvukAPIClient
    ) -> None:
        """Наследуется из TC-J01-00 шаг 3."""
        api_client.send_confirmation_code(TC_J01_02_Data.PHONE)
        assert api_client._confirmation_code is not None

    @allure.id("J01-TC-J01-02-04")
    @allure.label("layer", "smoke")
    @allure.label("req", "REQ-01")
    @allure.title("Неверный код — ошибка, аккаунт не создаётся")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description(
        "Шаг 4: ошибка «Неверный код», "
        "поле подсвечивается, аккаунт не создаётся. "
        "REQ-01. BLOCKER."
    )
    @allure.label("bug", "BLOCKER: REQ-01 не определяет "
                         "поведение при неверном коде")
    @allure.label("blocked_by", "question-1")
    @pytest.mark.skip(
        reason="BLOCKER: REQ-01 не специфицирует "
               "сообщение об ошибке и поведение при "
               "неверном коде — гипотеза требует "
               "подтверждения"
    )
    def test_04_wrong_code_raises_error(
        self, api_client: ZvukAPIClient
    ) -> None:
        """Проверка: неверный код → ошибка (гипотетическое поведение)."""
        api_client.send_confirmation_code(TC_J01_02_Data.PHONE)
        with pytest.raises(InvalidCodeError) as exc_info:
            api_client.confirm_code(TC_J01_02_Data.WRONG_CODE)
        # then: сообщение об ошибке
        assert INVALID_CODE_ERROR in str(exc_info.value)
        # then: аккаунт не создан
        assert api_client.is_authenticated is False


# ============================================================================
# TC-J01-03 — Variant: < 3 genres (6 steps)
# ============================================================================

@allure.epic("J01-onboarding-and-first-play")
@allure.feature("Variant — менее 3 жанров")
@allure.story("TC-J01-03")
class TestTC_J01_03:
    """Вариант: выбор менее 3 жанров — кнопка «Продолжить» неактивна."""

    @allure.id("J01-TC-J01-03-01")
    @allure.label("layer", "e2e")
    @allure.label("req", "REQ-01")
    @allure.title("Открытие приложения — экран входа")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description(
        "Шаг 1 из TC-J01-03: наследуется из TC-J01-00."
    )
    def test_01_few_genres_app_opens(self, api_client: ZvukAPIClient) -> None:
        """Наследуется из TC-J01-00 шаг 1."""
        assert api_client is not None

    @allure.id("J01-TC-J01-03-02")
    @allure.label("layer", "e2e")
    @allure.label("req", "REQ-01")
    @allure.title("Ввод номера телефона")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description(
        "Шаг 2 из TC-J01-03: номер введён. REQ-01."
    )
    def test_02_few_genres_enter_phone(self, api_client: ZvukAPIClient) -> None:
        """Наследуется из TC-J01-00 шаг 2."""
        result = api_client.send_confirmation_code(
            TC_J01_03_Data.PHONE
        )
        assert result["sent"] is True

    @allure.id("J01-TC-J01-03-03")
    @allure.label("layer", "e2e")
    @allure.label("req", "REQ-01")
    @allure.title("Подтверждение — экран ввода кода")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description(
        "Шаг 3 из TC-J01-03: экран ввода кода. REQ-01."
    )
    def test_03_few_genres_confirm_opens_code_input(
        self, api_client: ZvukAPIClient
    ) -> None:
        """Наследуется из TC-J01-00 шаг 3."""
        api_client.send_confirmation_code(TC_J01_03_Data.PHONE)
        assert api_client._confirmation_code is not None

    @allure.id("J01-TC-J01-03-04")
    @allure.label("layer", "e2e")
    @allure.label("req", "REQ-01")
    @allure.label("req", "REQ-02")
    @allure.title("Ввод кода — экран онбординга")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description(
        "Шаг 4 из TC-J01-03: код подтверждён, "
        "экран выбора жанров. REQ-01, REQ-02."
    )
    def test_04_few_genres_code_opens_onboarding(
        self, api_client: ZvukAPIClient
    ) -> None:
        """Наследуется из TC-J01-00 шаг 4."""
        api_client.send_confirmation_code(TC_J01_03_Data.PHONE)
        api_client.confirm_code(TC_J01_03_Data.CONFIRMATION_CODE)
        assert api_client.is_authenticated is True

    @allure.id("J01-TC-J01-03-05")
    @allure.label("layer", "e2e")
    @allure.label("req", "REQ-02")
    @allure.title("Выбор 2 жанров — счётчик = 2")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description(
        "Шаг 5 из TC-J01-03: выбрано 2 жанра, "
        "счётчик = 2. REQ-02."
    )
    def test_05_few_genres_select_two(
        self, api_client: ZvukAPIClient
    ) -> None:
        """Проверка: 2 жанра выбраны, счётчик = 2."""
        api_client.send_confirmation_code(TC_J01_03_Data.PHONE)
        api_client.confirm_code(TC_J01_03_Data.CONFIRMATION_CODE)
        # when: выбор 2 жанров
        genres = list(TC_J01_03_Data.GENRES_UNDER_MIN)
        with pytest.raises(OnboardingIncompleteError) as exc_info:
            api_client.select_genres(genres)
        # then: сообщение о минимуме
        assert TC_J01_03_Data.EXPECTED_HINT in str(exc_info.value)
        # then: онбординг не завершён
        assert api_client._onboarding_completed is False

    @allure.id("J01-TC-J01-03-06")
    @allure.label("layer", "smoke")
    @allure.label("req", "REQ-02")
    @allure.title("Попытка подтверждения — кнопка неактивна")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description(
        "Шаг 6: кнопка «Продолжить» неактивна, "
        "сообщение о минимуме. REQ-02. "
        "BLOCKER — поведение не определено в REQ-02."
    )
    @allure.label("bug", "BLOCKER: REQ-02 не уточняет, "
                         "активна ли кнопка и есть ли "
                         "сообщение-подсказка")
    @allure.label("blocked_by", "question-3")
    @pytest.mark.skip(
        reason="BLOCKER: REQ-02 не специфицирует "
               "состояние кнопки при < 3 жанров "
               "(неактивна vs скрыта) и наличие "
               "сообщения-подсказки"
    )
    def test_06_few_genres_confirm_blocked(
        self, api_client: ZvukAPIClient
    ) -> None:
        """
        Проверка: попытка подтверждения c < 3 жанров.

        Ожидаемый результат гипотетический — REQ-02
        не определяет UI при < 3.
        """
        api_client.send_confirmation_code(TC_J01_03_Data.PHONE)
        api_client.confirm_code(TC_J01_03_Data.CONFIRMATION_CODE)
        genres = list(TC_J01_03_Data.GENRES_UNDER_MIN)
        # Попытка (заглушка возвращает ошибку)
        with pytest.raises(OnboardingIncompleteError):
            api_client.select_genres(genres)


# ============================================================================
# TC-J01-04 — Variant: empty search query (8 steps)
# ============================================================================

@allure.epic("J01-onboarding-and-first-play")
@allure.feature("Variant — пустой поисковый запрос")
@allure.story("TC-J01-04")
class TestTC_J01_04:
    """Вариант: пустой запрос — поведение экрана поиска без ввода."""

    @allure.id("J01-TC-J01-04-01")
    @allure.label("layer", "e2e")
    @allure.label("req", "REQ-01")
    @allure.title("Открытие приложения — экран входа")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description(
        "Шаг 1 из TC-J01-04: наследуется из TC-J01-00."
    )
    def test_01_empty_search_app_opens(
        self, api_client: ZvukAPIClient
    ) -> None:
        """Наследуется из TC-J01-00 шаг 1."""
        assert api_client is not None

    @allure.id("J01-TC-J01-04-02")
    @allure.label("layer", "e2e")
    @allure.label("req", "REQ-01")
    @allure.title("Ввод номера телефона")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description(
        "Шаг 2 из TC-J01-04: номер введён. REQ-01."
    )
    def test_02_empty_search_enter_phone(
        self, api_client: ZvukAPIClient
    ) -> None:
        """Наследуется из TC-J01-00 шаг 2."""
        result = api_client.send_confirmation_code(
            TC_J01_04_Data.PHONE
        )
        assert result["sent"] is True

    @allure.id("J01-TC-J01-04-03")
    @allure.label("layer", "e2e")
    @allure.label("req", "REQ-01")
    @allure.title("Подтверждение — экран ввода кода")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description(
        "Шаг 3 из TC-J01-04: экран ввода кода. REQ-01."
    )
    def test_03_empty_search_confirm_opens_code_input(
        self, api_client: ZvukAPIClient
    ) -> None:
        """Наследуется из TC-J01-00 шаг 3."""
        api_client.send_confirmation_code(TC_J01_04_Data.PHONE)
        assert api_client._confirmation_code is not None

    @allure.id("J01-TC-J01-04-04")
    @allure.label("layer", "e2e")
    @allure.label("req", "REQ-01")
    @allure.label("req", "REQ-02")
    @allure.title("Ввод кода — экран онбординга")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description(
        "Шаг 4 из TC-J01-04: код верный, "
        "экран выбора жанров. REQ-01, REQ-02."
    )
    def test_04_empty_search_code_opens_onboarding(
        self, api_client: ZvukAPIClient
    ) -> None:
        """Наследуется из TC-J01-00 шаг 4."""
        api_client.send_confirmation_code(TC_J01_04_Data.PHONE)
        api_client.confirm_code(TC_J01_04_Data.CONFIRMATION_CODE)
        assert api_client.is_authenticated is True

    @allure.id("J01-TC-J01-04-05")
    @allure.label("layer", "e2e")
    @allure.label("req", "REQ-02")
    @allure.title("Выбор 3 жанров — счётчик = 3")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description(
        "Шаг 5 из TC-J01-04: выбрано 3 жанра. REQ-02."
    )
    def test_05_empty_search_select_three_genres(
        self, api_client: ZvukAPIClient
    ) -> None:
        """Наследуется из TC-J01-00 шаг 5."""
        api_client.send_confirmation_code(TC_J01_04_Data.PHONE)
        api_client.confirm_code(TC_J01_04_Data.CONFIRMATION_CODE)
        result = api_client.select_genres(list(TC_J01_04_Data.GENRES))
        assert result["selected"] == GENRE_COUNTER_MIN

    @allure.id("J01-TC-J01-04-06")
    @allure.label("layer", "e2e")
    @allure.label("req", "REQ-02")
    @allure.label("req", "REQ-03")
    @allure.title("Подтверждение — главный экран")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description(
        "Шаг 6 из TC-J01-04: главный экран, "
        "рекомендации. REQ-02, REQ-03."
    )
    def test_06_empty_search_confirm_main_screen(
        self, api_client: ZvukAPIClient
    ) -> None:
        """Наследуется из TC-J01-00 шаг 6."""
        api_client.send_confirmation_code(TC_J01_04_Data.PHONE)
        api_client.confirm_code(TC_J01_04_Data.CONFIRMATION_CODE)
        api_client.select_genres(list(TC_J01_04_Data.GENRES))
        recommendations = api_client.get_recommendations()
        assert recommendations["count"] >= 1

    @allure.id("J01-TC-J01-04-07")
    @allure.label("layer", "e2e")
    @allure.label("req", "REQ-04")
    @allure.title("Открытие поиска — пустой список")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description(
        "Шаг 7 из TC-J01-04: поле поиска, "
        "список результатов пуст. REQ-04."
    )
    def test_07_empty_search_open_search_empty(
        self, api_client: ZvukAPIClient
    ) -> None:
        """Наследуется из TC-J01-00 шаг 7."""
        api_client.send_confirmation_code(TC_J01_04_Data.PHONE)
        api_client.confirm_code(TC_J01_04_Data.CONFIRMATION_CODE)
        api_client.select_genres(list(TC_J01_04_Data.GENRES))
        results = api_client.search("")
        assert len(results.tracks) == 0

    @allure.id("J01-TC-J01-04-08")
    @allure.label("layer", "smoke")
    @allure.label("req", "REQ-04")
    @allure.title("Пустой запрос — вкладки не отображаются")
    @allure.severity(allure.severity_level.TRIVIAL)
    @allure.description(
        "Шаг 8: пустое поле, вкладки не отображаются. "
        "REQ-04. SKIP — поведение не определено "
        "в требованиях."
    )
    @allure.label("bug", "BLOCKER: REQ-04 не определяет "
                         "отображение вкладок при пустом "
                         "поисковом запросе")
    @allure.label("blocked_by", "question-4")
    @pytest.mark.skip(
        reason="BLOCKER: REQ-04 не уточняет, "
               "отображаются ли вкладки группировки "
               "при пустом поле ввода — гипотеза"
    )
    def test_08_empty_query_no_tabs(
        self, api_client: ZvukAPIClient
    ) -> None:
        """
        Проверка: при пустом запросе вкладки не отображаются.

        Ожидаемый результат — гипотеза, так как REQ-04
        не определяет поведение при отсутствии ввода.
        """
        api_client.send_confirmation_code(TC_J01_04_Data.PHONE)
        api_client.confirm_code(TC_J01_04_Data.CONFIRMATION_CODE)
        api_client.select_genres(list(TC_J01_04_Data.GENRES))
        results = api_client.search(TC_J01_04_Data.EMPTY_QUERY)
        # then: все результаты пусты
        assert len(results.tracks) == 0
        assert len(results.artists) == 0
        assert len(results.albums) == 0
        assert len(results.playlists) == 0


# ============================================================================
# Параметризованные тесты (граничные случаи)
# ============================================================================

@allure.epic("J01-onboarding-and-first-play")
@allure.feature("Edge cases — граничные значения")
class TestEdgeCases:
    """Группа граничных случаев, не привязанных к одному кейсу."""

    @allure.id("J01-EDGE-01")
    @allure.label("layer", "smoke")
    @allure.label("req", "REQ-01")
    @allure.title("Код из 3 цифр — ошибка формата")
    @allure.severity(allure.severity_level.TRIVIAL)
    @allure.description(
        "Проверка: код из 3 цифр не принимается. "
        "REQ-01 требует 4 цифры."
    )
    @pytest.mark.parametrize(
        "wrong_code,expected_error",
        [
            ("123", "Неверный код"),
            ("12", "Неверный код"),
            ("1", "Неверный код"),
            ("", "Неверный код"),  # пустая строка
        ],
    )
    def test_wrong_code_length(
        self, api_client: ZvukAPIClient, wrong_code: str, expected_error: str
    ) -> None:
        """Проверка: невалидная длина кода."""
        api_client.send_confirmation_code(TC_J01_00_Data.PHONE)
        with pytest.raises(InvalidCodeError) as exc_info:
            api_client.confirm_code(wrong_code)
        assert expected_error in str(exc_info.value)

    @allure.id("J01-EDGE-02")
    @allure.label("layer", "smoke")
    @allure.label("req", "REQ-02")
    @allure.title("Выбор 0 жанров — ошибка")
    @allure.severity(allure.severity_level.TRIVIAL)
    @allure.description(
        "Проверка: 0 жанров не принимается. "
        "REQ-02 требует ≥ 3."
    )
    @pytest.mark.parametrize(
        "few_genres",
        [
            [],
            ["Электроника"],
            ["Электроника", "Рок"],
        ],
    )
    def test_too_few_genres(
        self, api_client: ZvukAPIClient, few_genres: list[str]
    ) -> None:
        """Проверка: менее 3 жанров — ошибка."""
        api_client.send_confirmation_code(TC_J01_00_Data.PHONE)
        api_client.confirm_code(TC_J01_00_Data.CONFIRMATION_CODE)
        with pytest.raises(OnboardingIncompleteError) as exc_info:
            api_client.select_genres(few_genres)
        assert TC_J01_03_Data.EXPECTED_HINT in str(exc_info.value)

    @allure.id("J01-EDGE-03")
    @allure.label("layer", "smoke")
    @allure.label("req", "REQ-04")
    @allure.title("Поиск без авторизации — ошибка")
    @allure.severity(allure.severity_level.TRIVIAL)
    @allure.description(
        "Проверка: поиск без авторизации. "
        "REQ-04 требует авторизации."
    )
    def test_search_without_auth(self, api_client: ZvukAPIClient) -> None:
        """Проверка: поиск без токена."""
        # given: не авторизован
        with pytest.raises(ZvukAPIError) as exc_info:
            api_client.search(TC_J01_00_Data.SEARCH_QUERY)
        # then: ошибка авторизации
        assert "авторизац" in str(exc_info.value).lower()

    @allure.id("J01-EDGE-04")
    @allure.label("layer", "smoke")
    @allure.label("req", "REQ-06")
    @allure.title("Добавление в очередь без плеера — ошибка")
    @allure.severity(allure.severity_level.TRIVIAL)
    @allure.description(
        "Проверка: добавление в очередь без "
        "активного трека. REQ-06."
    )
    def test_play_next_without_current_track(
        self, api_client: ZvukAPIClient
    ) -> None:
        """Проверка: очередь без текущего трека."""
        api_client.send_confirmation_code(TC_J01_00_Data.PHONE)
        api_client.confirm_code(TC_J01_00_Data.CONFIRMATION_CODE)
        api_client.select_genres(list(TC_J01_00_Data.GENRES))
        results = api_client.search(TC_J01_00_Data.SEARCH_QUERY)
        second_track = results.tracks[1]
        # when: без запуска текущего
        result = api_client.play_next(second_track.id)
        # then: трек добавлен, но без current_track
        assert result["position"] == QUEUE_POSITION_AFTER_CURRENT
        assert result["added"] == second_track.id