"""
Типизированные константы для journey J03-corporate-business.

Источник: output/cases/J03-corporate-business/TC-J03-*.md
Покрываемые требования: BR-001, BR-003, BR-004, BR-005, BR-008, BR-009,
BR-014, ANS-09, ANS-13, ANS-22, ANS-23, ANS-24, ANS-25, ANS-26.
"""

from typing import Final

# --- Тариф (ANS-22) ---
TARIFF_NAME_STANDARD: Final[str] = "Стандарт"
TARIFF_LIST_MIN_ITEMS: Final[int] = 2

# --- Магазины (ANS-09) ---
STORE_MARKET: Final[str] = "Купер Бизнес Маркет"
STORE_WAREHOUSE: Final[str] = "Купер Бизнес Склад"

# --- Категории (BR-004) ---
CATEGORY_COFFEE_TEA: Final[str] = "Кофе и чай"
CATEGORY_GROCERY: Final[str] = "Бакалея"
CATEGORY_DRINKS: Final[str] = "Напитки"

# --- Товары (корпоративный прайс, ANS-09) ---
PRODUCT_COFFEE_NAME: Final[str] = "Кофе Lavazza Crema 250 г"
PRODUCT_COFFEE_PRICE: Final[str] = "1200 ₽"
PRODUCT_COFFEE_PRICE_VALUE: Final[int] = 1200

PRODUCT_TEA_NAME: Final[str] = "Чай Greenfield Sencha 100 пакетиков"
PRODUCT_TEA_PRICE: Final[str] = "450 ₽"
PRODUCT_TEA_PRICE_VALUE: Final[int] = 450

PRODUCT_SUGAR_NAME: Final[str] = "Сахар-песок 1 кг"
PRODUCT_SUGAR_PRICE: Final[str] = "80 ₽"
PRODUCT_SUGAR_PRICE_VALUE: Final[int] = 80

PRODUCT_WATER_NAME: Final[str] = "Минеральная вода «Ессентуки» 0,5 л, 12 шт."

# --- Суммы и скидки (ANS-23, BR-014) ---
TOTAL_BEFORE_DISCOUNT: Final[str] = "1730 ₽"
TOTAL_BEFORE_DISCOUNT_VALUE: Final[int] = 1730

DISCOUNT_PCT: Final[str] = "15 %"
DISCOUNT_PCT_VALUE: Final[int] = 15
DISCOUNT_AMOUNT: Final[str] = "259.50 ₽"
DISCOUNT_AMOUNT_VALUE: Final[float] = 259.50

TOTAL_AFTER_DISCOUNT: Final[str] = "1470.50 ₽"
TOTAL_AFTER_DISCOUNT_VALUE: Final[float] = 1470.50

# --- Расчёт доставки (BR-009) ---
DELIVERY_FEE: Final[str] = "98 ₽"
DELIVERY_FEE_VALUE: Final[int] = 98
ASSEMBLY_FEE: Final[str] = "29 ₽"
ASSEMBLY_FEE_VALUE: Final[int] = 29

TOTAL_TO_PAY: Final[str] = "1597.50 ₽"
TOTAL_TO_PAY_VALUE: Final[float] = 1597.50

# --- Доставка (BR-008, ANS-24) ---
DELIVERY_RECIPIENT: Final[str] = "Анна Петрова"
DELIVERY_ADDRESS: Final[str] = "г. Москва, ул. Корпоративная, д. 10, офис 5"
DELIVERY_TIME: Final[str] = "14:30"
DELIVERY_METHOD: Final[str] = "Доставка курьером"

# --- Способ оплаты (ANS-26) ---
PAYMENT_METHOD_LABEL: Final[str] = "безналичный расчёт"

# --- Корзина для TC-J03-02 (BR-004, BR-005, ANS-25) ---
CART_SUM_TWO_ITEMS: Final[str] = "1280 ₽"
CART_SUM_TWO_ITEMS_VALUE: Final[int] = 1280

SUGAR_NEW_QUANTITY: Final[int] = 2
SUGAR_NEW_POSITION_PRICE: Final[str] = "160 ₽"
SUGAR_NEW_POSITION_PRICE_VALUE: Final[int] = 160

CART_SUM_AFTER_QUANTITY_CHANGE: Final[str] = "1360 ₽"
CART_SUM_AFTER_QUANTITY_CHANGE_VALUE: Final[int] = 1360

# --- Счётчики позиций корзины ---
CART_POSITIONS_AFTER_FIRST_ADD: Final[int] = 1
CART_POSITIONS_AFTER_TWO_ADDS: Final[int] = 2
CART_POSITIONS_AFTER_THREE_ADDS: Final[int] = 3

# --- Сбер ID (BR-001, ANS-13) ---
SBER_ID_AUTH_OPTION: Final[str] = "Войти через Сбер ID"
