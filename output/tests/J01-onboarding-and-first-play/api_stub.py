"""
api_stub.py — deterministic emulated API client for Zvuk service.

All methods return pre-defined data matching the test data tables
from TC-J01-00 through TC-J01-04. No real network calls.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any


# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------

@dataclass
class Track:
    id: str
    title: str
    artist: str
    album: str
    duration_sec: int


@dataclass
class Artist:
    id: str
    name: str
    genre: str


@dataclass
class Album:
    id: str
    title: str
    artist: str
    year: int


@dataclass
class Playlist:
    id: str
    name: str
    track_count: int


@dataclass
class SearchResults:
    tracks: list[Track] = field(default_factory=list)
    artists: list[Artist] = field(default_factory=list)
    albums: list[Album] = field(default_factory=list)
    playlists: list[Playlist] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Pre-seeded catalogue for query "Дельфин"
# ---------------------------------------------------------------------------

_DOLPHIN_TRACKS = [
    Track(id="trk-001", title="Весна", artist="Дельфин", album="Юность", duration_sec=218),
    Track(id="trk-002", title="Любовь", artist="Дельфин", album="Юность", duration_sec=204),
    Track(id="trk-003", title="Вера", artist="Дельфин", album="Юность", duration_sec=195),
]

_DOLPHIN_ARTISTS = [
    Artist(id="art-001", name="Дельфин", genre="Русский рок"),
]

_DOLPHIN_ALBUMS = [
    Album(id="alb-001", title="Юность", artist="Дельфин", year=2021),
]

_DOLPHIN_PLAYLISTS = [
    Playlist(id="pl-001", name="Хиты русского рока", track_count=50),
]

# Full genre list for onboarding
_AVAILABLE_GENRES = [
    "Электроника",
    "Хип-хоп",
    "Инди",
    "Поп",
    "Рок",
    "R&B",
    "Классика",
    "Джаз",
    "Латино",
    "Метал",
    "Кантри",
    "Регги",
]


# ---------------------------------------------------------------------------
# Exception classes
# ---------------------------------------------------------------------------

class ZvukAPIError(Exception):
    """Generic API error."""


class InvalidCodeError(ZvukAPIError):
    """Raised when SMS confirmation code is wrong."""


class ResendTooSoonError(ZvukAPIError):
    """Raised when resend is attempted before 60 s elapse."""


class OnboardingIncompleteError(ZvukAPIError):
    """Raised when user tries to proceed with < 3 genres."""


class AuthRequiredError(ZvukAPIError):
    """Raised when an unauthenticated call is made."""


# ---------------------------------------------------------------------------
# Stub client
# ---------------------------------------------------------------------------

class ZvukAPIClient:
    """
    Deterministic stub that emulates the Zvuk mobile API.

    Internal state is reset on every ``reset()`` call or when a new
    instance is created.
    """

    def __init__(self) -> None:
        self.reset()

    # ------------------------------------------------------------------
    # State management
    # ------------------------------------------------------------------

    def reset(self) -> None:
        """Return to initial (unauthenticated, clean) state."""
        self._phone: str | None = None
        self._confirmation_code: str | None = None
        self._code_sent_at: float | None = None  # timestamp
        self._authenticated: bool = False
        self._access_token: str | None = None
        self._selected_genres: list[str] = []
        self._onboarding_completed: bool = False
        self._current_track: Track | None = None
        self._queue: list[Track] = []

    @property
    def is_authenticated(self) -> bool:
        return self._authenticated

    @property
    def selected_genres(self) -> list[str]:
        return list(self._selected_genres)

    @property
    def current_track(self) -> Track | None:
        return self._current_track

    @property
    def queue(self) -> list[Track]:
        return list(self._queue)

    # ------------------------------------------------------------------
    # REQ-01: Phone / SMS flow
    # ------------------------------------------------------------------

    def send_confirmation_code(self, phone: str) -> dict[str, Any]:
        """
        Send SMS confirmation code to *phone*.

        Returns a dict with ``{"sent": True, "retry_after_sec": 60}``.
        The stub always uses code ``"1111"``.
        """
        self._phone = phone
        self._confirmation_code = "1111"
        self._code_sent_at = time.monotonic()
        self._authenticated = False
        self._access_token = None
        return {"sent": True, "retry_after_sec": 60}

    def confirm_code(self, code: str) -> dict[str, Any]:
        """
        Confirm the SMS code.

        For the stub the only valid code is ``"1111"``.
        Raises ``InvalidCodeError`` for any other value.
        """
        if self._code_sent_at is None:
            raise AuthRequiredError("Код не был отправлен. Выполните send_confirmation_code.")

        if code != self._confirmation_code:
            raise InvalidCodeError("Неверный код")

        self._authenticated = True
        self._access_token = f"tok_{self._phone}_{int(time.time())}"
        return {
            "authenticated": True,
            "access_token": self._access_token,
            "user_id": "usr-001",
        }

    def resend_confirmation_code(self, phone: str | None = None) -> dict[str, Any]:
        """
        Resend SMS code.

        Raises ``ResendTooSoonError`` if called before 60 seconds
        have elapsed since ``send_confirmation_code``.
        """
        target_phone = phone or self._phone
        if target_phone is None:
            raise AuthRequiredError("Номер не указан.")

        if self._code_sent_at is not None:
            elapsed = time.monotonic() - self._code_sent_at
            if elapsed < 60.0:
                remaining = int(60.0 - elapsed) + 1
                raise ResendTooSoonError(
                    f"Повторная отправка недоступна. Подождите {remaining} с."
                )

        return self.send_confirmation_code(target_phone)

    # ------------------------------------------------------------------
    # REQ-02: Onboarding — genre selection
    # ------------------------------------------------------------------

    def get_genre_list(self) -> list[str]:
        """Return the full catalogue of available genres."""
        return list(_AVAILABLE_GENRES)

    def select_genres(self, genres: list[str]) -> dict[str, Any]:
        """
        Select genres for onboarding.

        ``REQ-02`` requires **at least 3** genres.
        Raises ``OnboardingIncompleteError`` otherwise.
        """
        if len(genres) < 3:
            raise OnboardingIncompleteError(
                "Выберите не менее 3 жанров"
            )
        self._selected_genres = list(genres)
        self._onboarding_completed = True
        return {"selected": len(genres), "status": "completed"}

    # ------------------------------------------------------------------
    # REQ-03: Recommendations block
    # ------------------------------------------------------------------

    def get_recommendations(self) -> dict[str, Any]:
        """
        Return recommendations based on selected genres.

        Requires authentication and completed onboarding.
        """
        self._require_auth()
        if not self._onboarding_completed:
            raise OnboardingIncompleteError(
                "Онбординг не завершён. Выберите не менее 3 жанров."
            )
        # Return at least one recommended item by default
        return {
            "items": [
                {
                    "type": "track",
                    "id": "rec-trk-001",
                    "title": "Рекомендованный трек",
                    "artist": "Исполнитель",
                }
            ],
            "count": 1,
        }

    # ------------------------------------------------------------------
    # REQ-04: Search
    # ------------------------------------------------------------------

    def search(self, query: str) -> SearchResults:
        """
        Search the catalogue.

        Returns tab-separated results matching REQ-04.
        Empty query returns empty results with no tabs.
        """
        self._require_auth()
        if not query or query.strip() == "":
            return SearchResults()

        q = query.strip().lower()
        if "дельфин" in q:
            return SearchResults(
                tracks=list(_DOLPHIN_TRACKS),
                artists=list(_DOLPHIN_ARTISTS),
                albums=list(_DOLPHIN_ALBUMS),
                playlists=list(_DOLPHIN_PLAYLISTS),
            )
        # Unknown query → empty
        return SearchResults()

    # ------------------------------------------------------------------
    # REQ-05: Player
    # ------------------------------------------------------------------

    def play_track(self, track_id: str) -> dict[str, Any]:
        """
        Start playback of a track.

        Returns player state dict. REQ-05 requires cover art, title,
        artist and timeline.
        """
        self._require_auth()
        # Find track from catalogue
        all_tracks = _DOLPHIN_TRACKS
        track = next((t for t in all_tracks if t.id == track_id), None)
        if track is None:
            raise ZvukAPIError(f"Трек {track_id} не найден.")

        self._current_track = track
        # Remove from queue if present
        self._queue = [t for t in self._queue if t.id != track.id]

        return {
            "track_id": track.id,
            "title": track.title,
            "artist": track.artist,
            "album": track.album,
            "duration_sec": track.duration_sec,
            "cover_url": f"https://zvuk.ru/covers/{track.id}.jpg",
            "status": "playing",
            "position_sec": 0,
        }

    # ------------------------------------------------------------------
    # REQ-06: Queue management
    # ------------------------------------------------------------------

    def play_next(self, track_id: str) -> dict[str, Any]:
        """
        Add a track to play next (position 1 in queue behind current).

        Returns updated queue.
        """
        self._require_auth()
        all_tracks = _DOLPHIN_TRACKS
        track = next((t for t in all_tracks if t.id == track_id), None)
        if track is None:
            raise ZvukAPIError(f"Трек {track_id} не найден.")
        # Insert right after current track
        self._queue.insert(0, track)
        return {
            "added": track.id,
            "position": 1,
            "queue": [t.id for t in self._queue],
        }

    def get_queue(self) -> list[Track]:
        """Return the current playback queue."""
        self._require_auth()
        return list(self._queue)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _require_auth(self) -> None:
        if not self._authenticated:
            raise AuthRequiredError(
                "Требуется авторизация. Выполните confirm_code."
            )