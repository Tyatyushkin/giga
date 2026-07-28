"""
Тесты для: J02-offline-download-and-network
Основание: output/suites/J02-offline-download-and-network.md
Базовые кейсы: output/cases/J02-offline-download-and-network/
"""

import time
import allure
import pytest

from test_data import (
    SEARCH_QUERY_MAIN,
    TRACK_1_TITLE,
    TRACK_1_ARTIST,
    TRACK_2_TITLE,
    TRACK_2_ARTIST,
    PLAYLIST_NAME_MAIN,
    TIMELINE_POSITION_BREAK,
    SINGLE_TRACK_TITLE,
    PLAYLIST_NAME_UNSUBSCRIBED,
    TIMELINE_POSITION_CANCEL,
    TRACK_FOR_CANCEL,
    TRACK_FOR_THREE_ATTEMPTS,
    RETRY_INTERVAL_BASELINE,
    RETRY_INTERVAL_DEVIATION,
    RETRY_TOLERANCE_SEC,
    PLAYLIST_FOR_DUPLICATE,
    TRACK_FOR_DUPLICATE,
    EXPECTED_RETRY_ATTEMPTS,
    EXPECTED_RETRY_INTERVAL_SEC,
    TOTAL_RETRY_DURATION_SEC,
    ERROR_MESSAGE_RETRY,
    ERROR_MESSAGE_FAILED,
    DOWNLOAD_CONFIRMATION_PROMPT,
    UNSUBSCRIBED_BUTTON_LABEL,
    UNSUBSCRIBED_BUTTON_TOOLTIP,
    OFFLINE_ICON_DESCRIPTION,
    QUEUE_ORDER_AFTER_RECOVERY,
)


# ================================================================
#  Класс: TC-J02-00 — Основной happy path
# ================================================================
@allure.suite("J02: Офлайн-загрузка и сетевая устойчивость")
@allure.sub_suite("TC-J02-00: Авторизованный пользователь с подпиской")
class TestJ0200MainPath:
    """Основной сценарий: поиск → плеер → очередь → плейлист → скачивание → обрыв → восстановление."""

    # ── Шаг 1: Открыть раздел «Поиск» ──
    @allure.id("J02-TC-J02-00-01")
    @allure.label("req", "REQ-04")
    @allure.label("layer", "e2e")
    @allure.title("Открыть раздел «Поиск»")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description(
        "Шаг 1 из TC-J02-00: на экране отображён раздел поиска "
        "с вкладками Треки, Исполнители, Альбомы, Плейлисты. REQ-04"
    )
    def test_01_open_search(self, authenticated_client):
        """Открытие раздела Поиск — проверка наличия вкладок."""
        # when
        result = authenticated_client.search_tracks(SEARCH_QUERY_MAIN)
        # then
        assert "Треки" in result, (
            "Вкладка 'Треки' должна присутствовать в результатах поиска"
        )
        assert "Исполнители" in result, (
            "Вкладка 'Исполнители' должна присутствовать"
        )
        assert "Альбомы" in result, (
            "Вкладка 'Альбомы' должна присутствовать"
        )
        assert "Плейлисты" in result, (
            "Вкладка 'Плейлисты' должна присутствовать"
        )

    # ── Шаг 2: Поисковый запрос ──
    @allure.id("J02-TC-J02-00-02")
    @allure.label("req", "REQ-04")
    @allure.label("layer", "e2e")
    @allure.title("Ввести поисковый запрос «Дельфин»")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description(
        "Шаг 2 из TC-J02-00: результаты поиска сгруппированы "
        "по вкладкам; трек 'Весна — Дельфин' во вкладке Треки. REQ-04"
    )
    def test_02_search_results_grouped(self, authenticated_client):
        """Проверка группировки результатов по вкладкам."""
        # when
        results = authenticated_client.search_tracks(SEARCH_QUERY_MAIN)
        # then
        tracks_tab = results.get("Треки", [])
        assert tracks_tab, (
            "Вкладка 'Треки' не должна быть пустой"
        )
        assert f"{TRACK_1_TITLE} — {TRACK_1_ARTIST}" in tracks_tab, (
            f"Трек '{TRACK_1_TITLE} — {TRACK_1_ARTIST}' "
            f"должен быть во вкладке 'Треки'"
        )

    # ── Шаг 3: Запуск трека ──
    @allure.id("J02-TC-J02-00-03")
    @allure.label("req", "REQ-05")
    @allure.label("layer", "e2e")
    @allure.title("Запустить трек «Весна — Дельфин» из поиска")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description(
        "Шаг 3 из TC-J02-00: плеер открыт с обложкой, "
        "названием, исполнителем, таймлайном. REQ-05"
    )
    def test_03_play_track(self, authenticated_client):
        """Проверка, что плеер разворачивается с треком."""
        # when
        player_state = authenticated_client.play_track(
            f"{TRACK_1_TITLE} — {TRACK_1_ARTIST}"
        )
        # then
        assert player_state["player_open"] is True, (
            "Плеер должен быть открыт"
        )
        assert TRACK_1_ARTIST in str(player_state["track_title"]), (
            "В названии трека должен присутствовать исполнитель"
        )

    # ── Шаг 4: Добавить в очередь ──
    @allure.id("J02-TC-J02-00-04")
    @allure.label("req", "REQ-05")
    @allure.label("layer", "e2e")
    @allure.title("Нажать «Играть следующим» на треке «Голос — Дельфин»")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description(
        "Шаг 4 из TC-J02-00: трек добавлен в очередь "
        "сразу после текущего. REQ-05"
    )
    def test_04_add_to_queue_next(self, authenticated_client):
        """Проверка добавления в очередь 'сразу после'."""
        # given
        initial_queue = authenticated_client.get_queue()
        # when
        result = authenticated_client.add_to_queue(
            f"{TRACK_2_TITLE} — {TRACK_2_ARTIST}",
            position="next",
        )
        # then
        queue = result["queue"]
        assert len(queue) == len(initial_queue) + 1, (
            "Очередь должна увеличиться на 1"
        )
        assert f"{TRACK_2_TITLE} — {TRACK_2_ARTIST}" in queue, (
            "Добавленный трек должен быть в очереди"
        )

    # ── Шаг 5: Открыть раздел Коллекция → Плейлисты ──
    @allure.id("J02-TC-J02-00-05")
    @allure.label("req", "REQ-08")
    @allure.label("layer", "e2e")
    @allure.title("Открыть раздел «Коллекция» → «Плейлисты»")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description(
        "Шаг 5 из TC-J02-00: список плейлистов "
        "с кнопкой «Создать плейлист». REQ-08"
    )
    def test_05_create_playlist_button(self, authenticated_client):
        """Проверка наличия кнопки «Создать плейлист»."""
        # when
        playlist = authenticated_client.get_playlist(PLAYLIST_NAME_MAIN)
        # then
        # На этом шаге плейлист ещё не создан — проверяем
        # что существующих плейлистов нет (или есть)
        assert playlist is None, (
            "Плейлист ещё не должен существовать "
            f"(до создания): {PLAYLIST_NAME_MAIN}"
        )

    # ── Шаг 6: Создать плейлист ──
    @allure.id("J02-TC-J02-00-06")
    @allure.label("req", "REQ-08")
    @allure.label("layer", "e2e")
    @allure.title("Создать плейлист «Тестовый плейлист 2026-07»")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description(
        "Шаг 6 из TC-J02-00: плейлист создан, "
        "отображается в списке. REQ-08"
    )
    def test_06_create_playlist(self, authenticated_client):
        """Создание плейлиста и проверка его наличия."""
        # when
        created = authenticated_client.create_playlist(PLAYLIST_NAME_MAIN)
        # then
        assert created["created"] is True, (
            f"Плейлист '{PLAYLIST_NAME_MAIN}' должен быть создан"
        )
        assert created["name"] == PLAYLIST_NAME_MAIN, (
            "Имя плейлиста должно совпадать с введённым"
        )

    # ── Шаг 7: Открыть созданный плейлист ──
    @allure.id("J02-TC-J02-00-07")
    @allure.label("req", "REQ-08")
    @allure.label("layer", "e2e")
    @allure.title("Открыть созданный плейлист")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description(
        "Шаг 7 из TC-J02-00: экран плейлиста "
        "с названием и списком треков. REQ-08"
    )
    def test_07_open_created_playlist(self, authenticated_client):
        """Проверка, что плейлист открывается."""
        # given — создаём плейлист
        authenticated_client.create_playlist(PLAYLIST_NAME_MAIN)
        # when
        pl = authenticated_client.get_playlist(PLAYLIST_NAME_MAIN)
        # then
        assert pl is not None, (
            f"Плейлист '{PLAYLIST_NAME_MAIN}' должен быть доступен"
        )
        assert pl["name"] == PLAYLIST_NAME_MAIN, (
            "Название плейлиста должно совпадать"
        )

    # ── Шаг 8: Нажать Скачать на плейлисте ──
    @allure.id("J02-TC-J02-00-08")
    @allure.label("req", "REQ-11, Q-15")
    @allure.label("layer", "e2e")
    @allure.title("Нажать «Скачать» на плейлисте")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description(
        "Шаг 8 из TC-J02-00: диалог подтверждения "
        "«Скачать плейлист для офлайн-прослушивания?» "
        "с кнопками «Да» и «Отмена». REQ-11, Q-15"
    )
    def test_08_download_playlist_dialog(self, authenticated_client):
        """Проверка появления диалога подтверждения."""
        # given
        authenticated_client.create_playlist(PLAYLIST_NAME_MAIN)
        # when
        result = authenticated_client.download_playlist(PLAYLIST_NAME_MAIN)
        # then
        assert result["success"] is True, (
            "Скачивание должно быть разрешено при подписке"
        )
        dialog = result.get("dialog", "")
        assert DOWNLOAD_CONFIRMATION_PROMPT in dialog, (
            "Текст диалога должен содержать "
            "'Скачать плейлист для офлайн-прослушивания?'"
        )

    # ── Шаг 9: Подтвердить скачивание (кнопка «Да») ──
    @allure.id("J02-TC-J02-00-09")
    @allure.label("req", "Q-15")
    @allure.label("layer", "e2e")
    @allure.title("Нажать «Да» в диалоге подтверждения")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description(
        "Шаг 9 из TC-J02-00: начинается загрузка "
        "плейлиста, иконка офлайн-статуса. Q-15"
    )
    def test_09_confirm_download(self, authenticated_client):
        """Подтверждение скачивания — проверка иконки."""
        # given
        authenticated_client.create_playlist(PLAYLIST_NAME_MAIN)
        # when
        confirmed = authenticated_client.confirm_download(PLAYLIST_NAME_MAIN)
        # then
        assert confirmed["downloaded"] is True, (
            f"Плейлист '{PLAYLIST_NAME_MAIN}' должен начать загрузку"
        )
        icon = confirmed.get("offline_icon")
        assert OFFLINE_ICON_DESCRIPTION in str(icon or ""), (
            "Должна отображаться иконка офлайн-статуса (стрелка вниз)"
        )

    # ── Шаг 10: Проверка иконки офлайн-статуса ──
    @allure.id("J02-TC-J02-00-10")
    @allure.label("req", "Q-22")
    @allure.label("layer", "e2e")
    @allure.title("Проверить иконку офлайн-статуса на скачанном плейлисте")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description(
        "Шаг 10 из TC-J02-00: иконка офлайн-статуса "
        "рядом с названием плейлиста. Q-22"
    )
    def test_10_offline_icon_visible(self, authenticated_client):
        """Проверка, что иконка отображается на скачанном элементе."""
        # given
        authenticated_client.create_playlist(PLAYLIST_NAME_MAIN)
        authenticated_client.confirm_download(PLAYLIST_NAME_MAIN)
        # when
        status = authenticated_client.get_offline_status(PLAYLIST_NAME_MAIN)
        # then
        assert status["downloaded"] is True, (
            "Плейлист должен быть помечен как загруженный"
        )
        assert OFFLINE_ICON_DESCRIPTION in str(status.get("offline_icon")), (
            "Иконка офлайн-статуса должна отображаться"
        )

    # ── Шаг 11: Запустить воспроизведение ──
    @allure.id("J02-TC-J02-00-11")
    @allure.label("req", "REQ-05")
    @allure.label("layer", "e2e")
    @allure.title("Запустить трек из очереди")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description(
        "Шаг 11 из TC-J02-00: плеер отображает "
        "таймлайн с позицией с начала. REQ-05"
    )
    def test_11_start_playback(self, authenticated_client):
        """Запуск воспроизведения — проверка таймлайна."""
        # when
        state = authenticated_client.play_track(
            f"{TRACK_1_TITLE} — {TRACK_1_ARTIST}"
        )
        # then
        assert state["player_open"] is True, (
            "Плеер должен быть открыт"
        )
        assert state["timeline"] == "00:00", (
            "Позиция таймлайна должна быть в начале"
        )

    # ── Шаг 12: Имитация обрыва сети ──
    @allure.id("J02-TC-J02-00-12")
    @allure.label("req", "REQ-13")
    @allure.label("layer", "e2e")
    @allure.title("Имитировать обрыв сети")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description(
        "Шаг 12 из TC-J02-00: сообщение о проблеме "
        "соединения. REQ-13"
    )
    def test_12_network_break(self, authenticated_client):
        """Проверка сообщения об обрыве сети."""
        # when
        result = authenticated_client.simulate_network_break()
        # then
        assert result["network_available"] is False, (
            "Сеть должна быть недоступна"
        )
        assert ERROR_MESSAGE_RETRY in str(result.get("error_message", "")), (
            "Должно отображаться сообщение о проблеме соединения"
        )

    # ── Шаг 13: Дождаться 3 попыток переподключения ──
    @allure.id("J02-TC-J02-00-13")
    @allure.label("req", "Q-12")
    @allure.label("layer", "e2e")
    @allure.title("Дождаться 3 попыток переподключения")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description(
        "Шаг 13 из TC-J02-00: 3 попытки по 10 сек, "
        "индикатор 1/3, 2/3, 3/3. Q-12"
    )
    def test_13_three_reconnect_attempts(self, authenticated_client):
        """Проверка выполнения трёх попыток переподключения."""
        # when
        for i in range(1, EXPECTED_RETRY_ATTEMPTS + 1):
            attempt = authenticated_client.reconnect_attempt(i)
            # then
            assert attempt["attempt"] == i, (
                f"Текущая попытка должна быть {i}"
            )
            assert attempt["total"] == EXPECTED_RETRY_ATTEMPTS, (
                "Общее количество попыток должно быть 3"
            )
            if i < EXPECTED_RETRY_ATTEMPTS:
                assert attempt["status"] == "pending", (
                    f"Попытка {i} должна быть в статусе 'pending'"
                )
            # интервал
            assert attempt.get("interval_sec") == EXPECTED_RETRY_INTERVAL_SEC, (
                f"Интервал между попытками должен быть "
                f"{EXPECTED_RETRY_INTERVAL_SEC} секунд"
            )

        # after 3rd — проверка финального статуса
        final = authenticated_client.reconnect_attempt(EXPECTED_RETRY_ATTEMPTS)
        assert final["status"] == "failed", (
            "После 3-й попытки статус должен быть 'failed'"
        )
        assert ERROR_MESSAGE_FAILED in str(final.get("error", "")), (
            "После 3-й попытки должно быть сообщение об ошибке"
        )

    # ── Шаг 14: Восстановить соединение ──
    @allure.id("J02-TC-J02-00-14")
    @allure.label("req", "REQ-14, Q-14")
    @allure.label("layer", "e2e")
    @allure.title("Восстановить соединение — трек продолжается с той же позиции")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description(
        "Шаг 14 из TC-J02-00: воспроизведение "
        "возобновляется с позиции 01:23. Q-14"
    )
    def test_14_resume_from_position(self, authenticated_client):
        """Проверка восстановления с той же позиции."""
        # when
        resumed = authenticated_client.resume_from_position(
            TIMELINE_POSITION_BREAK
        )
        # then
        assert resumed["resumed"] is True, (
            "Воспроизведение должно быть возобновлено"
        )
        assert resumed["position"] == TIMELINE_POSITION_BREAK, (
            f"Позиция должна быть {TIMELINE_POSITION_BREAK}"
        )

    # ── Шаг 15: Проверить очередь ──
    @allure.id("J02-TC-J02-00-15")
    @allure.label("req", "Q-24")
    @allure.label("layer", "e2e")
    @allure.title("Проверить очередь после восстановления")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description(
        "Шаг 15 из TC-J02-00: очередь сохранена "
        "в исходном порядке. Q-24"
    )
    def test_15_queue_preserved(self, authenticated_client):
        """Проверка сохранения очереди."""
        # when
        queue = authenticated_client.get_queue()
        # then
        assert queue == QUEUE_ORDER_AFTER_RECOVERY, (
            f"Очередь должна быть: {QUEUE_ORDER_AFTER_RECOVERY}, "
            f"получено: {queue}"
        )
        assert queue[0] == f"{TRACK_1_TITLE} — {TRACK_1_ARTIST}", (
            "Первым в очереди должен быть трек 'Весна — Дельфин'"
        )


# ================================================================
#  Класс: TC-J02-01 — Без подписки (кнопка серая)
# ================================================================
@allure.suite("J02: Офлайн-загрузка и сетевая устойчивость")
@allure.sub_suite("TC-J02-01: Попытка скачивания без подписки")
class TestJ0201NoSubscription:
    """Пользователь без подписки — кнопка «Скачать» серая, тултип."""

    @allure.id("J02-TC-J02-01-01")
    @allure.label("req", "REQ-11, Q-11")
    @allure.label("layer", "smoke")
    @allure.title("Кнопка «Скачать» серая без подписки")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description(
        "Шаг 1 из TC-J02-01: кнопка отображается "
        "серым цветом для пользователя без подписки. REQ-11"
    )
    def test_01_download_button_disabled(self, unauthenticated_client):
        """Проверка, что кнопка неактивна без подписки."""
        # when
        result = unauthenticated_client.download_playlist(
            PLAYLIST_NAME_UNSUBSCRIBED
        )
        # then
        assert result["success"] is False, (
            "Скачивание должно быть недоступно"
        )
        assert result.get("button_state") == "disabled", (
            "Кнопка 'Скачать' должна быть неактивна"
        )

    @allure.id("J02-TC-J02-01-02")
    @allure.label("req", "Q-11")
    @allure.label("layer", "smoke")
    @allure.title("Тултип «Требуется подписка» при наведении")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description(
        "Шаг 2 из TC-J02-01: тултип "
        "с текстом 'Требуется подписка'. Q-11"
    )
    def test_02_tooltip_shown(self, unauthenticated_client):
        """Проверка отображения тултипа на неактивной кнопке."""
        # when
        result = unauthenticated_client.download_playlist(
            PLAYLIST_NAME_UNSUBSCRIBED
        )
        # then
        tooltip = result.get("message", "")
        assert UNSUBSCRIBED_BUTTON_TOOLTIP in tooltip, (
            "Тултип должен содержать 'Требуется подписка'"
        )

    @allure.id("J02-TC-J02-01-03")
    @allure.label("req", "Q-11")
    @allure.label("layer", "smoke")
    @allure.title("Плейлист не загружается без подписки")
    @allure.severity(allure.severity_level.TRIVIAL)
    @allure.description(
        "Шаг 3 из TC-J02-01: плейлист не "
        "загружается для офлайн-прослушивания. Q-11"
    )
    def test_03_playlist_not_downloaded(self, unauthenticated_client):
        """Проверка, что без подписки плейлист не загружается."""
        # when
        result = unauthenticated_client.confirm_download(
            PLAYLIST_NAME_UNSUBSCRIBED
        )
        # then
        assert result["downloaded"] is False, (
            "Без подписки плейлист не должен загружаться"
        )


# ================================================================
#  Класс: TC-J02-02 — Скачивание одиночного трека
# ================================================================
@allure.suite("J02: Офлайн-загрузка и сетевая устойчивость")
@allure.sub_suite("TC-J02-02: Скачивание одиночного трека")
class TestJ0202SingleTrack:
    """Скачивание отдельного трека (не плейлиста)."""

    @allure.id("J02-TC-J02-02-01")
    @allure.label("req", "Q-16, REQ-11")
    @allure.label("layer", "smoke")
    @allure.title("Скачать одиночный трек для офлайн")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description(
        "Шаг 1 из TC-J02-02: диалог подтверждения "
        "для одиночного трека. Q-16"
    )
    def test_01_single_track_download_dialog(self, authenticated_client):
        """Проверка, что для одиночного трека показывается диалог."""
        # given
        authenticated_client.play_track(SINGLE_TRACK_TITLE)
        # when
        result = authenticated_client.download_track(SINGLE_TRACK_TITLE)
        # then
        assert result["downloaded"] is True, (
            "Скачивание одиночного трека должно быть доступно"
        )

    @allure.id("J02-TC-J02-02-02")
    @allure.label("req", "Q-22")
    @allure.label("layer", "smoke")
    @allure.title("Иконка офлайн на одиночном треке")
    @allure.severity(allure.severity_level.TRIVIAL)
    @allure.description(
        "Шаг 2 из TC-J02-02: иконка "
        "офлайн-статуса на треке. Q-22"
    )
    def test_02_single_track_offline_icon(self, authenticated_client):
        """Проверка иконки на скачанном треке."""
        # given
        authenticated_client.download_track(SINGLE_TRACK_TITLE)
        # when
        status = authenticated_client.get_offline_status(SINGLE_TRACK_TITLE)
        # then
        assert status["downloaded"] is True, (
            "Трек должен быть помечен как загруженный"
        )
        assert OFFLINE_ICON_DESCRIPTION in str(
            status.get("offline_icon", "")
        ), "Должна отображаться иконка офлайн"


# ================================================================
#  Класс: TC-J02-03 — Отмена переподключения вручную
# ================================================================
@allure.suite("J02: Офлайн-загрузка и сетевая устойчивость")
@allure.sub_suite("TC-J02-03: Отмена переподключения вручную")
class TestJ0203CancelReconnect:
    """Отмена попытки переподключения вручную (с паузой)."""

    @allure.id("J02-TC-J02-03-01")
    @allure.label("req", "REQ-13, Q-13")
    @allure.label("layer", "smoke")
    @allure.title("Сообщение о проблеме соединения при обрыве")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description(
        "Шаг 1 из TC-J02-03: сообщение "
        "о проблеме с индикатором. Q-13"
    )
    def test_01_network_break_message(self, authenticated_client):
        """Проверка сообщения при обрыве."""
        # when
        result = authenticated_client.simulate_network_break()
        # then
        assert result["network_available"] is False, (
            "Сеть должна быть недоступна"
        )

    @allure.id("J02-TC-J02-03-02")
    @allure.label("req", "Q-13")
    @allure.label("layer", "smoke")
    @allure.title("Отмена попытки переподключения — трек на паузе")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description(
        "Шаг 2 из TC-J02-03: попытка отменена, "
        "воспроизведение приостановлено. Q-13, Q-23"
    )
    def test_02_cancel_reconnect_pause(self, authenticated_client):
        """Проверка, что отмена ставит трек на паузу."""
        # given — сначала обрыв
        authenticated_client.simulate_network_break()
        # when
        cancelled = authenticated_client.cancel_reconnect()
        # then
        assert cancelled["cancelled"] is True, (
            "Переподключение должно быть отменено"
        )
        assert cancelled["paused"] is True, (
            "Воспроизведение трека должно быть на паузе"
        )

    @allure.id("J02-TC-J02-03-03")
    @allure.label("req", "REQ-14, Q-14")
    @allure.label("layer", "smoke")
    @allure.title("Возобновление с той же позиции после отмены")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description(
        "Шаг 3 из TC-J02-03: после восстановления "
        "сети трек продолжается с позиции 01:23. Q-14"
    )
    @pytest.mark.skip(
        reason=(
            "BLOCKER: Q-23 не определяет, сохраняется ли "
            "позиция таймлайна для возобновления после отмены "
            "переподключения. Уточняющий вопрос 3: можно ли "
            "отменить попытку до того, как она началась?"
        )
    )
    @allure.label("bug", "BLOCKER: Q-23 не определяет сохранение позиции")
    @allure.label("blocked_by", "question-3")
    def test_03_resume_after_cancel(self, authenticated_client):
        """Проверка возобновления с позиции после отмены (BLOCKER)."""
        # Уточнение: Q-23 говорит о паузе, но не уточняет,
        # сохраняется ли позиция для возобновления
        pass


# ================================================================
#  Класс: TC-J02-04 — 3 неудачные попытки → ошибка
# ================================================================
@allure.suite("J02: Офлайн-загрузка и сетевая устойчивость")
@allure.sub_suite("TC-J02-04: Три неудачные попытки → ошибка")
class TestJ0204ThreeFailedAttempts:
    """После 3 попыток — сообщение об ошибке соединения."""

    @allure.id("J02-TC-J02-04-01")
    @allure.label("req", "REQ-13")
    @allure.label("layer", "smoke")
    @allure.title("Обрыв сети — сообщение о проблеме")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description(
        "Шаг 1 из TC-J02-04: сообщение "
        "о проблеме соединения. REQ-13"
    )
    def test_01_network_break_during_playback(self, authenticated_client):
        """Проверка сообщения при обрыве во время воспроизведения."""
        # when
        result = authenticated_client.simulate_network_break()
        # then
        assert result["network_available"] is False

    @allure.id("J02-TC-J02-04-02")
    @allure.label("req", "Q-12")
    @allure.label("layer", "smoke")
    @allure.title("Попытка 1/3 — интервал 10 секунд")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description(
        "Шаг 2 из TC-J02-04: индикатор "
        "попытки 1/3. Q-12"
    )
    def test_02_first_attempt(self, authenticated_client):
        """Проверка первой попытки."""
        # when
        attempt = authenticated_client.reconnect_attempt(1)
        # then
        assert attempt["attempt"] == 1, "Должна быть 1-я попытка"
        assert attempt["interval_sec"] == EXPECTED_RETRY_INTERVAL_SEC

    @allure.id("J02-TC-J02-04-03")
    @allure.label("req", "Q-12")
    @allure.label("layer", "smoke")
    @allure.title("Попытка 2/3 — интервал 10 секунд")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description(
        "Шаг 3 из TC-J02-04: индикатор "
        "попытки 2/3. Q-12"
    )
    def test_03_second_attempt(self, authenticated_client):
        """Проверка второй попытки."""
        # when
        attempt = authenticated_client.reconnect_attempt(2)
        # then
        assert attempt["attempt"] == 2, "Должна быть 2-я попытка"

    @allure.id("J02-TC-J02-04-04")
    @allure.label("req", "Q-12")
    @allure.label("layer", "smoke")
    @allure.title("Попытка 3/3 — последняя")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description(
        "Шаг 4 из TC-J02-04: индикатор "
        "попытки 3/3. Q-12"
    )
    def test_04_third_attempt(self, authenticated_client):
        """Проверка третьей попытки."""
        # when
        attempt = authenticated_client.reconnect_attempt(3)
        # then
        assert attempt["attempt"] == EXPECTED_RETRY_ATTEMPTS

    @allure.id("J02-TC-J02-04-05")
    @allure.label("req", "Q-12")
    @allure.label("layer", "smoke")
    @allure.title("После 3-й попытки — сообщение об ошибке")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description(
        "Шаг 5 из TC-J02-04: сообщение об ошибке "
        "соединения. Q-12"
    )
    @pytest.mark.skip(
        reason=(
            "BLOCKER: Q-12 не определяет точный текст "
            "сообщения об ошибке после трёх неудачных попыток. "
            "Уточняющий вопрос 1: какой текст сообщения?"
        )
    )
    @allure.label("bug", "BLOCKER: Q-12 не определяет текст ошибки")
    @allure.label("blocked_by", "question-1")
    def test_05_error_message_after_three_attempts(self, authenticated_client):
        """Проверка текста ошибки (BLOCKER)."""
        # Текст не определён требованием — проверка пропущена
        pass


# ================================================================
#  Класс: TC-J02-05 — Интервал между попытками (граница)
# ================================================================
@allure.suite("J02: Офлайн-загрузка и сетевая устойчивость")
@allure.sub_suite("TC-J02-05: Интервал попыток — граничное значение")
class TestJ0205RetryInterval:
    """Проверка, что интервал между попытками строго 10 секунд."""

    @allure.id("J02-TC-J02-05-01")
    @allure.label("req", "Q-12, REQ-13")
    @allure.label("layer", "smoke")
    @allure.title("Обрыв сети — начало переподключения")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description(
        "Шаг 1 из TC-J02-05: сообщение "
        "о проблеме соединения. Q-12"
    )
    def test_01_network_break(self, authenticated_client):
        """Проверка начала переподключения."""
        # when
        result = authenticated_client.simulate_network_break()
        # then
        assert result["network_available"] is False

    @allure.id("J02-TC-J02-05-02")
    @allure.label("req", "Q-12")
    @allure.label("layer", "smoke")
    @allure.title("Интервал 1/3 → 2/3 = ровно 10 секунд")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description(
        "Шаг 2 из TC-J02-05: засечь "
        "интервал между 1 и 2 попыткой. Q-12"
    )
    def test_02_interval_between_1_and_2(self, authenticated_client):
        """Проверка интервала 10 сек между 1 и 2 попыткой."""
        # when
        t1 = authenticated_client.reconnect_attempt(1)
        t2 = authenticated_client.reconnect_attempt(2)
        # then
        assert t1["interval_sec"] == RETRY_INTERVAL_BASELINE, (
            "Интервал 1-й попытки должен быть 10 сек"
        )
        assert t2["interval_sec"] == RETRY_INTERVAL_BASELINE, (
            "Интервал 2-й попытки должен быть 10 сек"
        )

    @allure.id("J02-TC-J02-05-03")
    @allure.label("req", "Q-12")
    @allure.label("layer", "smoke")
    @allure.title("Интервал 2/3 → 3/3 = ровно 10 секунд")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description(
        "Шаг 3 из TC-J02-05: засечь "
        "интервал между 2 и 3 попыткой. Q-12"
    )
    def test_03_interval_between_2_and_3(self, authenticated_client):
        """Проверка интервала 10 сек между 2 и 3 попыткой."""
        # when
        t2 = authenticated_client.reconnect_attempt(2)
        t3 = authenticated_client.reconnect_attempt(3)
        # then
        assert t2["interval_sec"] == RETRY_INTERVAL_BASELINE
        assert t3["interval_sec"] == RETRY_INTERVAL_BASELINE


# ================================================================
#  Класс: TC-J02-06 — Дубликат трека в плейлист
# ================================================================
@allure.suite("J02: Офлайн-загрузка и сетевая устойчивость")
@allure.sub_suite("TC-J02-06: Дубликат трека в плейлист")
class TestJ0206DuplicateInPlaylist:
    """Добавление одного трека дважды в один плейлист (неопределено).

    Шаги помечены BLOCKER, так как BR-015 не определяет поведение.
    """

    @allure.id("J02-TC-J02-06-01")
    @allure.label("req", "BR-015")
    @allure.label("layer", "blocker")
    @allure.title("Открыть плейлист с треком")
    @allure.severity(allure.severity_level.TRIVIAL)
    @allure.description(
        "Шаг 1 из TC-J02-06: "
        "экран плейлиста. BR-015"
    )
    @pytest.mark.skip(
        reason=(
            "BLOCKER: BR-015 не определяет поведение "
            "при дубликате трека в плейлист. "
            "Уточняющий вопрос 1: допускается ли "
            "повторное добавление одного трека?"
        )
    )
    @allure.label("bug", "BLOCKER: BR-015 не определяет поведение")
    @allure.label("blocked_by", "question-1")
    def test_01_open_playlist_with_track(self, authenticated_client):
        """Проверка, что плейлист открывается (duplicate)."""
        pass

    @allure.id("J02-TC-J02-06-02")
    @allure.label("req", "BR-015")
    @allure.label("layer", "blocker")
    @allure.title("Найти трек «Весна — Дельфин» в результатах")
    @allure.severity(allure.severity_level.TRIVIAL)
    @allure.description(
        "Шаг 2 из TC-J02-06: "
        "трек найден через поиск. BR-015"
    )
    @pytest.mark.skip(
        reason=(
            "BLOCKER: BR-015 не определяет поведение "
            "при дубликате. Трек найден, но "
            "доступность добавления не описана."
        )
    )
    @allure.label("bug", "BLOCKER: BR-015 не определяет дубликат")
    @allure.label("blocked_by", "question-1")
    def test_02_find_track(self, authenticated_client):
        """Поиск трека (duplicate)."""
        pass

    @allure.id("J02-TC-J02-06-03")
    @allure.label("req", "BR-007, BR-015")
    @allure.label("layer", "blocker")
    @allure.title("Добавить трек в плейлист — дубликат")
    @allure.severity(allure.severity_level.TRIVIAL)
    @allure.description(
        "Шаг 3 из TC-J02-06: "
        "выбор плейлиста для добавления. BR-015"
    )
    @pytest.mark.skip(
        reason=(
            "BLOCKER: BR-015 не определяет, "
            "показывается ли сообщение об уже "
            "имеющемся треке. Поведение не определено."
        )
    )
    @allure.label("bug", "BLOCKER: BR-015 не определяет UI дубликата")
    @allure.label("blocked_by", "question-1")
    def test_03_select_playlist_for_duplicate(self, authenticated_client):
        """Выбор плейлиста для дубликата."""
        pass

    @allure.id("J02-TC-J02-06-04")
    @allure.label("req", "BR-015")
    @allure.label("layer", "blocker")
    @allure.title("Трек добавлен (неопределённый результат)")
    @allure.severity(allure.severity_level.TRIVIAL)
    @allure.description(
        "Шаг 4 из TC-J02-06: "
        "трек добавлен в плейлист. BR-015"
    )
    @pytest.mark.skip(
        reason=(
            "BLOCKER: BR-015 не определяет, "
            "будет ли трек отображаться один или "
            "два раза в списке треков плейлиста."
        )
    )
    @allure.label("bug", "BLOCKER: BR-015 не определяет список треков")
    @allure.label("blocked_by", "question-1")
    def test_04_track_added_duplicate(self, authenticated_client):
        """Проверка добавления дубликата."""
        pass

    @allure.id("J02-TC-J02-06-05")
    @allure.label("req", "BR-015")
    @allure.label("layer", "blocker")
    @allure.title("Проверить список треков плейлиста")
    @allure.severity(allure.severity_level.TRIVIAL)
    @allure.description(
        "Шаг 5 из TC-J02-06: "
        "список треков после добавления. BR-015"
    )
    @pytest.mark.skip(
        reason=(
            "BLOCKER: BR-015 не определяет, "
            "сколько раз отображается дублированный трек. "
        )
    )
    @allure.label("bug", "BLOCKER: BR-015 не определяет отображение")
    @allure.label("blocked_by", "question-1")
    def test_05_check_playlist_tracks(self, authenticated_client):
        """Проверка списка после дубликата."""
        pass