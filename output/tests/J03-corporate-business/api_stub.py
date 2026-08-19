"""
Детерминированная эмуляция API корпоративного портала «Купер для бизнеса».

Один метод — одно REQ-действие. Состояние хранится в памяти объекта;
метод reset() возвращает стаб к начальному состоянию.

Покрываемые требования:
- BR-001: единый вход через Сбер ID
- BR-003 / ANS-25: корзина в рамках одного магазина
- BR-004: добавление товаров
- BR-005: пересчёт корзины при изменении количества
- BR-008: выбор способа получения
- BR-009: комиссия доставки и сборка
- BR-014: корпоративные тарифы, безналичный расчёт, выделенный курьер, точное время
- ANS-09: отдельный корпоративный портал с корпоративными ценами
- ANS-13: Сбер ID — единый вход
- ANS-22: тарифы из списка с названием и ценой
- ANS-23: скидка до 15 % после активации
- ANS-24: точное время доставки
- ANS-26: метка «безналичный расчёт», без формы карты
"""

from __future__ import annotations

from typing import Any

from test_data import (
    ASSEMBLY_FEE,
    ASSEMBLY_FEE_VALUE,
    CATEGORY_COFFEE_TEA,
    CATEGORY_DRINKS,
    CATEGORY_GROCERY,
    DELIVERY_ADDRESS,
    DELIVERY_FEE,
    DELIVERY_FEE_VALUE,
    DELIVERY_METHOD,
    DELIVERY_RECIPIENT,
    DELIVERY_TIME,
    DISCOUNT_AMOUNT_VALUE,
    DISCOUNT_PCT_VALUE,
    PAYMENT_METHOD_LABEL,
    PRODUCT_COFFEE_NAME,
    PRODUCT_COFFEE_PRICE_VALUE,
    PRODUCT_SUGAR_NAME,
    PRODUCT_SUGAR_PRICE_VALUE,
    PRODUCT_TEA_NAME,
    PRODUCT_TEA_PRICE_VALUE,
    PRODUCT_WATER_NAME,
    SBER_ID_AUTH_OPTION,
    STORE_MARKET,
    STORE_WAREHOUSE,
    TARIFF_NAME_STANDARD,
    TOTAL_AFTER_DISCOUNT_VALUE,
    TOTAL_BEFORE_DISCOUNT_VALUE,
    TOTAL_TO_PAY_VALUE,
)


# Каталог известных товаров с ценами за единицу.
_UNIT_PRICES: dict[str, int] = {
    PRODUCT_COFFEE_NAME: PRODUCT_COFFEE_PRICE_VALUE,
    PRODUCT_TEA_NAME: PRODUCT_TEA_PRICE_VALUE,
    PRODUCT_SUGAR_NAME: PRODUCT_SUGAR_PRICE_VALUE,
}


class CorporateApiStub:
    """Состояние сессии представителя компании в «Купер для бизнеса»."""

    def __init__(self) -> None:
        self.reset()

    # ------------------------------------------------------------------
    # Сброс
    # ------------------------------------------------------------------
    def reset(self) -> None:
        self.portal_open: bool = False
        self.authenticated: bool = False
        self.sber_id_window_open: bool = False
        self.tariff_selected: str | None = None
        self.tariff_list: list[dict[str, Any]] = []
        self.catalog_open: bool = False
        self.discount_active: bool = False
        self.cart: list[dict[str, Any]] = []
        self.cart_store: str | None = None
        self.checkout_form_open: bool = False
        self.delivery_address: str | None = None
        self.delivery_recipient: str | None = None
        self.delivery_time: str | None = None
        self.delivery_method: str | None = None
        self.last_order_id: str | None = None
        self.order_status: str | None = None
        self.cross_store_attempt_blocked: bool = False

    # ------------------------------------------------------------------
    # BR-001 / ANS-09 / ANS-13 — вход через Сбер ID
    # ------------------------------------------------------------------
    def open_portal(self) -> dict[str, Any]:
        """Открыть корпоративный портал (ANS-09). Возвращает экран входа."""
        self.portal_open = True
        return {
            "screen": "corporate_login",
            "auth_options": [SBER_ID_AUTH_OPTION],
        }

    def select_sber_id_auth(self) -> dict[str, Any]:
        """Шаг 2 TC-J03-00: выбор варианта Сбер ID (ANS-13)."""
        if not self.portal_open:
            return {"error": "portal_not_open"}
        self.sber_id_window_open = True
        return {"screen": "sber_id_auth"}

    def confirm_sber_id_auth(self) -> dict[str, Any]:
        """Шаг 3 TC-J03-00: подтверждение авторизации (BR-001, ANS-13)."""
        if not self.sber_id_window_open:
            return {"error": "sber_id_window_not_open"}
        self.sber_id_window_open = False
        self.authenticated = True
        return {
            "screen": "corporate_home",
            "session": "active",
        }

    # ------------------------------------------------------------------
    # ANS-22 — корпоративные тарифы
    # ------------------------------------------------------------------
    def list_corporate_tariffs(self) -> dict[str, Any]:
        """Шаг 4 TC-J03-00: список готовых тарифов с названием и ценой."""
        if not self.authenticated:
            return {"error": "not_authenticated"}
        self.tariff_list = [
            {"name": "Базовый", "price": "0 ₽"},
            {"name": TARIFF_NAME_STANDARD, "price": "5000 ₽"},
            {"name": "Премиум", "price": "15000 ₽"},
        ]
        return {"tariffs": list(self.tariff_list)}

    def select_corporate_tariff(self, tariff_name: str) -> dict[str, Any]:
        """Шаг 5 TC-J03-00: выбор тарифа, открытие корпоративного каталога."""
        if not self.tariff_list:
            return {"error": "tariff_list_not_opened"}
        if tariff_name not in {t["name"] for t in self.tariff_list}:
            return {"error": "tariff_not_found"}
        self.tariff_selected = tariff_name
        self.catalog_open = True
        return {
            "selected_tariff": tariff_name,
            "screen": "corporate_catalog",
        }

    # ------------------------------------------------------------------
    # ANS-09 — корпоративный каталог
    # ------------------------------------------------------------------
    def get_corporate_catalog(self) -> dict[str, Any]:
        """Шаг 6 TC-J03-00: состав каталога с корпоративными ценами."""
        if not self.catalog_open:
            return {"error": "catalog_not_open"}
        return {
            "stores": [
                {
                    "name": STORE_MARKET,
                    "categories": [
                        {
                            "name": CATEGORY_COFFEE_TEA,
                            "products": [PRODUCT_COFFEE_NAME, PRODUCT_TEA_NAME],
                        },
                        {"name": CATEGORY_GROCERY, "products": [PRODUCT_SUGAR_NAME]},
                    ],
                },
                {
                    "name": STORE_WAREHOUSE,
                    "categories": [
                        {"name": CATEGORY_DRINKS, "products": [PRODUCT_WATER_NAME]},
                    ],
                },
            ],
        }

    # ------------------------------------------------------------------
    # BR-004 — добавление товаров
    # BR-003 / ANS-25 — ограничение «корзина в рамках одного магазина»
    # ------------------------------------------------------------------
    def add_to_cart(self, store: str, product: str, qty: int = 1) -> dict[str, Any]:
        """Добавить товар в корзину (BR-004).

        Если в корзине уже есть товары из другого магазина — попытка
        добавления блокируется согласно BR-003 / ANS-25, флаг
        ``cross_store_attempt_blocked`` устанавливается в True, корзина
        остаётся без изменений.
        """
        # 1) Проверка ограничения «один магазин» идёт ДО проверки цены товара:
        # так попытка добавления из чужого магазина всегда вызывает блокировку.
        if self.cart_store is not None and self.cart_store != store:
            self.cross_store_attempt_blocked = True
            return {
                "added": False,
                "blocked_by": "single_store_constraint",
                "cart_store": self.cart_store,
                "attempted_store": store,
                "attempted_product": product,
            }
        if product not in _UNIT_PRICES:
            return {"error": "unknown_product"}
        if self.cart_store is None:
            self.cart_store = store
        # объединить, если уже есть
        for line in self.cart:
            if line["product"] == product:
                line["qty"] += qty
                line["price"] = _UNIT_PRICES[product] * line["qty"]
                return self._cart_payload()
        self.cart.append(
            {
                "store": store,
                "product": product,
                "qty": qty,
                "price": _UNIT_PRICES[product] * qty,
            }
        )
        return self._cart_payload()

    def _cart_payload(self) -> dict[str, Any]:
        return {
            "store": self.cart_store,
            "lines": list(self.cart),
            "positions_count": len(self.cart),
            "sum": sum(line["price"] for line in self.cart),
        }

    def get_cart(self) -> dict[str, Any]:
        """Шаги 7–10 / TC-J03-02: текущее состояние корзины."""
        return self._cart_payload()

    # ------------------------------------------------------------------
    # BR-005 — изменение количества
    # ------------------------------------------------------------------
    def change_quantity(self, product: str, new_qty: int) -> dict[str, Any]:
        """Шаг 3 TC-J03-02: изменить количество позиции."""
        for line in self.cart:
            if line["product"] == product:
                line["qty"] = new_qty
                line["price"] = _UNIT_PRICES[product] * new_qty
                return self._cart_payload()
        return {"error": "product_not_in_cart"}

    # ------------------------------------------------------------------
    # ANS-23 — корпоративная скидка до 15 %
    # ------------------------------------------------------------------
    def get_order_calculation(self) -> dict[str, Any]:
        """Шаги 10, 12, 17: блок расчёта заказа."""
        items_sum = sum(line["price"] for line in self.cart)
        if self.discount_active:
            discount_value = round(items_sum * DISCOUNT_PCT_VALUE / 100, 2)
            items_after = round(items_sum - discount_value, 2)
            total = round(items_after + DELIVERY_FEE_VALUE + ASSEMBLY_FEE_VALUE, 2)
            return {
                "items_sum": items_sum,
                "discount": {
                    "active": True,
                    "pct": DISCOUNT_PCT_VALUE,
                    "value": discount_value,
                },
                "items_after_discount": items_after,
                "delivery_fee": DELIVERY_FEE_VALUE,
                "assembly_fee": ASSEMBLY_FEE_VALUE,
                "total": total,
            }
        return {
            "items_sum": items_sum,
            "discount": {"active": False},
            "items_after_discount": None,
            "delivery_fee": DELIVERY_FEE_VALUE,
            "assembly_fee": ASSEMBLY_FEE_VALUE,
            "total": None,
        }

    def activate_corporate_discount(self) -> dict[str, Any]:
        """Шаг 11 / TC-J03-01 шаг 2: активация скидки."""
        if not self.tariff_selected:
            return {"error": "tariff_not_selected"}
        self.discount_active = True
        return self.get_order_calculation()

    # ------------------------------------------------------------------
    # ANS-26 — безналичный расчёт
    # ------------------------------------------------------------------
    def open_checkout_form(self) -> dict[str, Any]:
        """Шаг 13 / TC-J03-04 шаг 1: открыть форму оформления."""
        self.checkout_form_open = True
        return {
            "screen": "checkout_form",
            "payment_label": PAYMENT_METHOD_LABEL,
            "card_form_visible": False,
        }

    # ------------------------------------------------------------------
    # BR-008, ANS-24 — параметры доставки
    # ------------------------------------------------------------------
    def get_delivery_form(self) -> dict[str, Any]:
        """Шаг 14 / TC-J03-03 шаг 1: блок параметров доставки."""
        return {
            "fields": ["address", "recipient", "time"],
            "methods": [
                {
                    "name": DELIVERY_METHOD,
                    "dedicated_courier": True,
                }
            ],
            "time_options": {
                "exact_values_present": True,
                "interval_values_present": False,
                "sample": [
                    "09:00",
                    "10:00",
                    "11:00",
                    "12:00",
                    "13:00",
                    "14:30",
                    "15:00",
                    "16:00",
                ],
            },
        }

    def fill_delivery_fields(self, address: str, recipient: str) -> dict[str, Any]:
        """Шаг 15 / TC-J03-03 шаг 2: заполнить адрес и получателя."""
        self.delivery_address = address
        self.delivery_recipient = recipient
        return {
            "address": self.delivery_address,
            "recipient": self.delivery_recipient,
        }

    def select_delivery_time(self, time_value: str) -> dict[str, Any]:
        """Шаг 16 / TC-J03-03 шаг 4: выбор точного времени."""
        self.delivery_time = time_value
        return {
            "selected_time": self.delivery_time,
        }

    # ------------------------------------------------------------------
    # BR-014 — подтверждение заказа
    # ------------------------------------------------------------------
    def confirm_order(self) -> dict[str, Any]:
        """Шаг 18 TC-J03-00: подтверждение и создание корпоративного заказа."""
        if not self.checkout_form_open:
            return {"error": "checkout_form_not_open"}
        if not self.delivery_time or not self.delivery_address or not self.delivery_recipient:
            return {"error": "delivery_fields_incomplete"}
        self.last_order_id = "KUPER-CORP-000123"
        self.order_status = "Создан"
        self.delivery_method = DELIVERY_METHOD
        # корзина перенесена в заказ
        self.cart = []
        self.cart_store = None
        self.discount_active = False
        return {
            "order_id": self.last_order_id,
            "status": self.order_status,
            "store": STORE_MARKET,
            "address": self.delivery_address,
            "recipient": self.delivery_recipient,
            "time": self.delivery_time,
            "payment_method": PAYMENT_METHOD_LABEL,
            "dedicated_courier": True,
        }
