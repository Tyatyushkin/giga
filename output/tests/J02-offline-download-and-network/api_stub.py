"""
Детерминированная эмуляция API сервиса «Звук».

Каждый метод — на одно REQ-действие. Один и тот же вход → один и тот же результат.
"""

from typing import Dict, List, Optional, Any


class ZvukAPIClient:
    """
    Детерминированный клиент API сервиса «Звук».
    Не требует реального подключения — все ответы предопределены.
    """

    def __init__(self):
        self._authenticated = False
        self._user_id: Optional[str] = None
        self._subscription_tier: Optional[str] = None
        self._playlists: Dict[str, Any] = {}
        self._queue: List[Dict[str, Any]] = []
        self._current_track: Optional[Dict[str, Any]] = None
        self._network_connected = True
        self._reconnection_attempts = 0
        self._download_progress: Dict[str, Any] = {}

    # ------------------------------------------------------------------
    # Аутентификация и профиль
    # ------------------------------------------------------------------

    def reset(self) -> None:
        """
        Сбрасывает всё внутреннее состояние.
        Используется в фикстурах для изоляции тестов.
        """
        self._authenticated = False
        self._user_id = None
        self._subscription_tier = None
        self._playlists = {}
        self._queue = []
        self._current_track = None
        self._network_connected = True
        self._reconnection_attempts = 0
        self._download_progress = {}

    def authenticate(self, user_id: str, subscription_tier: str = "premium") -> Dict[str, Any]:
        """
        Аутентифицирует пользователя.

        Args:
            user_id: email или ID пользователя
            subscription_tier: 'premium' | 'free'

        Returns:
            Dict с профилем пользователя
        """
        self._authenticated = True
        self._user_id = user_id
        self._subscription_tier = subscription_tier

        return {
            "user_id": user_id,
            "authenticated": True,
            "subscription_tier": subscription_tier,
            "subscription_active": subscription_tier == "premium",
        }

    def is_authenticated(self) -> bool:
        return self._authenticated

    def get_subscription_tier(self) -> str:
        return self._subscription_tier or "free"

    # ------------------------------------------------------------------
    # Поиск
    # ------------------------------------------------------------------

    def search(self, query: str) -> Dict[str, Any]:
        """
        Поиск по сервису.

        Args:
            query: поисковый запрос

        Returns:
            Результаты, сгруппированные по вкладкам
        """
        return {
            "query": query,
            "tabs": {
                "Треки": [
                    {"title": "Весна", "artist": "Дельфин"},
                    {"title": "Голос", "artist": "Дельфин"},
                ],
                "Исполнители": [{"name": "Дельфин"}],
                "Альбомы": [],
                "Плейлисты": [],
            },
            "results_count": 2,
        }

    # ------------------------------------------------------------------
    # Плеер
    # ------------------------------------------------------------------

    def play_track(self, track_id: str) -> Dict[str, Any]:
        """
        Запускает воспроизведение трека.

        Args:
            track_id: идентификатор трека

        Returns:
            Информация о плеере
        """
        self._current_track = {
            "id": track_id,
            "title": "Весна",
            "artist": "Дельфин",
            "album_cover": "cover_spring_delfin.png",
            "is_playing": True,
        }
        return self._current_track

    def get_player_state(self) -> Dict[str, Any]:
        """
        Текущее состояние плеера.
        """
        if not self._current_track:
            return {"is_playing": False}
        return {
            **self._current_track,
            "current_position": "01:23",
            "duration_seconds": 180,
            "progress_percent": 46.0,
        }

    def get_player_position(self) -> str:
        """Возвращает текущую позицию таймлайна."""
        return "01:23"

    def pause_playback(self) -> Dict[str, Any]:
        """
        Ставит воспроизведение на паузу.
        """
        if self._current_track:
            self._current_track["is_playing"] = False
        return {"paused": True, "position": "01:23"}

    def resume_playback(self) -> Dict[str, Any]:
        """
        Возобновляет воспроизведение.
        """
        if self._current_track:
            self._current_track["is_playing"] = True
        return {"resumed": True, "position": "01:23"}

    # ------------------------------------------------------------------
    # Очередь
    # ------------------------------------------------------------------

    def add_to_queue(self, track_id: str, position: str = "next") -> Dict[str, Any]:
        """
        Добавляет трек в очередь воспроизведения.

        Args:
            track_id: идентификатор трека
            position: 'next' — сразу после текущего

        Returns:
            Обновлённая очередь
        """
        self._queue.append(
            {
                "track_id": track_id,
                "title": "Голос",
                "artist": "Дельфин",
                "position": len(self._queue) + 1,
            }
        )
        return {"queue": self._queue, "updated": True}

    def get_queue(self) -> List[Dict[str, Any]]:
        """
        Возвращает текущую очередь воспроизведения.
        """
        return [
            {"title": "Весна", "artist": "Дельфин", "position": 1},
            {"title": "Голос", "artist": "Дельфин", "position": 2},
        ]

    # ------------------------------------------------------------------
    # Плейлисты
    # ------------------------------------------------------------------

    def create_playlist(self, name: str) -> Dict[str, Any]:
        """
        Создаёт новый плейлист.

        Args:
            name: название плейлиста (до 100 символов)

        Returns:
            Созданный плейлист
        """
        playlist = {
            "id": "pl-001",
            "name": name,
            "created_at": "2026-07-28T10:00:00Z",
            "track_count": 0,
            "tracks": [],
            "offline_available": False,
        }
        self._playlists[name] = playlist
        return playlist

    def get_playlist(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Возвращает плейлист по имени.
        """
        return self._playlists.get(name)

    def get_all_playlists(self) -> List[Dict[str, Any]]:
        """
        Список всех плейлистов пользователя.
        """
        return list(self._playlists.values())

    # ------------------------------------------------------------------
    # Скачивание
    # ------------------------------------------------------------------

    def download_playlist(self, name: str, confirmed: bool = False) -> Dict[str, Any]:
        """
        Скачивает плейлист для офлайн-прослушивания.

        Args:
            name: название плейлиста
            confirmed: true — диалог подтверждения пройден

        Returns:
            Статус скачивания
        """
        if not confirmed:
            return {
                "status": "pending_confirmation",
                "dialog": "Скачать плейлист для офлайн-прослушивания?",
                "buttons": ["Да", "Отмена"],
            }

        self._playlists[name]["offline_available"] = True
        self._download_progress[name] = {
            "status": "downloading",
            "progress_percent": 0,
            "icon": "download_arrow",
        }
        return {
            "status": "started",
            "name": name,
            "offline_icon": "download_arrow",
            "progress_percent": 0,
        }

    def download_track(
        self, track_id: str, confirmed: bool = False
    ) -> Dict[str, Any]:
        """
        Скачивает одиночный трек для офлайн-прослушивания.

        Args:
            track_id: идентификатор трека
            confirmed: true — диалог подтверждения пройден

        Returns:
            Статус скачивания
        """
        if not confirmed:
            return {
                "status": "pending_confirmation",
                "dialog": "Скачать трек для офлайн-прослушивания?",
                "buttons": ["Да", "Отмена"],
            }

        return {
            "status": "started",
            "track_id": track_id,
            "offline_icon": "download_arrow",
        }

    def get_download_status(self, name: str) -> Dict[str, Any]:
        """
        Статус скачивания.
        """
        return self._download_progress.get(name, {})

    # ------------------------------------------------------------------
    # Сеть и переподключение
    # ------------------------------------------------------------------

    def simulate_network_disruption(self) -> Dict[str, Any]:
        """
        Имитирует обрыв сети.
        """
        self._network_connected = False
        return {
            "status": "disconnected",
            "message": NETWORK_ERROR_MESSAGE,
            "reconnection_attempts": 0,
        }

    def get_network_status(self) -> Dict[str, Any]:
        """
        Текущий статус сети.
        """
        return {
            "connected": self._network_connected,
        }

    def attempt_reconnection(self) -> Dict[str, Any]:
        """
        Выполняет одну попытку переподключения.

        Returns:
            Результат попытки
        """
        self._reconnection_attempts += 1
        is_last = self._reconnection_attempts >= 3
        if is_last:
            # После 3-й неудачной попытки — ставим плеер на паузу
            if self._current_track:
                self._current_track["is_playing"] = False
        return {
            "attempt": self._reconnection_attempts,
            "max_attempts": 3,
            "interval_seconds": 10,
            "status": "failed",
            "is_last_attempt": is_last,
        }

    def cancel_reconnection(self) -> Dict[str, Any]:
        """
        Отменяет попытку переподключения вручную.
        """
        self._reconnection_attempts = 0
        return {
            "status": "cancelled",
            "playback_paused": True,
            "position": "01:23",
        }

    def restore_network(self) -> Dict[str, Any]:
        """
        Восстанавливает сетевое соединение.
        """
        self._network_connected = True
        return {
            "status": "connected",
            "previous_position": "01:23",
        }

    def get_network_reconnection_attempts(self) -> int:
        """Возвращает количество выполненных попыток переподключения."""
        return self._reconnection_attempts


# ---------------------------------------------------------------------------
# Константы для детерминированного поведения заглушек
# ---------------------------------------------------------------------------

NETWORK_ERROR_MESSAGE = (
    "Проблема с соединением. Выполняется попытка переподключения…"
)

RECONNECTION_FAILED_MESSAGE = (
    "Не удалось восстановить соединение. "
    "Проверьте подключение к интернету."
)