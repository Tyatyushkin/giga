# Тестовые данные для J01 — Онбординг и первое воспроизведение
# Источник: output/cases/J01-onboarding-and-first-play/

# Телефоны
PHONE_NEW = "+79990000011"
PHONE_EXISTING = "+79990000022"
PHONE_OTHER = "+79990000033"

# Коды подтверждения
SMS_CODE_VALID = "1111"
SMS_CODE_WRONG = "0000"
SMS_CODE_RESEND_COOLDOWN_SEC = 60

# Жанры
GENRES = ["Электроника", "Хип-хоп", "Инди", "Поп", "Рок", "Джаз"]
GENRES_TOO_FEW = ["Электроника", "Хип-хоп"]       # менее 3 — граница
GENRES_MIN = ["Электроника", "Хип-хоп", "Инди"]     # ровно 3 — нижняя граница

# Поиск
SEARCH_QUERY_VALID = "Дельфин"
SEARCH_QUERY_EMPTY = ""

# Треки
TRACK_FIRST = {
    "title": "Весна",
    "artist": "Дельфин",
}
TRACK_NEXT = {
    "title": "Любовь",
    "artist": "Дельфин",
}