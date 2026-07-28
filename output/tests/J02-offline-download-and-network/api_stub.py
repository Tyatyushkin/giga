"""
Детерминированная эмуляция API «Звук».

Один метод = одно REQ-действие.
Один и тот же вход → один и тот же выход.
"""

from __future__ import annotations

import copy
from typing import Any


class ApiStub:
    """
    Заглушка API-сервиса «Звук».

    Состояние хранится в экземпляре, поэтому каждый
    ``api_client`` получает независимый изолированный объект.

    Поддерживаемые операции (Reqiurement → method):

    | REQ | Метод | Описание |
    |-----|-------|----------|
    | REQ-04 | ``search_tracks(query)`` | Поиск, группировка по вкладкам |
    | REQ-05 | ``play_track(track_id)`` | Запуск плеера с треком |
    | REQ-08 | ``create_playlist(name)`` | Создание плейлиста |
    | REQ-11 | ``download_playlist(…)`` | Скачивание (только при подписке) |
    | REQ-13 | ``simulate_network_break()`` | Эмуляция обрыва сети |
    | REQ-14 | ``reconnect()`` | Попытка восстановления соединения |
    | Q-12 | ``reconnect_attempt(count)`` | N-я попытка переподключения |
    | Q-13 | ``cancel_reconnect()`` | Отмена вручную |
    | Q-14 | ``resume_from_position(pos)`` | Возобновление с позиции |
    | Q-15 | ``confirm_download()`` | Диалог подтверждения |
    | Q-22 | ``get_offline_icon()`` | Иконка офлайн-статуса |
    | Q-23 | ``pause_playback()`` | Пауза |
    | Q-24 | ``get_queue()`` | Получение очереди |
    | BR-005 | ``playback_controls()`` | Пауза, пропуск, перемотка |
    | BR-007 | ``playlist_operations()`` | Создание/редактирование плейлиста |
    | BR-011 | ``subscription_gate()`` | Проверка тарифа |
    | BR-015 | ``add_to_playlist()`` | Добавление трека в плейлист |
    """

    def __init__(self):
        # ── Внутреннее состояние ──
        self._subscription: str | None = None
        self._authenticated: bool = False
        self._play_queue: list[str] = []
        self._collection: list[str] = []
        self._playlists: dict[str, list[str]] = {}
        self._playlist_downloaded: set[str] = set()
        self._track_downloaded: set[str] = set()
        self._current_track: str | None = None
        self._current_position: str = "00:00"
        self._network_available: bool = True
        self._reconnect_attempts: int = 0
        self._reconnect_cancelled: bool = False
        self._search_results: dict[str, list[str]] = {}
        self._player_open: bool = False

    # ── Сеттеры для фикстур ──

    def _set_subscription(self, plan: str | None) -> None:
        self._subscription = plan

    def _set_authenticated(self, val: bool) -> None:
        self._authenticated = val

    def _set_play_queue(self, queue: list[str]) -> None:
        self._play_queue = list(queue)

    def _set_collection(self, items: list[str]) -> None:
        self._collection = list(items)

    # ── REQ-04: Поиск ──

    def search_tracks(self, query: str) -> dict[str, list[str]]:
        """
        Возвращает детерминированные результаты поиска.

        ``query = "Дельфин"`` → ``{"Треки": ["Весна — Дельфин", …], …}``
        Любой другой запрос → пустой словарь.
        """
        if query == "Дельфин":
            self._search_results = {
                "Треки": ["Весна — Дельфин", "Голос — Дельфин"],
                "Исполнители": ["Дельфин"],
                "Альбомы": [],
                "Плейлисты": [],
            }
        else:
            self._search_results = {}
        return copy.deepcopy(self._search_results)

    # ── REQ-05: Плеер ──

    def play_track(self, track_title: str) -> dict[str, Any]:
        """
        Запускает плеер с треком.

        ``track_title = "Весна — Дельфин"`` → плеер открыт,
        обложка, название, исполнитель, таймлайн.
        """
        self._player_open = True
        self._current_track = track_title
        self._current_position = "00:00"
        return {
            "player_open": True,
            "track_title": track_title,
            "artist": "Дельфин",
            "timeline": "00:00",
        }

    def get_player_state(self) -> dict[str, Any]:
        """Текущее состояние плеера."""
        return {
            "player_open": self._player_open,
            "current_track": self._current_track,
            "position": self._current_position,
        }

    # ── REQ-08: Создание плейлиста ──

    def create_playlist(self, name: str) -> dict[str, Any]:
        """
        Создаёт плейлист (макс 100 символов).

        ``name`` сохраняется в ``self._playlists``.
        """
        self._playlists[name] = []
        return {"created": True, "name": name, "tracks": []}

    def get_playlist(self, name: str) -> dict[str, Any] | None:
        """Возвращает плейлист по имени или None."""
        if name in self._playlists:
            return {
                "name": name,
                "tracks": list(self._playlists[name]),
            }
        return None

    # ── REQ-11 / Q-04: Скачивание ──

    def download_playlist(self, name: str) -> dict[str, Any]:
        """
        Скачивание плейлиста.

        Если ``_subscription is None`` → ошибка 403.
        Если подписка есть → диалог подтверждения → загрузка.
        """
        if self._subscription is None or self._subscription == "free":
            return {
                "success": False,
                "error": 403,
                "message": UNSUBSCRIBED_BUTTON_TOOLTIP,
                "button_state": "disabled",
            }
        # Подписка есть — диалог подтверждения
        return {
            "success": True,
            "dialog": DOWNLOAD_CONFIRMATION_PROMPT,
            "offline_icon": OFFLINE_ICON_DESCRIPTION,
        }

    def confirm_download(self, name: str) -> dict[str, Any]:
        """
        Подтверждение скачивания (Q-15).

        После нажатия «Да» — плейлист начинает загружаться.
        """
        if self._subscription is not None and self._subscription != "free":
            self._playlist_downloaded.add(name)
            return {
                "downloaded": True,
                "playlist": name,
                "offline_icon": OFFLINE_ICON_DESCRIPTION,
            }
        return {"downloaded": False, "error": "Нет подписки"}

    def download_track(self, track_title: str) -> dict[str, Any]:
        """
        Скачивание одиночного трека (Q-16).
        """
        if self._subscription is not None and self._subscription != "free":
            self._track_downloaded.add(track_title)
            return {
                "downloaded": True,
                "track": track_title,
                "offline_icon": OFFLINE_ICON_DESCRIPTION,
            }
        return {
            "downloaded": False,
            "error": "Нет подписки",
        }

    def get_offline_status(self, item_name: str) -> dict[str, Any]:
        """Статус офлайн-загрузки элемента."""
        return {
            "downloaded": (
                item_name in self._playlist_downloaded
                or item_name in self._track_downloaded
            ),
            "offline_icon": (
                OFFLINE_ICON_DESCRIPTION
                if (item_name in self._playlist_downloaded
                    or item_name in self._track_downloaded)
                else None
            ),
        }

    # ── REQ-13, Q-12: Сеть / переподключение ──

    def simulate_network_break(self) -> dict[str, Any]:
        """Эмуляция обрыва сети."""
        self._network_available = False
        return {
            "network_available": False,
            "error_message": ERROR_MESSAGE_RETRY,
        }

    def reconnect_attempt(self, count: int) -> dict[str, Any]:
        """
        N-я попытка переподключения.

        ``count`` от 1 до 3.
        """
        self._reconnect_attempts = count
        if count < EXPECTED_RETRY_ATTEMPTS:
            return {
                "attempt": count,
                "total": EXPECTED_RETRY_ATTEMPTS,
                "status": "pending",
                "interval_sec": EXPECTED_RETRY_INTERVAL_SEC,
            }
        # Последняя (3-я) попытка — тоже с интервалом
        return {
            "attempt": count,
            "total": EXPECTED_RETRY_ATTEMPTS,
            "status": "failed",
            "error": ERROR_MESSAGE_FAILED,
            "interval_sec": EXPECTED_RETRY_INTERVAL_SEC,
        }

    def get_reconnect_state(self) -> dict[str, Any]:
        """Текущее состояние переподключения."""
        return {
            "attempts": self._reconnect_attempts,
            "cancelled": self._reconnect_cancelled,
            "network_available": self._network_available,
        }

    # ── Q-13: Отмена переподключения ──

    def cancel_reconnect(self) -> dict[str, Any]:
        """
        Отмена попытки переподключения вручную.

        После отмены — трек ставится на паузу.
        """
        self._reconnect_cancelled = True
        self._reconnect_attempts = 0
        return {
            "cancelled": True,
            "paused": True,
        }

    # ── Q-14: Возобновление ──

    def resume_from_position(self, position: str) -> dict[str, Any]:
        """
        Возобновление воспроизведения с указанной позиции.

        ``position`` — строка ``MM:SS``.
        """
        self._current_position = position
        return {
            "resumed": True,
            "position": position,
        }

    def get_current_position(self) -> str:
        """Текущая позиция таймлайна."""
        return self._current_position

    # ── Q-24: Очередь ──

    def get_queue(self) -> list[str]:
        """Возвращает копию очереди воспроизведения."""
        return list(self._play_queue)

    def add_to_queue(self, track_title: str, position: str = "next") -> dict[str, Any]:
        """
        Добавление трека в очередь.

        ``position="next"`` — сразу после текущего.
        """
        if position == "next":
            self._play_queue.insert(1, track_title)
        else:
            self._play_queue.append(track_title)
        return {
            "added": True,
            "track": track_title,
            "position": position,
            "queue": list(self._play_queue),
        }

    # ── BR-007 / BR-015: Плейлист / дубликат ──

    def add_to_playlist(
        self,
        playlist_name: str,
        track_title: str,
        allow_duplicates: bool = False,
    ) -> dict[str, Any]:
        """
        Добавление трека в плейлист.

        Если ``allow_duplicates=False`` и трек уже есть —
        поведение зависит от ``BR-015`` (не определено).
        """
        playlist = self._playlists.get(playlist_name)
        if playlist is None:
            return {"error": "Плейлист не найден"}

        if not allow_duplicates and track_title in playlist:
            # BR-015: не определено — возвращаем как есть
            return {
                "added": True,
                "duplicate": True,
                "track": track_title,
                "playlist": playlist_name,
            }

        playlist.append(track_title)
        self._playlists[playlist_name] = playlist
        return {
            "added": True,
            "duplicate": False,
            "track": track_title,
            "playlist": playlist_name,
            "tracks": list(playlist),
        }

    # ── BR-005: Управление воспроизведением ──

    def playback_controls(self, action: str) -> dict[str, Any]:
        """
        Управление воспроизведением.

        ``action``: ``"pause"``, ``"play"``, ``"skip"``, ``"seek"``.
        """
        valid = {"pause", "play", "skip", "seek"}
        assert action in valid, f"Unknown action: {action}"
        return {
            "action": action,
            "success": True,
        }


# ── Константы (локальные, продублированы для изоляции) ──

UNSUBSCRIBED_BUTTON_TOOLTIP: str = "Требуется подписка"
DOWNLOAD_CONFIRMATION_PROMPT: str = (
    "Скачать плейлист для "
    "офлайн-прослушивания?"
)
OFFLINE_ICON_DESCRIPTION: str = "стрелка вниз"
ERROR_MESSAGE_RETRY: str = (
    "Проблема с соединением. "
    "Выполняется попытка переподключения…"
)
ERROR_MESSAGE_FAILED: str = (
    "Не удалось восстановить соединение. "
    "Проверьте подключение к интернету"
)
EXPECTED_RETRY_ATTEMPTS: int = 3
EXPECTED_RETRY_INTERVAL_SEC: int = 10