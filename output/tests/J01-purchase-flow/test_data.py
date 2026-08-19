"""
Типизированные константы для journey J01-purchase-flow.

Источник: output/cases/J01-purchase-flow/TC-J01-*.md
Покрываемые требования: BR-001, BR-002, BR-003, BR-004, BR-005, BR-006,
BR-007, BR-008, BR-009, BR-010, BR-011, BR-013, BR-N01, BR-N02, BR-N03,
BR-N04, BR-N06, BR-N07, ANS-01, ANS-02, ANS-03, ANS-04, ANS-10, ANS-11,
ANS-14, ANS-15, ANS-16, ANS-17, ANS-18, ANS-19, ANS-27, ANS-28.
"""

from __future__ import annotations

from typing import Final


# =============================================================================
# Базовый адрес и магазин (TC-J01-00, BR-002, BR-003, ANS-01)
# =============================================================================
ADDRESS_TVERSKAYA: Final[str] = "г. Москва, ул. Тверская, д. 1, кв. 5"
ADDRESS_ARBAT: Final[str] = "г. Москва, ул. Арбат, д. 10, кв. 3"
ADDRESS_OUT_OF_ZONE: Final[str] = "г. Электросталь, ул. Северная, д. 99"

STORE_TVERSKAYA: Final[str] = "Купер Маркет Тверская"
STORE_ARBAT: Final[str] = "Купер Маркет Арбат"

MIN_STORES_AVAILABLE: Final[int] = 2

# =============================================================================
# Товары (TC-J01-00, BR-004, ANS-18)
# =============================================================================
PRODUCT_MILK: Final[str] = "Молоко Простоквашино 3,2% 0,9 л"
PRODUCT_BANANA: Final[str] = "Бананы 1 кг"
PRODUCT_CHOCOLATE: Final[str] = "Шоколад Алёнка 100 г"
PRODUCT_PEAR_UNAVAILABLE: Final[str] = "Груши Конференц 1 кг"

PRODUCT_MILK_PRICE: Final[int] = 95
PRODUCT_BANANA_PRICE: Final[int] = 130
PRODUCT_CHOCOLATE_PRICE: Final[int] = 99

PRODUCT_MILK_WEIGHT_KG: Final[float] = 0.97
PRODUCT_BANANA_WEIGHT_KG: Final[float] = 1.0
PRODUCT_CHOCOLATE_WEIGHT_KG: Final[float] = 0.2

SEARCH_QUERY_MILK: Final[str] = "Молоко 3,2% 0,9 л"
SEARCH_QUERY_PEAR: Final[str] = "Груши Конференц"
SEARCH_QUERY_EMPTY: Final[str] = "Квантовый телепорт 999"

UNAVAILABLE_BADGE: Final[str] = "нет в наличии"

# =============================================================================
# Промокод и бонусы (TC-J01-00 / TC-J01-05 / TC-J01-06 / TC-J01-10,
# BR-006, BR-007, ANS-03, ANS-11, ANS-28)
# =============================================================================
PROMO_CODE_VALID: Final[str] = "WELCOME15"
PROMO_CODE_INVALID: Final[str] = "EXPIRED2024"

PROMO_DISCOUNT_PCT: Final[int] = 15
PROMO_DISCOUNT_AMOUNT: Final[int] = 231
PROMO_MIN_SUM: Final[int] = 1500

BONUS_BALANCE_INITIAL: Final[int] = 5000
BONUS_SPEND_MAIN: Final[int] = 1290
BONUS_SPEND_BOUNDARY: Final[int] = 1295
BONUS_SPEND_OVER_LIMIT: Final[int] = 1296

BONUS_BALANCE_AFTER_MAIN: Final[int] = 3710
BONUS_BALANCE_AFTER_BOUNDARY: Final[int] = 3705

# =============================================================================
# Получатель, комментарий, доставка (TC-J01-00 / TC-J01-11, BR-008, ANS-04, ANS-17)
# =============================================================================
RECIPIENT_NAME: Final[str] = "Иван Иванов"
COURIER_COMMENT: Final[str] = "Позвоните за 5 минут до доставки"

DELIVERY_METHOD_COURIER: Final[str] = "Доставка курьером"
DELIVERY_INTERVAL_DEFAULT: Final[str] = "20–45 мин"
DELIVERY_INTERVAL_LARGE: Final[str] = "40–60 мин"

# =============================================================================
# Суммы и комиссии (TC-J01-00 / TC-J01-06 / TC-J01-07 / TC-J01-10,
# BR-009, ANS-02, ANS-14, ANS-15, ANS-28)
# =============================================================================
CART_SUM_INITIAL: Final[int] = 1540  # 760 (8 молока) + 780 (6 бананов)
CART_SUM_AFTER_CHOCOLATE_ADD: Final[int] = 1639  # 1540 + 99 (шоколад)
CART_SUM_AFTER_PROMO: Final[int] = 1309  # 1540 - 231 (15 %)
CART_SUM_AFTER_BONUSES_MAIN: Final[int] = 19  # 1309 - 1290
CART_SUM_AFTER_BONUSES_BOUNDARY: Final[int] = 14  # 1309 - 1295

# Позиция молока
MILK_QTY_8: Final[int] = 8
MILK_QTY_1: Final[int] = 1
MILK_LINE_PRICE_8: Final[int] = 760  # 8 * 95
MILK_LINE_PRICE_1: Final[int] = 95

# Позиция бананов
BANANA_QTY_6: Final[int] = 6
BANANA_QTY_1: Final[int] = 1
BANANA_LINE_PRICE_6: Final[int] = 780  # 6 * 130

# Шоколад (TC-J01-07)
CHOCOLATE_QTY_1: Final[int] = 1
CHOCOLATE_LINE_PRICE_1: Final[int] = 99

# TC-J01-07 — минимальная сумма
MIN_ORDER_SUM: Final[int] = 500  # ANS-14

# TC-J01-07 — добивка до порога
MILK_QTY_5: Final[int] = 5
MILK_LINE_PRICE_5: Final[int] = 475  # 5 * 95
CART_SUM_ABOVE_THRESHOLD: Final[int] = 574  # 99 + 475

# TC-J01-08 — превышение веса
WEIGHT_LIMIT_KG: Final[float] = 10.0  # ANS-15
BANANA_QTY_11: Final[int] = 11
MILK_QTY_WEIGHT_1: Final[int] = 1
CART_TOTAL_WEIGHT_KG: Final[float] = 11.97  # 11 * 1.0 + 1 * 0.97

# TC-J01-09 — крупный заказ
CART_POSITIONS_LARGE: Final[int] = 16
CART_POSITIONS_THRESHOLD: Final[int] = 15

# TC-J01-10 — комиссии и остаток наличными
DELIVERY_FEE_VALUE: Final[int] = 98
ASSEMBLY_FEE_VALUE: Final[int] = 29
CASH_DUE_TO_COURIER: Final[int] = 146  # 19 + 98 + 29 (ANS-28)

# =============================================================================
# Статусы и этапы отслеживания (TC-J01-00, BR-011, ANS-10, ANS-27)
# =============================================================================
ORDER_STATUS_CREATED: Final[str] = "Создан"
ORDER_STATUS_DELIVERED: Final[str] = "Доставлен"
ORDER_STATUS_AUTOCANCELLED: Final[str] = "Автоотменён"

TRACKING_STAGES: Final[tuple[str, ...]] = (
    "создание",
    "сборка",
    "передача курьеру",
    "доставка",
    "завершение",
)

# =============================================================================
# Способы оплаты (TC-J01-00 / TC-J01-10, BR-010, ANS-11, ANS-28)
# =============================================================================
PAYMENT_METHOD_CARD: Final[str] = "Карта Сбера"
PAYMENT_METHOD_BONUSES: Final[str] = "Бонусы СберСпасибо"

# =============================================================================
# TC-J01-12 — авторизация по номеру телефона (BR-001, ANS-19)
# =============================================================================
PHONE_NUMBER: Final[str] = "+7 999 000-00-11"
WRONG_CODE: Final[str] = "0000"
CORRECT_CODE: Final[str] = "1111"

CODE_VALIDITY_MINUTES: Final[int] = 3
MAX_ATTEMPTS: Final[int] = 3
ATTEMPTS_AFTER_1_FAIL: Final[int] = 2
ATTEMPTS_AFTER_2_FAIL: Final[int] = 1

# =============================================================================
# TC-J01-01 / TC-J01-05 — сообщения/предложения (BR-N01, BR-N02)
# =============================================================================
# Используются нейтральные дескрипторы, не выдуманные тексты.
