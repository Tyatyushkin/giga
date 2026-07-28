"""
Детерминированная эмуляция API «Звук» для тарифа Free (без подписки).

Один метод = одно REQ-действие. Вход → выход детерминирован.
"""

from typing import Optional, Dict, Any, List


class ZvukFreeApiStub:
    """Заглушка API приложения «Звук» для пользователя без подписки (Free).

    Хранит состояние: авторизован ли, номер телефона, сессия,
    плейлисты, очередь, текущий трек, позиция, счётчик лайков,
    счётчик пропусков.
    """

    def __init__(self) -> None:
        self._is_authenticated: bool = False
        self._phone_number: Optional[str] = None
        self._session_active: bool = False
        self._current_track: Optional[str] = None
        self._queue: List[str] = []
        self._playlist_ids: List[str] = []
        self._history: List[str] = []
        self._liked_tracks_count: int = 0
        self._skip_count: int = 0
        self._skip_blocked: bool = False
        self._favorites: List[str] = []
        self._current_timeline: str = "0:00"

    # ── REQ-01 / REQ-15: Авторизация по СМС ──

    def send_sms_code(self, phone: str) -> Dict[str, Any]:
        """Отправить СМС-код на указанный номер.

        Детерминировано: при любом номере возвращаем success.
        """
        self._phone_number = phone
        return {"status": "ok", "phone": phone}

    def confirm_sms_code(self, phone: str, code: str) -> Dict[str, Any]:
        """Подтвердить СМС-код.

        Детерминировано:
        - Если code == "111222" → вход выполнен, сессия создана.
        - Если code == "0000" → ошибка 'Неверный код'.
        - Иначе → ошибка 'Неверный код'.
        """
        if code == "111222":
            self._is_authenticated = True
            self._session_active = True
            return {"status": "ok", "session": "active"}
        return {"status": "error", "message": "Неверный код подтверждения"}

    # ── REQ-02 / REQ-16: Главная, подборки ──

    def get_main_page(self) -> Dict[str, Any]:
        """Получить главную страницу с персональными рекомендациями.

        Детерминировано: всегда показывает блоки 'Рекомендации дня'
        и 'Подборки' для авторизованного пользователя.
        """
        if not self._is_authenticated:
            return {"screen": "public", "sections": []}
        return {
            "screen": "main",
            "sections": [
                {
                    "title": "Рекомендации дня",
                    "items": [
                        {"track": "Весна", "artist": "Дельфин"},
                        {"track": "Любовь", "artist": "Дельфин"},
                    ],
                },
                {"title": "Подборки", "items": ["Рекомендации дня"]},
            ],
        }

    # ── REQ-03 / REQ-17: Поиск с заглушкой (Free) ──

    def search_track(self, query: str) -> Dict[str, Any]:
        """Поиск трека.

        Детерминировано:
        - Если query == "Весна" → результат в разделе 'Треки',
          'Исполнители', 'Альбомы'. Клик → заглушка.
        - Если query == "xyzzy_nonexistent_2026" → пустой результат.
        - Иначе → пустой результат.
        """
        if query == "Весна":
            return {
                "tracks": [{"title": "Весна", "artist": "Дельфин"}],
                "artists": [{"name": "Дельфин"}],
                "albums": [],
                "play_button_blocked": True,
            }
        if query == "xyzzy_nonexistent_2026":
            return {
                "tracks": [],
                "artists": [],
                "albums": [],
                "message": "По вашему запросу ничего не найдено",
            }
        return {"tracks": [], "artists": [], "albums": []}

    # ── REQ-03 / Q-02: Заглушка при клике на трек (Free) ──

    def click_track_free(self, track_title: str) -> Dict[str, Any]:
        """Кликнуть на трек, который НЕЛЬЗЯ воспроизвести (Free).

        Детерминировано: возвращает заглушку 'Доступно только с подпиской'.
        """
        return {
            "status": "blocked",
            "message": "Доступно только с подпиской",
            "track": track_title,
        }

    # ── REQ-04 / REQ-18: Страница исполнителя ──

    def get_artist_page(self, artist_name: str) -> Dict[str, Any]:
        """Открыть страницу исполнителя.

        Детерминировано: показывает популярные треки и альбомы.
        """
        return {
            "artist": artist_name,
            "popular_tracks": ["Весна", "Любовь"],
            "albums": ["Альбом 1", "Альбом 2"],
        }

    # ── REQ-05 / REQ-19: Воспроизведение из подборки ──

    def play_from_playlist(self, playlist_name: str) -> Dict[str, Any]:
        """Воспроизвести подборку.

        Детерминировано: плеер развёрнут, трек играет.
        """
        self._current_track = "Весна"
        self._current_timeline = "0:00 / 3:45"
        self._skip_count = 0
        self._skip_blocked = False
        return {
            "status": "playing",
            "track": "Весна",
            "artist": "Дельфин",
            "cover": "cover.jpg",
            "timeline": self._current_timeline,
        }

    def get_player_state(self) -> Dict[str, Any]:
        """Текущее состояние плеера.

        Детерминировано: трек 'Весна', исполнитель 'Дельфин',
        обложка, таймлайн активен.
        """
        return {
            "track": self._current_track or "Весна",
            "artist": "Дельфин",
            "cover": "cover.jpg",
            "timeline": self._current_timeline,
            "skip_count": self._skip_count,
            "skip_blocked": self._skip_blocked,
        }

    # ── REQ-06 / REQ-20: Лайк трека (Любимое) ──

    def like_track(self, track_title: str) -> Dict[str, Any]:
        """Поставить лайк треку.

        Детерминировано: счётчик увеличивается на 1.
        """
        self._liked_tracks_count += 1
        if track_title not in self._favorites:
            self._favorites.append(track_title)
        return {
            "status": "liked",
            "favorites_count": self._liked_tracks_count,
            "favorites": self._favorites,
            "liked": True,
        }

    # ── REQ-05 / REQ-27: Пропуск трека (Далее) ──

    def skip_track(self) -> Dict[str, Any]:
        """Нажать 'Далее' (пропустить трек).

        Детерминировано:
        - Если skip_count < 5 → пропуск выполнен.
        - Если skip_count >= 5 → кнопка 'Далее' блокируется,
          трек продолжает играть до конца.
        """
        self._skip_count += 1
        if self._skip_count >= 5:
            self._skip_blocked = True
            return {
                "status": "blocked",
                "message": "Лимит пропусков исчерпан",
                "track_continues": True,
                "timeline": "доигрывает",
            }
        return {"status": "skipped", "track": "Весна", "timeline": "следующий трек"}

    # ── REQ-07 / REQ-28: Выход ──

    def logout(self) -> Dict[str, Any]:
        """Выход из аккаунта. Завершает сессию.

        Детерминировано: сессия завершена, плеер остановлен,
        персональные данные скрыты.
        """
        self._session_active = False
        self._is_authenticated = False
        self._current_track = None
        self._queue = []
        self._current_timeline = "0:00"
        return {
            "status": "logged_out",
            "session": "ended",
            "player": "stopped",
            "timeline": "0:00",
        }

    # ── REQ-08 / REQ-29: Повторный вход ──

    def login_again(self, phone: str, code: str) -> Dict[str, Any]:
        """Повторный вход в аккаунт.

        Детерминировано: вход выполнен, библиотека, плейлисты
        и история видны. Очередь и трек НЕ восстановлены.
        """
        if code == "111222":
            self._is_authenticated = True
            self._session_active = True
            # Не восстанавливаем очередь
            self._current_track = None
            self._queue = []
            self._current_timeline = "0:00"
            return {
                "status": "ok",
                "restored": {
                    "library": ["Моя музыка", "плейлист 1"],
                    "history": ["Весна", "Любовь"],
                    "favorites": self._favorites,
                },
                "not_restored": {
                    "queue": [],
                    "current_track": None,
                    "timeline": "0:00",
                },
            }
        return {"status": "error", "message": "Неверный код"}