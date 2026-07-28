"""
Хелперы для эмуляции API сервиса «Звук».

В реальном проекте эти функции вызывают реальный HTTP API.
Здесь — заглушка, демонстрирующая контракты и структуру вызовов.
"""

from typing import Optional
from dataclasses import dataclass, field
from helpers.test_data import SMS_CODE_VALID, SMS_CODE_RESEND_COOLDOWN_SEC

# ---------------------------------------------------------------------------
# Модели данных (в реальном проекте — из OpenAPI схемы)
# ---------------------------------------------------------------------------

@dataclass
class PhoneVerificationState:
    """Состояние верификации номера."""
    phone: str
    code_sent: bool = False
    code_resend_attempts: int = 0
    last_code_sent_at: Optional[int] = None  # timestamp Unix

@dataclass
class Account:
    """Аккаунт пользователя."""
    phone: str
    is_verified: bool = False
    selected_genres: list = field(default_factory=list)

@dataclass
class SearchResult:
    """Результат поиска."""
    query: str
    tracks: list = field(default_factory=list)
    artists: list = field(default_factory=list)
    albums: list = field(default_factory=list)
    playlists: list = field(default_factory=list)

@dataclass
class PlayerState:
    """Состояние плеера."""
    current_track: Optional[dict] = None
    queue: list = field(default_factory=list)
    is_expanded: bool = False

@dataclass
class Playlist:
    """Плейлист (из J02, переиспользуется)."""
    name: str
    is_private: bool = True
    tracks: list = field(default_factory=list)

# ---------------------------------------------------------------------------
# Эмуляция API-вызовов
# ---------------------------------------------------------------------------

class ZvukAPIClient:
    """Эмуляция HTTP-клиента сервиса «Звук»."""

    def __init__(self, base_url: str = "https://api.zvuk.dev/v1"):
        self.base_url = base_url
        self._state = {
            "accounts": {},
            "playlists": [],
            "likes": set(),
        }

    # ---- Авторизация ----

    def send_verification_code(self, phone: str) -> dict:
        """
        Отправить SMS с кодом. REQ-01.
        Возвращает: { "phone": str, "code_sent": bool, "resend_available_at": int }
        """
        return {
            "phone": phone,
            "code_sent": True,
            "resend_available_at": SMS_CODE_RESEND_COOLDOWN_SEC,
        }

    def verify_code(self, phone: str, code: str) -> dict:
        """
        Подтвердить код. REQ-01.
        Возвращает: { "verified": bool, "message": str }
        """
        if code == SMS_CODE_VALID:
            return {"verified": True, "message": "Код подтверждён"}
        return {"verified": False, "message": "Неверный код"}

    # ---- Онбординг ----

    def select_genres(self, phone: str, genres: list) -> dict:
        """
        Выбрать жанры. REQ-02.
        """
        if len(genres) < 3:
            return {
                "selected": False,
                "message": "Выберите не менее 3 жанров",
                "count": len(genres),
            }
        return {
            "selected": True,
            "message": "Жанры выбраны",
            "count": len(genres),
        }

    # ---- Поиск ----

    def search(self, query: str) -> SearchResult:
        """REQ-04."""
        if not query.strip():
            return SearchResult(query="", tracks=[], artists=[], albums=[], playlists=[])
        # В реальности — запрос к поисковому API
        return SearchResult(
            query=query,
            tracks=[{"title": "Весна", "artist": "Дельфин"}],
            artists=[{"name": "Дельфин"}],
            albums=[{"title": "Глубина"}],
            playlists=[{"title": "Звуки моря"}],
        )

    # ---- Плеер ----

    def play_track(self, track_id: str) -> PlayerState:
        """REQ-05."""
        return PlayerState(
            current_track={"title": "Весна", "artist": "Дельфин"},
            is_expanded=True,
        )

    def add_to_queue(self, track_id: str, position: str = "next") -> PlayerState:
        """REQ-06."""
        return PlayerState(
            current_track={"title": "Весна", "artist": "Дельфин"},
            queue=[{"title": "Любовь", "artist": "Дельфин"}],
        )

    # ---- Коллекция ----

    def like_track(self, phone: str, track_id: str) -> int:
        """REQ-07. Возвращает счётчик лайков."""
        self._state["likes"].add(track_id)
        return len(self._state["likes"])

    def unlike_track(self, phone: str, track_id: str) -> int:
        """Снятие лайка (гипотеза)."""
        self._state["likes"].discard(track_id)
        return len(self._state["likes"])

    # ---- Плейлисты ----

    def create_playlist(self, name: str, is_private: bool = True) -> Playlist:
        """REQ-08."""
        p = Playlist(name=name, is_private=is_private)
        self._state["playlists"].append(p)
        return p

    def get_playlists(self, phone: str) -> list:
        """REQ-10."""
        return sorted(self._state["playlists"], key=lambda x: x.name)

    def download_playlist(self, phone: str, playlist_name: str, has_subscription: bool) -> dict:
        """REQ-11."""
        if has_subscription:
            return {"downloaded": True, "url": "https://cdn.zvuk.dev/offline/..."}
        return {"downloaded": False, "message": "Требуется подписка"}