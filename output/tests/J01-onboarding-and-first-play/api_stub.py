"""
Детерминированная эмуляция API «Звук».

Один метод = одно REQ-действие. Вход → выход детерминирован.
"""

from typing import List, Optional, Dict, Any


class ZvukApiStub:
    """Заглушка API приложения «Звук».

    Хранит состояние: авторизован ли пользователь, какие жанры выбраны,
    какой трек воспроизводится, какая очередь.
    """

    def __init__(self) -> None:
        self._is_authenticated: bool = False
        self._phone_number: Optional[str] = None
        self._confirmed_code: Optional[str] = None
        self._selected_genres: List[str] = []
        self._onboarding_completed: bool = False
        self._current_track: Optional[str] = None
        self._queue: List[str] = []

    # ── REQ-01: Регистрация по номеру телефона ──

    def send_code(self, phone: str) -> Dict[str, Any]:
        """Отправить код на указанный номер.

        Детерминированный результат: при любом номере возвращаем код 1111.
        """
        self._phone_number = phone
        return {"status": "code_sent", "code": "1111", "phone": phone}

    def confirm_code(self, phone: str, code: str) -> Dict[str, Any]:
        """Подтвердить код.

        Детерминированный результат:
        - Если code == "1111" → успех.
        - Иначе → ошибка "Неверный код".
        """
        if code == "1111":
            self._is_authenticated = True
            return {"status": "ok", "phone": phone}
        return {"status": "error", "message": "Неверный код"}

    def is_code_resend_available(self) -> bool:
        """Доступна ли повторная отправка кода.

        Детерминированный результат: всегда False в течение 60 секунд.
        """
        return False

    # ── REQ-02: Онбординг — выбор жанров ──

    def select_genres(self, genres: List[str]) -> Dict[str, Any]:
        """Выбрать жанры на онбординге.

        Детерминированный результат: жанры сохраняются, возвращается
        количество выбранных. REQ-02 требует не менее 3 для продолжения.
        """
        self._selected_genres = genres
        count = len(genres)
        can_continue = count >= 3
        return {
            "status": "ok",
            "count": count,
            "can_continue": can_continue,
        }

    def confirm_onboarding(self) -> Dict[str, Any]:
        """Подтвердить завершение онбординга.

        Детерминированный результат:
        - Если выбрано >= 3 жанров → главный экран открыт.
        - Иначе → ошибка.
        """
        if len(self._selected_genres) >= 3:
            self._onboarding_completed = True
            return {"status": "ok", "screen": "main", "recommendations": 1}
        return {"status": "error", "message": "Выберите не менее 3 жанров"}

    # ── REQ-03: Блок «Рекомендации» ──

    def get_recommendations(self) -> List[Dict[str, Any]]:
        """Получить блок рекомендаций.

        Детерминированный результат: всегда содержит 1 элемент при
        завершённом онбординге.
        """
        if self._onboarding_completed:
            return [{"title": "Рекомендовано для вас", "items": 3}]
        return []

    # ── REQ-04: Поиск ──

    def search(self, query: str) -> Dict[str, Any]:
        """Поиск по запросу.

        Детерминированный результат:
        - Если query == "Дельфин" → результаты во всех 4 вкладках.
        - Если query == "" → пустой результат.
        - Иначе → частичные результаты.
        """
        if query == "Дельфин":
            return {
                "tracks": [{"title": "Весна"}, {"title": "Любовь"}],
                "artists": [{"name": "Дельфин"}],
                "albums": [],
                "playlists": [],
            }
        if query == "":
            return {"tracks": [], "artists": [], "albums": [], "playlists": []}
        return {"tracks": [], "artists": [], "albums": [], "playlists": []}

    # ── REQ-05: Плеер ──

    def get_player_state(self) -> Dict[str, Any]:
        """Текущее состояние плеера.

        Детерминированный результат: трек "Весна", обложка загружена,
        таймлайн активен.
        """
        return {
            "track": "Весна",
            "artist": "Дельфин",
            "cover": "cover.jpg",
            "timeline": "0:00 / 3:45",
        }

    # ── REQ-06: Управление очередью ──

    def add_to_queue(self, track: str, position: str = "next") -> Dict[str, Any]:
        """Добавить трек в очередь.

        Детерминированный результат: трек встаёт на позицию сразу после
        текущего.
        """
        self._queue.append(track)
        return {"status": "ok", "queue": self._queue, "position": position}