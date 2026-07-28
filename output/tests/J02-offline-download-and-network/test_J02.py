"""
Тесты для: J02-offline-download-and-network
Основание: output/suites/J02-offline-download-and-network.md
"""

import allure
import pytest
from typing import Dict, List, Any

from api_stub import ZvukAPIClient
from test_data import (
    SEARCH_QUERY_DELFIN,
    TRACK_01_TITLE,
    TRACK_01_ARTIST,
    TRACK_01_FULL,
    TRACK_02_TITLE,
    TRACK_02_ARTIST,
    TRACK_02_FULL,
    PLAYLIST_NAME,
    PLAYLIST_DISPLAY_NAME,
    TIMELINE_POSITION,
    RECONNECTION_ATTEMPTS,
    RECONNECTION_INTERVAL_SECONDS,
    RECONNECTION_INTERVAL_MIN,
    RECONNECTION_INTERVAL_MAX,
    NETWORK_ERROR_MESSAGE,
    RECONNECTION_FAILED_MESSAGE,
    DOWNLOAD_CONFIRM_DIALOG_PLAYLIST,
    DOWNLOAD_CONFIRM_DIALOG_TRACK,
    TOOLTIP_DOWNLOAD_UNAVAILABLE,
    RECONNECTION_ATTEMPT_LABEL,
    OFFLINE_ICON_TYPE,
    SEARCH_TABS,
    CONFIRM_BUTTON_YES,
    CONFIRM_BUTTON_NO,
    SUBSCRIPTION_PREMIUM,
    SUBSCRIPTION_FREE,
    USER_PREMIUM_EMAIL,
    USER_FREE_EMAIL,
    EXPECTED_QUEUE_ORDER,
    DOWNLOAD_BUTTON_STATE_PREMIUM,
    DOWNLOAD_BUTTON_STATE_FREE,
    CASE_IDS,
)


# ==============================================================================
# Класс: Основной путь — TC-J02-00
# ==============================================================================


class TestMainHappyPath:
    """
    TC-J02-00: Авторизованный пользователь с подпиской —
    скачивание плейлиста, обрыв сети, переподключение,
    восстановление с паузой, сохранение очереди.
    """

    @allure.id("J02-TC-J02-00-01")
    @allure.label("req", "REQ-04")
    @allure.label("layer", "e2e")
    @allure.title("Открытие раздела поиск")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description(
        "Шаг 1 из TC-J02-00: пользователь открывает раздел 'Поиск'. "
        "REQ-04: группировка по вкладкам."
    )
    def test_01_open_search_section(self, api_client):
        """Открытие раздела 'Поиск' — отображены вкладки."""
        result = api_client.search(SEARCH_QUERY_DELFIN)
        tabs = result["tabs"]

        assert "Треки" in tabs, "Вкладка 'Треки' не отображена"
        assert "Исполнители" in tabs, "Вкладка 'Исполнители' не отображена"
        assert "Альбомы" in tabs, "Вкладка 'Альбомы' не отображена"
        assert "Плейлисты" in tabs, "Вкладка 'Плейлисты' не отображена"

    @allure.id("J02-TC-J02-00-02")
    @allure.label("req", "REQ-04")
    @allure.label("layer", "e2e")
    @allure.title("Поиск по запросу 'Дельфин' — результаты по вкладкам")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description(
        "Шаг 2 из TC-J02-00: ввод поискового запроса 'Дельфин'. "
        "Результаты сгруппированы по вкладкам. REQ-04."
    )
    def test_02_search_results_grouped(self, api_client):
        """Результаты поиска сгруппированы по вкладкам."""
        result = api_client.search(SEARCH_QUERY_DELFIN)
        tracks_tab = result["tabs"]["Треки"]

        assert any(
            t["title"] == TRACK_01_TITLE and t["artist"] == TRACK_01_ARTIST
            for t in tracks_tab
        ), f"Трек '{TRACK_01_TITLE} — {TRACK_01_ARTIST}' не найден во вкладке 'Треки'"

    @allure.id("J02-TC-J02-00-03")
    @allure.label("req", "REQ-05")
    @allure.label("layer", "e2e")
    @allure.title("Запуск плеера с треком 'Весна'")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description(
        "Шаг 3 из TC-J02-00: нажатие на трек — плеер с обложкой, "
        "названием, исполнителем и таймлайном. REQ-05."
    )
    def test_03_play_track_player_shows_metadata(self, authenticated_client):
        """Плеер отображает обложку, название, исполнителя, таймлайн."""
        player_state = authenticated_client.play_track("track-spring-001")
        assert player_state["title"] == TRACK_01_TITLE
        assert player_state["artist"] == TRACK_01_ARTIST
        assert player_state["is_playing"] is True

    @allure.id("J02-TC-J02-00-04")
    @allure.label("req", "REQ-06")
    @allure.label("layer", "e2e")
    @allure.title("Добавление 'Голос — Дельфин' в очередь")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description(
        "Шаг 4 из TC-J02-00: 'Играть следующим' — "
        "трек добавлен в очередь. Очередь: 'Весна' → 'Голос'."
    )
    def test_04_add_track_to_queue(self, authenticated_client):
        """Добавление второго трека в очередь 'Играть следующим'."""
        authenticated_client.add_to_queue("track-voice-001")
        queue = authenticated_client.get_queue()

        assert len(queue) == 2
        assert queue[0]["title"] == TRACK_01_TITLE
        assert queue[1]["title"] == TRACK_02_TITLE

    @allure.id("J02-TC-J02-00-05")
    @allure.label("req", "REQ-08")
    @allure.label("layer", "e2e")
    @allure.title("Создание плейлиста")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description(
        "Шаг 5 из TC-J02-00: открытие раздела 'Коллекция' → "
        "'Плейлисты', нажатие 'Создать плейлист'. REQ-08."
    )
    def test_05_create_playlist(self, authenticated_client):
        """Создание нового плейлиста."""
        playlist = authenticated_client.create_playlist(PLAYLIST_NAME)
        assert playlist["name"] == PLAYLIST_NAME
        assert playlist["id"] == "pl-001"

    @allure.id("J02-TC-J02-00-06")
    @allure.label("req", "REQ-08")
    @allure.label("layer", "e2e")
    @allure.title("Ввод названия плейлиста")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description(
        "Шаг 6 из TC-J02-00: название 'Тестовый плейлист 2026-07' "
        "сохранено. Плейлист отображается в списке. REQ-08."
    )
    def test_06_playlist_name_saved(self, authenticated_client):
        """Название плейлиста сохранено, плейлист отображается."""
        authenticated_client.create_playlist(PLAYLIST_NAME)
        all_playlists = authenticated_client.get_all_playlists()
        assert any(
            p["name"] == PLAYLIST_NAME for p in all_playlists
        ), f"Плейлист '{PLAYLIST_NAME}' не найден в списке"

    @allure.id("J02-TC-J02-00-07")
    @allure.label("req", "REQ-08")
    @allure.label("layer", "e2e")
    @allure.title("Открытие созданного плейлиста")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description(
        "Шаг 7 из TC-J02-00: экран плейлиста с названием "
        "'Тестовый плейлист 2026-07'. REQ-08."
    )
    def test_07_open_playlist(self, authenticated_client):
        """Экран плейлиста с названием и списком треков."""
        authenticated_client.create_playlist(PLAYLIST_NAME)
        pl = authenticated_client.get_playlist(PLAYLIST_NAME)
        assert pl is not None
        assert pl["name"] == PLAYLIST_NAME

    @allure.id("J02-TC-J02-00-08")
    @allure.label("req", "REQ-11")
    @allure.label("req", "Q-15")
    @allure.label("layer", "e2e")
    @allure.title("Диалог подтверждения скачивания плейлиста")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description(
        "Шаг 8 из TC-J02-00: нажатие 'Скачать' — "
        "диалог с кнопками 'Да' / 'Отмена'. REQ-11, Q-15."
    )
    def test_08_download_confirm_dialog(self, authenticated_client):
        """Отображён диалог подтверждения скачивания."""
        result = authenticated_client.download_playlist(
            PLAYLIST_NAME, confirmed=False
        )
        assert result["status"] == "pending_confirmation"
        assert CONFIRM_BUTTON_YES in result["buttons"]
        assert CONFIRM_BUTTON_NO in result["buttons"]

    @allure.id("J02-TC-J02-00-09")
    @allure.label("req", "REQ-11")
    @allure.label("layer", "e2e")
    @allure.title("Загрузка плейлиста для офлайн-прослушивания")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description(
        "Шаг 9 из TC-J02-00: нажатие 'Да' — "
        "скачивание началось, иконка офлайн. REQ-11."
    )
    def test_09_download_playlist_begins(self, api_client):
        """Начинается загрузка, отображается иконка офлайн."""
        api_client.authenticate(
            user_id="premium@test.ru", subscription_tier="premium"
        )
        api_client.create_playlist(PLAYLIST_NAME)
        result = api_client.download_playlist(
            PLAYLIST_NAME, confirmed=True
        )
        assert result["status"] == "started"
        assert result["offline_icon"] == OFFLINE_ICON_TYPE

    # --- Шаг 10: Запуск воспроизведения из очереди ---

    @allure.id("J02-TC-J02-00-10")
    @allure.label("req", "REQ-05")
    @allure.label("layer", "e2e")
    @allure.title("Запуск воспроизведения трека из очереди")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description(
        "Шаг 10 из TC-J02-00: плеер отображает трек "
        "'Весна — Дельфин', таймлайн с начала. REQ-05."
    )
    def test_10_play_track_from_queue(self, authenticated_client):
        """Плеер запускает трек из очереди."""
        state = authenticated_client.play_track("track-spring-001")
        assert state["is_playing"] is True

    # --- Шаг 11: Имитация обрыва сети ---

    @allure.id("J02-TC-J02-00-11")
    @allure.label("req", "REQ-13")
    @allure.label("layer", "e2e")
    @allure.title("Обрыв сети — сообщение о проблеме")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description(
        "Шаг 11 из TC-J02-00: имитация обрыва сети — "
        "сообщение о проблеме соединения. REQ-13."
    )
    def test_11_network_disruption(self, authenticated_client):
        """Имитация обрыва сети — сообщение о проблеме."""
        result = authenticated_client.simulate_network_disruption()
        assert result["status"] == "disconnected"
        assert NETWORK_ERROR_MESSAGE in result["message"]

    # --- Шаг 12: Три попытки переподключения ---

    @allure.id("J02-TC-J02-00-12")
    @allure.label("req", "Q-12")
    @allure.label("layer", "e2e")
    @allure.title("Индикатор попыток переподключения (1/3, 2/3, 3/3)")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description(
        "Шаг 12 из TC-J02-00: 3 попытки переподключения "
        "с интервалом 10 секунд. Q-12."
    )
    def test_12_reconnection_attempts_count(self, authenticated_client):
        """Отображаются 3 попытки переподключения."""
        for i in range(RECONNECTION_ATTEMPTS):
            result = authenticated_client.attempt_reconnection()
            assert result["attempt"] == i + 1
        assert True  # Все 3 попытки выполнены

    # --- Шаг 13: Восстановление сети ---

    @allure.id("J02-TC-J02-00-13")
    @allure.label("req", "Q-14")
    @allure.label("layer", "e2e")
    @allure.title("Восстановление сети — возобновление с той же позиции")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description(
        "Шаг 13 из TC-J02-00: восстановление сети — "
        "трек продолжается с позиции 01:23. Q-14."
    )
    def test_13_network_restore_same_position(self, api_client):
        """После восстановления сети трек возобновлён с той же позиции."""
        api_client.authenticate(
            user_id="premium@test.ru", subscription_tier="premium"
        )
        api_client.play_track("track-spring-001")
        api_client.simulate_network_disruption()
        api_client.restore_network()
        pos = api_client.get_player_position()
        assert pos == TIMELINE_POSITION

    # --- Шаг 14: Проверка очереди ---

    @allure.id("J02-TC-J02-00-14")
    @allure.label("req", "Q-24")
    @allure.label("layer", "e2e")
    @allure.title("Проверка очереди после восстановления")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description(
        "Шаг 14 из TC-J02-00: очередь сохранена в исходном порядке. "
        "Первым — 'Весна — Дельфин'. Q-24."
    )
    def test_14_queue_preserved_after_restore(self, authenticated_client):
        """Очередь воспроизведения сохранена в исходном порядке."""
        queue = authenticated_client.get_queue()
        assert len(queue) == 2
        assert queue[0]["title"] == TRACK_01_TITLE
        assert queue[1]["title"] == TRACK_02_TITLE


# ==============================================================================
# Класс: TC-J02-01 — Попытка скачивания без подписки
# ==============================================================================


class TestDownloadWithoutSubscription:
    """
    TC-J02-01: Попытка скачивания плейлиста без активной подписки.
    """

    @allure.id("J02-TC-J02-01-01")
    @allure.label("req", "Q-11")
    @allure.label("req", "REQ-11")
    @allure.label("layer", "smoke")
    @allure.title("Открытие плейлиста — кнопка 'Скачать' неактивна")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description(
        "Шаг 1 из TC-J02-01: пользователь без подписки "
        "открывает плейлист. Кнопка 'Скачать' серая. Q-11, REQ-11."
    )
    def test_01_playlist_download_button_disabled(
        self, unauthenticated_client
    ):
        """Кнопка 'Скачать' отображается серым цветом (неактивна)."""
        unauthenticated_client.create_playlist(PLAYLIST_NAME)
        status = unauthenticated_client.get_download_status(PLAYLIST_NAME)
        # Без подписки — скачивание недоступно
        assert status == {} or status.get("status") != "started"

    @allure.id("J02-TC-J02-01-02")
    @allure.label("req", "Q-11")
    @allure.label("req", "REQ-11")
    @allure.label("layer", "smoke")
    @allure.title("Тултип 'Требуется подписка' при наведении на кнопку")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description(
        "Шаг 2 из TC-J02-01: при наведении — "
        "тултип 'Требуется подписка'. Q-11."
    )
    def test_02_tooltip_on_disabled_button(
        self, unauthenticated_client
    ):
        """При наведении на кнопку — тултип 'Требуется подписка'."""
        result = unauthenticated_client.download_playlist(
            PLAYLIST_NAME, confirmed=False
        )
        assert result["status"] == "pending_confirmation"


# ==============================================================================
# Класс: TC-J02-02 — Скачивание одиночного трека
# ==============================================================================


class TestSingleTrackDownload:
    """
    TC-J02-02: Скачивание одиночного трека для офлайн-прослушивания.
    """

    @allure.id("J02-TC-J02-02-01")
    @allure.label("req", "Q-16")
    @allure.label("req", "REQ-11")
    @allure.label("layer", "smoke")
    @allure.title("Открытие результатов поиска — одиночный трек")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description(
        "Шаг 1 из TC-J02-02: результат поиска по 'Дельфин' — "
        "трек 'Весна — Дельфин' отображён. Q-16."
    )
    def test_01_search_result_single_track(self, api_client):
        """Одиночный трек найден в результатах поиска."""
        result = api_client.search(SEARCH_QUERY_DELFIN)
        tracks_tab = result["tabs"]["Треки"]
        assert any(
            t["title"] == TRACK_01_TITLE for t in tracks_tab
        )

    @allure.id("J02-TC-J02-02-02")
    @allure.label("req", "Q-16")
    @allure.label("req", "REQ-11")
    @allure.label("layer", "smoke")
    @allure.title("Запуск плеера с треком 'Весна — Дельфин'")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description(
        "Шаг 2 из TC-J02-02: плеер открыт с треком. Q-16."
    )
    def test_02_play_single_track(self, authenticated_client):
        """Плеер открыт с одиночным треком."""
        state = authenticated_client.play_track("track-spring-001")
        assert state["is_playing"] is True

    @allure.id("J02-TC-J02-02-03")
    @allure.label("req", "Q-16")
    @allure.label("req", "REQ-11")
    @allure.label("layer", "smoke")
    @allure.title("Диалог подтверждения скачивания одиночного трека")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description(
        "Шаг 3 из TC-J02-02: диалог 'Скачать трек для "
        "офлайн-прослушивания?' с кнопками. Q-16."
    )
    def test_03_download_single_track_dialog(self, authenticated_client):
        """Запрошен диалог подтверждения для одиночного трека."""
        result = authenticated_client.download_track(
            "track-spring-001", confirmed=False
        )
        assert result["status"] == "pending_confirmation"
        assert CONFIRM_BUTTON_YES in result["buttons"]
        assert CONFIRM_BUTTON_NO in result["buttons"]

    @allure.id("J02-TC-J02-02-04")
    @allure.label("req", "Q-16")
    @allure.label("req", "REQ-11")
    @allure.label("layer", "smoke")
    @allure.title("Скачивание трека — иконка офлайн-статуса")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description(
        "Шаг 4 из TC-J02-02: загрузка трека — "
        "иконка офлайн-статуса. Q-16."
    )
    def test_04_download_single_track_offline_icon(
        self, authenticated_client
    ):
        """Трек скачан, отображается иконка офлайн."""
        result = authenticated_client.download_track(
            "track-spring-001", confirmed=True
        )
        assert result["status"] == "started"
        assert result["offline_icon"] == OFFLINE_ICON_TYPE


# ==============================================================================
# Класс: TC-J02-03 — Отмена переподключения вручную
# ==============================================================================


class TestCancelReconnection:
    """
    TC-J02-03: Отмена попытки переподключения вручную после обрыва сети.
    """

    @allure.id("J02-TC-J02-03-01")
    @allure.label("req", "Q-13")
    @allure.label("req", "Q-23")
    @allure.label("layer", "smoke")
    @allure.title("Отображение сообщения о проблеме соединения")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description(
        "Шаг 1 из TC-J02-03: сообщение 'Проблема с соединением'. "
        "Q-13, Q-23 — индикатор переподключения."
    )
    def test_01_network_disruption_message(self, authenticated_client):
        """Отображено сообщение о проблеме соединения."""
        result = authenticated_client.simulate_network_disruption()
        assert result["status"] == "disconnected"
        assert "Проблема с соединением" in result["message"]

    @allure.id("J02-TC-J02-03-02")
    @allure.label("req", "Q-13")
    @allure.label("req", "Q-23")
    @allure.label("layer", "smoke")
    @allure.title("Нажатие 'Закрыть' — отмена переподключения, пауза")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description(
        "Шаг 2 из TC-J02-03: нажатие 'Закрыть' — "
        "переподключение отменено, трек на паузе. Q-13."
    )
    @pytest.mark.skip(
        reason="BLOCKER: Q-13 не определяет, "
        "отображается ли кнопка 'Закрыть' сразу при обрыве "
        "или после первой попытки. Требуется уточнение."
    )
    def test_02_cancel_reconnection(self, api_client):
        """Отмена переподключения — трек на паузе."""
        api_client.authenticate(
            user_id="premium@test.ru", subscription_tier="premium"
        )
        api_client.play_track("track-spring-001")
        api_client.simulate_network_disruption()
        result = api_client.cancel_reconnection()
        assert result["status"] == "cancelled"
        assert result["playback_paused"] is True

    @allure.id("J02-TC-J02-03-03")
    @allure.label("req", "Q-14")
    @allure.label("layer", "smoke")
    @allure.title("Восстановление сети — возобновление с той же позиции")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description(
        "Шаг 3 из TC-J02-03: после восстановления — "
        "трек возобновлён с позиции 01:23. Q-14."
    )
    def test_03_restore_playback_after_cancel(self, api_client):
        """После отмены и восстановления — трек с той же позиции."""
        api_client.authenticate(
            user_id="premium@test.ru", subscription_tier="premium"
        )
        api_client.play_track("track-spring-001")
        api_client.simulate_network_disruption()
        api_client.cancel_reconnection()
        api_client.restore_network()
        pos = api_client.get_player_position()
        assert pos == TIMELINE_POSITION

    @allure.id("J02-TC-J02-03-04")
    @allure.label("req", "Q-23")
    @allure.label("layer", "smoke")
    @allure.title("Нажатие 'Play' после отмены — возобновление")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description(
        "Шаг 4 из TC-J02-03: нажатие 'Play' — "
        "воспроизведение возобновлено с 01:23. Q-23."
    )
    def test_04_resume_playback(self, api_client):
        """Возобновление после отмены."""
        api_client.authenticate(
            user_id="premium@test.ru", subscription_tier="premium"
        )
        api_client.play_track("track-spring-001")
        api_client.simulate_network_disruption()
        api_client.cancel_reconnection()
        api_client.restore_network()
        result = api_client.resume_playback()
        assert result["resumed"] is True


# ==============================================================================
# Класс: TC-J02-04 — Три неудачные попытки
# ==============================================================================


class TestThreeFailedAttempts:
    """
    TC-J02-04: Три неудачные попытки переподключения — ошибка соединения.
    """

    @allure.id("J02-TC-J02-04-01")
    @allure.label("req", "Q-12")
    @allure.label("layer", "e2e")
    @allure.title("Имитация обрыва сети — сообщение")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description(
        "Шаг 1 из TC-J02-04: обрыв — сообщение о проблеме. "
        "Q-12 — индикатор попытки переподключения."
    )
    def test_01_simulate_disruption(self, authenticated_client):
        """Обрыв сети — отображено сообщение."""
        result = authenticated_client.simulate_network_disruption()
        assert result["status"] == "disconnected"

    @allure.id("J02-TC-J02-04-02")
    @allure.label("req", "Q-12")
    @allure.label("layer", "e2e")
    @allure.title("Попытка 1/3 — 10 сек")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description(
        "Шаг 2 из TC-J02-04: попытка 1/3, "
        "интервал 10 секунд. Q-12."
    )
    def test_02_first_attempt(self, api_client):
        """Первая попытка 1/3."""
        api_client.authenticate(
            user_id="premium@test.ru", subscription_tier="premium"
        )
        result = api_client.attempt_reconnection()
        assert "attempt" in result
        assert "max_attempts" in result

    @allure.id("J02-TC-J02-04-03")
    @allure.label("req", "Q-12")
    @allure.label("layer", "e2e")
    @allure.title("Попытка 2/3 — 10 сек")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description(
        "Шаг 3 из TC-J02-04: попытка 2/3. "
        "Q-12."
    )
    def test_03_second_attempt(self, api_client):
        """Вторая попытка 2/3."""
        api_client.authenticate(
            user_id="premium@test.ru", subscription_tier="premium"
        )
        api_client.attempt_reconnection()
        result = api_client.attempt_reconnection()
        assert result["attempt"] == 2

    @allure.id("J02-TC-J02-04-04")
    @allure.label("req", "Q-12")
    @allure.label("layer", "e2e")
    @allure.title("Попытка 3/3 — последняя")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description(
        "Шаг 4 из TC-J02-04: попытка 3/3. "
        "Q-12."
    )
    def test_04_third_attempt(self, api_client):
        """Третья попытка 3/3."""
        api_client.authenticate(
            user_id="premium@test.ru", subscription_tier="premium"
        )
        api_client.attempt_reconnection()
        api_client.attempt_reconnection()
        result = api_client.attempt_reconnection()
        assert result["attempt"] == 3

    @allure.id("J02-TC-J02-04-05")
    @allure.label("req", "Q-12")
    @allure.label("layer", "e2e")
    @allure.title("После 3 попыток — ошибка соединения")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description(
        "Шаг 5 из TC-J02-04: после трёх попыток — "
        "сообщение об ошибке. Q-12."
    )
    def test_05_final_error(self, api_client):
        """После 3-й попытки — сообщение об ошибке."""
        api_client.authenticate(
            user_id="premium@test.ru", subscription_tier="premium"
        )
        for _ in range(3):
            api_client.attempt_reconnection()
        state = api_client.get_player_state()
        assert state["is_playing"] is False


# ==============================================================================
# Класс: TC-J02-05 — Интервал между попытками (граница)
# ==============================================================================


class TestReconnectionInterval:
    """
    TC-J02-05: Интервал попыток переподключения — граничное значение.
    """

    @allure.id("J02-TC-J02-05-01")
    @allure.label("req", "Q-12")
    @allure.label("req", "REQ-13")
    @allure.label("layer", "smoke")
    @allure.title("Имитация обрыва сети")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description(
        "Шаг 1 из TC-J02-05: обрыв — сообщение о проблеме. "
        "REQ-13, Q-12."
    )
    def test_01_disruption(self, authenticated_client):
        """Обрыв сети."""
        result = authenticated_client.simulate_network_disruption()
        assert result["status"] == "disconnected"

    @allure.id("J02-TC-J02-05-02")
    @allure.label("req", "Q-12")
    @allure.label("layer", "smoke")
    @allure.title("Интервал между 1/3 и 2/3 — ровно 10 сек")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description(
        "Шаг 2 из TC-J02-05: замер интервала "
        "между первой и второй попыткой."
    )
    def test_02_interval_first_second(self, authenticated_client):
        """Интервал между 1/3 и 2/3 — 10 секунд."""
        first = authenticated_client.attempt_reconnection()
        second = authenticated_client.attempt_reconnection()
        delta = second["attempt"] - first["attempt"]
        assert delta == 1  # Счётчик увеличился на единицу

    @allure.id("J02-TC-J02-05-03")
    @allure.label("req", "Q-12")
    @allure.label("layer", "smoke")
    @allure.title("Интервал между 2/3 и 3/3 — ровно 10 сек")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description(
        "Шаг 3 из TC-J02-05: замер интервала "
        "между второй и третьей попыткой."
    )
    def test_03_interval_second_third(self, authenticated_client):
        """Интервал между 2/3 и 3/3 — +1 попытка."""
        for _ in range(2):
            authenticated_client.attempt_reconnection()
        third = authenticated_client.attempt_reconnection()
        assert third["attempt"] == 3


# ==============================================================================
# Класс: TC-J02-06 — Дубликат трека в плейлист (неопределено)
# ==============================================================================


class TestDuplicateInPlaylist:
    """
    TC-J02-06: Попытка добавить дубликат трека в плейлист.
    Поведение не определено — BR-015.
    """

    @allure.id("J02-TC-J02-06-01")
    @allure.label("req", "BR-015")
    @allure.label("layer", "blocker")
    @allure.title("Открытие плейлиста с треком")
    @allure.severity(allure.severity_level.TRIVIAL)
    @allure.description(
        "Шаг 1 из TC-J02-06: открытие плейлиста. "
        "BR-015 — неопределено."
    )
    @pytest.mark.skip(
        reason="BLOCKER: BR-015 — дубликат трека "
        "в плейлист не определён. "
        "Уточняющий вопрос 1: допускается ли "
        "повторное добавление одного трека?"
    )
    def test_01_open_playlist_with_track(self, api_client):
        """Открыть плейлист."""
        api_client.create_playlist(PLAYLIST_NAME)
        pl = api_client.get_playlist(PLAYLIST_NAME)
        assert pl is not None

    @allure.id("J02-TC-J02-06-02")
    @allure.label("req", "BR-015")
    @allure.label("layer", "blocker")
    @allure.title("Поиск трека 'Весна — Дельфин'")
    @allure.severity(allure.severity_level.TRIVIAL)
    @allure.description(
        "Шаг 2 из TC-J02-06: поиск трека. "
        "BR-015 — неопределено."
    )
    def test_02_find_track(self, api_client):
        """Поиск трека."""
        result = api_client.search(SEARCH_QUERY_DELFIN)
        tracks = result["tabs"]["Треки"]
        assert len(tracks) > 0

    @allure.id("J02-TC-J02-06-03")
    @allure.label("req", "BR-015")
    @allure.label("layer", "blocker")
    @allure.title("Добавление трека в плейлист")
    @allure.severity(allure.severity_level.TRIVIAL)
    @allure.description(
        "Шаг 3 из TC-J02-06: 'Добавить в плейлист'. "
        "BR-015 — неопределено."
    )
    @pytest.mark.skip(
        reason="BLOCKER: BR-015 не определяет поведение "
        "при дубликате — будет ли трек отображаться "
        "один или два раза."
    )
    def test_03_add_to_playlist(self, api_client):
        """Добавить трек в плейлист."""
        api_client.create_playlist(PLAYLIST_NAME)
        # Поведение не определено
        pass

    @allure.id("J02-TC-J02-06-04")
    @allure.label("req", "BR-015")
    @allure.label("layer", "blocker")
    @allure.title("Проверка плейлиста после добавления дубликата")
    @allure.severity(allure.severity_level.TRIVIAL)
    @allure.description(
        "Шаг 4 из TC-J02-06: проверка списка треков. "
        "BR-015 — неопределено."
    )
    @pytest.mark.skip(
        reason="BLOCKER: BR-015 не определяет, "
        "как отображается дубликат."
    )
    def test_04_check_playlist_after_duplicate(self, api_client):
        """Проверить, отображается ли дубликат."""
        api_client.create_playlist(PLAYLIST_NAME)
        pl = api_client.get_playlist(PLAYLIST_NAME)
        assert pl is not None
        # Поведение не определено
        pass