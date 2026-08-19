"""
test_data.py — typed constants for J02-reorder-from-history.

Source: output/cases/J02-reorder-from-history/TC-*.md (8 cases, 42 steps)
+ input/requirements/kuper.md and _answers.md.
"""
from __future__ import annotations

from typing import Final

# === Brand / store ===
STORE_NAME: Final[str] = "Купер Маркет Тверская"
DELIVERY_METHOD: Final[str] = "Доставка курьером"

# === Auth options (BR-001) ===
AUTH_OPTION_SBER_ID: Final[str] = "Сбер ID"
AUTH_OPTION_PHONE: Final[str] = "по номеру телефона"

# === Order 4711 — completed source order (BR-012, ANS-10, ANS-12) ===
ORDER_NUMBER_4711: Final[str] = "4711"
ORDER_DATE_4711: Final[str] = "2026-08-15"
ORDER_STATUS_DELIVERED: Final[str] = "Доставлен"

# New order (after reorder)
NEW_ORDER_NUMBER: Final[str] = "4712"
NEW_ORDER_DATE: Final[str] = "2026-08-18"
NEW_ORDER_STATUS: Final[str] = "Создан"

# === Additional orders for variants ===
# TC-J02-01 — cancelled order
ORDER_NUMBER_4720: Final[str] = "4720"
ORDER_DATE_4720: Final[str] = "2026-08-12"
ORDER_STATUS_CANCELLED: Final[str] = "Отменён"

# TC-J02-02 — three orders for sort check
ORDER_NUMBER_4700: Final[str] = "4700"
ORDER_DATE_4700: Final[str] = "2026-07-10"
ORDER_NUMBER_4710: Final[str] = "4710"
ORDER_DATE_4710: Final[str] = "2026-08-01"

# === Source order delivery data (ANS-07, BR-008) ===
DELIVERY_ADDRESS: Final[str] = "г. Москва, ул. Тверская, д. 1, кв. 5"
RECIPIENT_NAME: Final[str] = "Иван Иванов"
DELIVERY_INTERVAL: Final[str] = "20–45 мин"

# === Source order 4711 items (BR-004, BR-012) ===
# Item 1 — Milk (price changes)
PRODUCT_MILK: Final[str] = "Молоко Простоквашино 3,2% 0,9 л"
PRODUCT_MILK_OLD_PRICE: Final[str] = "95 ₽"
PRODUCT_MILK_NEW_PRICE: Final[str] = "100 ₽"

# Item 2 — Bananas (unavailable, replacement available)
PRODUCT_BANANA: Final[str] = "Бананы 1 кг"
PRODUCT_BANANA_PRICE: Final[str] = "130 ₽"
PRODUCT_BANANA_REPLACEMENT: Final[str] = "Бананы Эквадор 1 кг"
PRODUCT_BANANA_REPLACEMENT_PRICE: Final[str] = "135 ₽"

# Item 3 — Apples (partial availability in TC-J02-05)
PRODUCT_APPLE: Final[str] = "Яблоки Гренни Смит 1 кг"
PRODUCT_APPLE_PRICE: Final[str] = "110 ₽"

# === Partial availability — TC-J02-05 (ANS-21) ===
APPLE_ORIGINAL_QTY: Final[int] = 3
APPLE_AVAILABLE_QTY: Final[int] = 1
APPLE_EXCLUDED_QTY: Final[int] = 2

# === Cost components (BR-009) ===
DELIVERY_FEE: Final[str] = "98 ₽"
PACKING_FEE: Final[str] = "29 ₽"

# === Cart totals ===
# After all confirmations (TC-J02-00 step 9)
CART_TOTAL_AFTER_CONFIRM: Final[str] = "345 ₽"
# After removing Bananas Ecuador (TC-J02-07)
CART_TOTAL_AFTER_REMOVAL: Final[str] = "210 ₽"

# === Order grand total (BR-009) ===
GRAND_TOTAL: Final[str] = "472 ₽"           # 345 + 98 + 29

# === Bonus and payment (ANS-03, BR-010) ===
BONUS_LABEL: Final[str] = "СберСпасибо"
BONUS_AMOUNT: Final[int] = 400
CARD_PAYMENT: Final[str] = "72 ₽"           # 472 - 400

# === Order stages (BR-011) ===
# Stages: creation -> assembly -> courier handoff -> delivery -> completion
ORDER_STAGE_CREATED: Final[str] = "создание"
