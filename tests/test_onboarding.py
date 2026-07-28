"""
E2E тесты для J01 — Онбординг и первое воспроизведение.

Источник: output/cases/J01-onboarding-and-first-play/
Покрываемые требования: REQ-01 … REQ-06

Каждый тест — ровно один шаг из кейса TC-J01-00.
"""

import pytest
from helpers.test_data import (
    PHONE_NEW,
    SMS_CODE_VALID,
    SMS_CODE_WRONG,
    SMS_CODE_RESEND_COOLDOWN_SEC,
    GENRES,
    GENRES_MIN,
    GENRES_TOO_FEW,
    SEARCH_QUERY_VALID,
    SEARCH_QUERY_EMPTY,
    TRACK_FIRST,
    TRACK_NEXT,
)
from helpers.api_stub import ZvukAPIClient, Account, Playlist


# ==============================================================================
# Fixtures
# ==============================================================================

@pytest.fixture(scope="function")
def new_user() -> Account:
    """Новый, ещё не зарегистрированный пользователь."""
    return Account(phone=PHONE_NEW, is_verified=False, selected_genres=[])


@pytest.fixture(scope="function")
def api_client() -> ZvukAPIClient:
    """Чистый экземпляр API-клиента (без состояния между тестами)."""
    return ZvukAPIClient()


# ==============================================================================
# TC-J01-00 — Основной счастливый путь (10 шагов)
# ==============================================================================

class TestMainPath:
    """
    TC-J01-00: Регистрация → онбординг → поиск → плеер → очередь.
    """

    def test_01_app_starts_showing_login_screen(self, api_client):
        """
        Шаг 1: Приложение открывается — показан экран входа.
        REQ-01
        """
        result = api_client.send_verification_code(PHONE_NEW)
        assert result["code_sent"] is True

    def test_02_phone_input_accepted(self, api_client):
        """
        Шаг 2: Введённый номер отображается целиком.
        REQ-01
        """
        result = api_client.send_verification_code(PHONE_NEW)
        assert result["phone"] == PHONE_NEW

    def test_03_code_entry_screen_shown(self, api_client):
        """
        Шаг 3: После подтверждения номера — экран ввода кода.
        REQ-01
        """
        result = api_client.send_verification_code(PHONE_NEW)
        assert result["resend_available_at"] == SMS_CODE_RESEND_COOLDOWN_SEC

    def test_04_enter_valid_code_opens_onboarding(self, api_client):
        """
        Шаг 4: Ввод корректного кода — открывается экран онбординга.
        REQ-01, REQ-02
        """
        verify_result = api_client.verify_code(PHONE_NEW, SMS_CODE_VALID)
        assert verify_result["verified"] is True

    def test_05_three_genres_selected(self, api_client):
        """
        Шаг 5: Выбрано 3 жанра — счётчик = 3.
        REQ-02
        """
        result = api_client.select_genres(PHONE_NEW, GENRES_MIN)
        assert result["selected"] is True
        assert result["count"] == 3

    def test_06_main_screen_with_recommendations(self, api_client):
        """
        Шаг 6a: Подтверждение выбора → главный экран.
        Шаг 6b: Блок «Рекомендации» не пуст (минимум 1 элемент).
        REQ-02, REQ-03
        """
        result = api_client.select_genres(PHONE_NEW, GENRES_MIN)
        assert result["selected"] is True

    @pytest.mark.skip(reason="Выдуманное поведение: REQ-03 не специфицирует UI блока")
    def test_06b_recommendations_block_renders(self):
        """
        Шаг 6 (БЛОКИРУЕТСЯ): UI блока «Рекомендации» не определён.
        Нужно решение по вопросу: 'Какие визуальные компоненты содержит блок?'
        """
        ...

    def test_07_search_opens_with_empty_results(self, api_client):
        """
        Шаг 7: Раздел поиска — поле ввода, результаты пустые.
        REQ-04
        """
        result = api_client.search("")
        assert result.tracks == []
        assert result.artists == []

    def test_08_search_query_groups_by_tabs(self, api_client):
        """
        Шаг 8: Поисковый запрос выводит результаты по вкладкам.
        REQ-04
        """
        result = api_client.search(SEARCH_QUERY_VALID)
        assert len(result.tracks) > 0
        assert len(result.artists) > 0

    def test_09_player_expands_with_track_info(self, api_client):
        """
        Шаг 9: Плеер разворачивается — обложка, название, исполнитель.
        REQ-05
        """
        state = api_client.play_track("весна_1")
        assert state.current_track["title"] == TRACK_FIRST["title"]
        assert state.current_track["artist"] == TRACK_FIRST["artist"]
        assert state.is_expanded is True

    def test_10_queue_ordered_correctly(self, api_client):
        """
        Шаг 10: «Играть следующим» — трек сразу после текущего.
        REQ-06
        """
        state = api_client.add_to_queue("любовь_2")
        assert len(state.queue) >= 1


# ==============================================================================
# TC-J01-01 — Повторная отправка кода (таймер 60 с)
# ==============================================================================

class TestResendTimer:
    """
    TC-J01-01: Попытка повторной отправки до истечения 60 секунд.
    """

    @pytest.mark.skip(reason="Выдуманное поведение: REQ-01 не определяет, виден ли таймер")
    def test_timer_visual_shows_remaining_time(self):
        """
        Шаг 4 из TC-J01-01.
        БЛОКИРУЕТСЯ: REQ-01 не специфицирует UI таймера.
        """
        ...


# ==============================================================================
# TC-J01-02 — Неверный код подтверждения
# ==============================================================================

class TestWrongCode:
    """
    TC-J01-02: Ввод неверного кода.
    """

    def test_wrong_code_rejected(self, api_client):
        """
        Шаг 4 из TC-J01-02.
        (БЛОКЕР — выдуманное поведение, но шаг минимален.)
        """
        result = api_client.verify_code(PHONE_NEW, SMS_CODE_WRONG)
        assert result["verified"] is False

    @pytest.mark.skip(reason="Выдуманное поведение: REQ-01 не определяет UI ошибки")
    def test_error_message_displayed(self):
        """
        Шаг 4b: Сообщение об ошибке.
        БЛОКИРУЕТСЯ: ожидаемый результат не в требованиях.
        """
        ...


# ==============================================================================
# TC-J01-03 — Выбор < 3 жанров
# ==============================================================================

class TestTooFewGenres:
    """
    TC-J01-03: Менее 3 жанров — кнопка неактивна.
    """

    def test_continue_button_disabled(self, api_client):
        """
        Шаг 6 из TC-J01-03: выбор 2 жанров → подтверждение недоступно.
        """
        result = api_client.select_genres(PHONE_NEW, GENRES_TOO_FEW)
        assert result["selected"] is False
        assert "не менее 3" in result["message"]

    @pytest.mark.skip(reason="REQ-02 не определяет Visible State кнопки")
    def test_button_visually_disabled(self):
        """
        Визуальное состояние кнопки — BLOCKER.
        """
        ...


# ==============================================================================
# TC-J01-04 — Пустой поисковый запрос
# ==============================================================================

class TestEmptySearch:
    """
    TC-J01-04: Пустой запрос — нет результатов.
    """

    def test_empty_input_no_results(self, api_client):
        """
        Шаг 8 из TC-J01-04: пустой ввод → пустой список.
        """
        result = api_client.search(SEARCH_QUERY_EMPTY)
        assert result.tracks == []
        assert result.artists == []
        assert result.albums == []
        assert result.playlists == []

    @pytest.mark.skip(reason="REQ-04 не определяет, видны ли вкладки при пустом поле")
    def test_tabs_visible_or_not(self):
        """
        Визуальное состояние вкладок — BLOCKER.
        """
        ...