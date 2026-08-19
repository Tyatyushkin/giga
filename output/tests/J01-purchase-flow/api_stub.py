"""
Детерминированная эмуляция API веб-версии «Купера».

Один метод — одно REQ-действие. Состояние хранится в памяти объекта;
метод reset() возвращает стаб к начальному состоянию.

Покрываемые требования:
- BR-001: вход через Сбер ID или по номеру телефона и коду
- BR-002 / BR-N01: ввод нового адреса, проверка зоны обслуживания
- BR-003 / ANS-01: выбор магазина, корзина в рамках одного магазина,
  смена адреса сохраняет корзину
- BR-004 / BR-N07 / ANS-18: поиск, добавление товаров, недоступные товары
- BR-005: управление корзиной (изменение количества, удаление)
- BR-006 / BR-N02: валидный/невалидный промокод
- BR-007 / ANS-03: бонусы «СберСпасибо» (до 99 %)
- BR-008 / ANS-04 / ANS-17: выбор способа получения и интервалов
- BR-009 / ANS-02: комиссия доставки 98 ₽ и сборка 29 ₽
- BR-010 / ANS-11 / ANS-28: оплата картой или бонусами
- BR-011 / ANS-10 / ANS-27: отслеживание заказа, курьер на карте
- BR-013: выход и повторный вход
- BR-N03 / ANS-14: минимальная сумма корзины
- BR-N04 / ANS-15: превышение веса заказа
- BR-N06: истечение срока оплаты
- ANS-19: 3 попытки ввода кода, 3 минуты срок действия
"""

from __future__ import annotations

from typing import Any

from test_data import (
    ADDRESS_ARBAT,
    ADDRESS_OUT_OF_ZONE,
    ADDRESS_TVERSKAYA,
    ASSEMBLY_FEE_VALUE,
    ATTEMPTS_AFTER_1_FAIL,
    ATTEMPTS_AFTER_2_FAIL,
    BANANA_LINE_PRICE_6,
    BANANA_QTY_1,
    BANANA_QTY_11,
    BANANA_QTY_6,
    CART_POSITIONS_LARGE,
    CART_POSITIONS_THRESHOLD,
    CART_SUM_ABOVE_THRESHOLD,
    CART_SUM_AFTER_BONUSES_BOUNDARY,
    CART_SUM_AFTER_BONUSES_MAIN,
    CART_SUM_AFTER_CHOCOLATE_ADD,
    CART_SUM_AFTER_PROMO,
    CART_SUM_INITIAL,
    CART_TOTAL_WEIGHT_KG,
    CASH_DUE_TO_COURIER,
    CHOCOLATE_LINE_PRICE_1,
    CHOCOLATE_QTY_1,
    CODE_VALIDITY_MINUTES,
    CORRECT_CODE,
    COURIER_COMMENT,
    DELIVERY_FEE_VALUE,
    DELIVERY_INTERVAL_DEFAULT,
    DELIVERY_INTERVAL_LARGE,
    DELIVERY_METHOD_COURIER,
    MAX_ATTEMPTS,
    MILK_LINE_PRICE_1,
    MILK_LINE_PRICE_5,
    MILK_LINE_PRICE_8,
    MILK_QTY_1,
    MILK_QTY_5,
    MILK_QTY_8,
    MIN_ORDER_SUM,
    MIN_STORES_AVAILABLE,
    ORDER_STATUS_AUTOCANCELLED,
    ORDER_STATUS_CREATED,
    ORDER_STATUS_DELIVERED,
    PAYMENT_METHOD_BONUSES,
    PAYMENT_METHOD_CARD,
    PHONE_NUMBER,
    PRODUCT_BANANA,
    PRODUCT_CHOCOLATE,
    PRODUCT_MILK,
    PRODUCT_MILK_PRICE,
    PRODUCT_MILK_WEIGHT_KG,
    PRODUCT_PEAR_UNAVAILABLE,
    PROMO_CODE_INVALID,
    PROMO_CODE_VALID,
    PROMO_DISCOUNT_AMOUNT,
    PROMO_DISCOUNT_PCT,
    RECIPIENT_NAME,
    SEARCH_QUERY_EMPTY,
    SEARCH_QUERY_MILK,
    SEARCH_QUERY_PEAR,
    STORE_ARBAT,
    STORE_TVERSKAYA,
    UNAVAILABLE_BADGE,
    WEIGHT_LIMIT_KG,
    WRONG_CODE,
)


# Каталог известных товаров с ценой и весом за единицу.
_CATALOG: dict[str, dict[str, Any]] = {
    PRODUCT_MILK: {"price": PRODUCT_MILK_PRICE, "weight": PRODUCT_MILK_WEIGHT_KG},
    PRODUCT_BANANA: {"price": 130, "weight": 1.0},
    PRODUCT_CHOCOLATE: {"price": 99, "weight": 0.2},
}

# Список магазинов для тестового адреса.
_STORES_FOR_TVERSKAYA: Final[list[str]] = [STORE_TVERSKAYA, STORE_ARBAT]


class KuperApiStub:
    """Состояние сессии пользователя в веб-версии «Купера»."""

    def __init__(self) -> None:
        self.reset()

    # ------------------------------------------------------------------
    # Сброс
    # ------------------------------------------------------------------
    def reset(self) -> None:
        # Авторизация
        self.login_screen_open: bool = False
        self.sber_id_window_open: bool = False
        self.authenticated: bool = False
        self.has_sber_card: bool = True
        self.last_phone: str | None = None

        # SMS-код (TC-J01-12, ANS-19)
        self.sms_code_sent: bool = False
        self.sms_attempts_left: int = MAX_ATTEMPTS
        self.sms_validity_active: bool = False
        self.last_wrong_code: str | None = None

        # Адрес / магазин
        self.current_address: str | None = None
        self.current_store: str | None = None
        self.available_stores: list[str] = []
        self.address_form_open: bool = False

        # Поиск / каталог
        self.search_query: str | None = None
        self.search_results: list[str] = []
        self.unavailable_in_results: list[str] = []
        self.catalog_open: bool = False

        # Корзина
        self.cart: list[dict[str, Any]] = []
        self.cart_store: str | None = None

        # Промокод
        self.promo_code: str | None = None
        self.promo_discount_amount: int = 0
        self.promo_error: str | None = None

        # Бонусы
        self.bonus_balance: int = 5000
        self.bonus_spent: int = 0

        # Оформление / доставка
        self.checkout_form_open: bool = False
        self.delivery_intervals: list[str] = []
        self.delivery_method: str | None = None
        self.delivery_interval: str | None = None
        self.delivery_recipient: str | None = None
        self.delivery_comment: str | None = None

        # Оплата и заказ
        self.payment_methods: list[str] = []
        self.pay_success_screen_open: bool = False
        self.last_order_id: str | None = None
        self.order_status: str | None = None
        self.order_history: list[dict[str, Any]] = []
        self.order_amount_total: int | None = None
        self.order_amount_items: int | None = None
        self.order_address: str | None = None
        self.order_interval: str | None = None
        self.order_recipient: str | None = None
        self.order_partial_payment: bool = False
        self.order_cash_due: int | None = None

        # Отслеживание
        self.tracking_open: bool = False
        self.courier_name: str | None = None
        self.courier_on_map: bool = False

        # BR-N01 / BR-N03 / BR-N04 / BR-N06 — состояния ошибок
        self.address_out_of_zone: bool = False
        self.address_out_of_zone_message_visible: bool = False
        self.address_out_of_zone_cta_visible: bool = False
        self.min_sum_warning_visible: bool = False
        self.checkout_button_blocked_min_sum: bool = False
        self.weight_warning_visible: bool = False
        self.courier_blocked: bool = False
        self.alternative_methods_offered: bool = False
        self.payment_deadline_expired: bool = False
        self.autocancel_message_visible: bool = False
        self.new_order_cta_visible: bool = False

    # ------------------------------------------------------------------
    # BR-001 — экран входа
    # ------------------------------------------------------------------
    def open_login_screen(self) -> dict[str, Any]:
        """Шаг 1 TC-J01-00 / шаг 1 TC-J01-12: экран входа с двумя вариантами."""
        self.login_screen_open = True
        return {
            "screen": "login",
            "auth_options": ["sber_id", "phone"],
        }

    def select_sber_id_auth(self) -> dict[str, Any]:
        """Шаг 2 TC-J01-00: нажата кнопка авторизации через Сбер ID."""
        if not self.login_screen_open:
            return {"error": "login_screen_not_open"}
        self.sber_id_window_open = True
        return {"screen": "sber_id_auth"}

    def confirm_sber_id_auth(self) -> dict[str, Any]:
        """Шаг 3 TC-J01-00: подтверждение входа через Сбер ID."""
        if not self.sber_id_window_open:
            return {"error": "sber_id_window_not_open"}
        self.sber_id_window_open = False
        self.authenticated = True
        return {"screen": "home", "session": "active"}

    # ------------------------------------------------------------------
    # TC-J01-12 — авторизация по номеру телефона (BR-001, ANS-19)
    # ------------------------------------------------------------------
    def select_phone_auth(self) -> dict[str, Any]:
        """Шаг 2 TC-J01-12: нажата кнопка авторизации по номеру телефона."""
        if not self.login_screen_open:
            return {"error": "login_screen_not_open"}
        return {"screen": "phone_auth_form"}

    def enter_phone(self, phone: str) -> dict[str, Any]:
        """Шаг 3 TC-J01-12: ввод номера телефона."""
        self.last_phone = phone
        return {
            "phone": phone,
            "code_request_button_enabled": True,
        }

    def request_sms_code(self) -> dict[str, Any]:
        """Шаг 4 TC-J01-12: запрос SMS-кода.

        SMS отправлен, открыт экран ввода кода, индикатор срока действия
        активен (3 минуты), счётчик попыток установлен в 3.
        """
        self.sms_code_sent = True
        self.sms_attempts_left = MAX_ATTEMPTS
        self.sms_validity_active = True
        return {
            "sms_sent_to": self.last_phone,
            "screen": "code_input",
            "validity_minutes": CODE_VALIDITY_MINUTES,
            "attempts_left": self.sms_attempts_left,
        }

    def enter_sms_code(self, code: str) -> dict[str, Any]:
        """Шаги 5–7, 9 TC-J01-12: ввод кода.

        При неверном коде — уменьшает счётчик попыток, при исчерпании —
        блокирует поле и показывает кнопку повторного запроса.
        При корректном — авторизует.
        """
        if not self.sms_code_sent:
            return {"error": "no_code_sent"}
        if self.sms_attempts_left <= 0:
            return {"error": "attempts_exhausted"}
        if code == CORRECT_CODE:
            self.sms_validity_active = False
            self.authenticated = True
            return {"authenticated": True, "screen": "home"}
        # Неверный код
        self.sms_attempts_left -= 1
        self.last_wrong_code = code
        if self.sms_attempts_left <= 0:
            self.sms_validity_active = False
            return {
                "error": "attempts_exhausted",
                "code_input_blocked": True,
                "resend_button_enabled": True,
            }
        return {
            "error": "wrong_code",
            "attempts_left": self.sms_attempts_left,
        }

    def resend_sms_code(self) -> dict[str, Any]:
        """Шаг 8 TC-J01-12: повторный запрос SMS-кода.

        Отправлен новый SMS, счётчик попыток сброшен до 3, индикатор срока
        действия снова активен.
        """
        self.sms_code_sent = True
        self.sms_attempts_left = MAX_ATTEMPTS
        self.sms_validity_active = True
        return {
            "sms_sent_to": self.last_phone,
            "screen": "code_input",
            "validity_minutes": CODE_VALIDITY_MINUTES,
            "attempts_left": self.sms_attempts_left,
            "counter_reset": True,
        }

    # ------------------------------------------------------------------
    # BR-002 — ввод нового адреса, проверка зоны
    # BR-N01 — адрес вне зоны
    # ------------------------------------------------------------------
    def open_address_form(self) -> dict[str, Any]:
        """Шаг 4 TC-J01-00: открыта форма ввода адреса."""
        self.address_form_open = True
        return {
            "screen": "address_form",
            "fields": ["city", "street", "house", "apartment"],
        }

    def enter_address(self, address: str) -> dict[str, Any]:
        """Шаг 5 TC-J01-00 / шаг 2 TC-J01-01: ввод адреса.

        Если адрес вне зоны (TC-J01-01) — устанавливает флаги ошибки
        и НЕ открывает список магазинов.
        """
        self.address_out_of_zone = False
        self.address_out_of_zone_message_visible = False
        self.address_out_of_zone_cta_visible = False

        if address == ADDRESS_OUT_OF_ZONE:
            self.current_address = address
            self.address_out_of_zone = True
            self.address_out_of_zone_message_visible = True
            self.address_out_of_zone_cta_visible = True
            self.available_stores = []
            return {
                "out_of_zone": True,
                "message_visible": True,
                "change_address_cta_visible": True,
                "alternative_methods_offered": True,
            }

        # Адрес в зоне
        self.current_address = address
        if address == ADDRESS_TVERSKAYA:
            self.available_stores = list(_STORES_FOR_TVERSKAYA)
        elif address == ADDRESS_ARBAT:
            self.available_stores = [STORE_ARBAT, STORE_TVERSKAYA]
        else:
            self.available_stores = [STORE_TVERSKAYA]
        return {
            "available_stores": list(self.available_stores),
            "stores_count": len(self.available_stores),
        }

    # ------------------------------------------------------------------
    # BR-003 / ANS-01 — выбор магазина, смена адреса
    # ------------------------------------------------------------------
    def select_store(self, store_name: str) -> dict[str, Any]:
        """Шаг 6 TC-J01-00 / шаг 3 TC-J01-02: выбор магазина.

        При смене адреса (TC-J01-02) — корзина сохраняется, меняется только
        магазин.
        """
        if store_name not in self.available_stores:
            return {"error": "store_not_available"}
        previous_store = self.current_store
        self.current_store = store_name
        self.cart_store = store_name
        self.catalog_open = True
        return {
            "store": store_name,
            "previous_store": previous_store,
            "cart_preserved": True,
            "screen": "catalog",
        }

    def get_catalog(self) -> dict[str, Any]:
        """Шаг 6 TC-J01-00: состав каталога выбранного магазина."""
        return {
            "store": self.current_store,
            "products": list(_CATALOG.keys()),
            "categories": ["Молочные", "Фрукты", "Сладости"],
        }

    # ------------------------------------------------------------------
    # BR-004 / BR-N07 / ANS-18 — поиск
    # ------------------------------------------------------------------
    def open_search(self) -> dict[str, Any]:
        """Шаг 7 TC-J01-00: открыт раздел поиска."""
        self.search_query = None
        self.search_results = []
        self.unavailable_in_results = []
        return {
            "screen": "search",
            "input_visible": True,
            "results_empty": True,
        }

    def search(self, query: str) -> dict[str, Any]:
        """Шаги 8–9 TC-J01-00 / шаги 1–2 TC-J01-03: поиск товаров.

        Поддерживаемые запросы:
        - SEARCH_QUERY_MILK → [PRODUCT_MILK]
        - SEARCH_QUERY_PEAR → [PRODUCT_PEAR_UNAVAILABLE] (недоступен, ANS-18)
        - SEARCH_QUERY_EMPTY → [] (BR-N07)
        - любая строка с "Банан" или слагаемое Бананы → [PRODUCT_BANANA]
        - любая строка с "Шоколад" → [PRODUCT_CHOCOLATE]
        """
        self.search_query = query
        self.search_results = []
        self.unavailable_in_results = []

        if query == SEARCH_QUERY_EMPTY:
            return {"results": [], "unavailable": [], "found_count": 0}

        if query == SEARCH_QUERY_MILK or "Молоко" in query:
            self.search_results = [PRODUCT_MILK]
        elif query == SEARCH_QUERY_PEAR or "Груши" in query:
            self.unavailable_in_results = [PRODUCT_PEAR_UNAVAILABLE]
        elif "Банан" in query:
            self.search_results = [PRODUCT_BANANA]
        elif "Шоколад" in query:
            self.search_results = [PRODUCT_CHOCOLATE]

        return {
            "results": list(self.search_results),
            "unavailable": list(self.unavailable_in_results),
            "found_count": len(self.search_results) + len(self.unavailable_in_results),
        }

    def get_unavailable_card_state(self, product: str) -> dict[str, Any]:
        """Шаг 9 TC-J01-00: состояние карточки недоступного товара (ANS-18)."""
        if product in self.unavailable_in_results:
            return {
                "product": product,
                "dimmed": True,
                "badge": UNAVAILABLE_BADGE,
                "add_to_cart_available": False,
            }
        return {"error": "product_available"}

    # ------------------------------------------------------------------
    # BR-004 — добавление товара в корзину
    # BR-005 — изменение количества и удаление
    # ------------------------------------------------------------------
    def add_to_cart(self, product: str, qty: int = 1) -> dict[str, Any]:
        """Шаги 10–14 TC-J01-00: добавить товар в корзину.

        Если товар из каталога — добавляется. Если уже есть — инкремент.
        """
        if product not in _CATALOG:
            return {"error": "unknown_product"}
        if self.cart_store is None:
            self.cart_store = self.current_store
        for line in self.cart:
            if line["product"] == product:
                line["qty"] += qty
                line["price"] = _CATALOG[product]["price"] * line["qty"]
                return self._cart_payload()
        self.cart.append(
            {
                "product": product,
                "qty": qty,
                "price": _CATALOG[product]["price"] * qty,
            }
        )
        return self._cart_payload()

    def change_quantity(self, product: str, new_qty: int) -> dict[str, Any]:
        """Шаги 12–13 TC-J01-00: изменение количества позиции."""
        for line in self.cart:
            if line["product"] == product:
                line["qty"] = new_qty
                line["price"] = _CATALOG[product]["price"] * new_qty
                return self._cart_payload()
        return {"error": "product_not_in_cart"}

    def remove_from_cart(self, product: str) -> dict[str, Any]:
        """Шаг 15 TC-J01-00 / шаг 1 TC-J01-04: удалить позицию из корзины."""
        before = len(self.cart)
        self.cart = [line for line in self.cart if line["product"] != product]
        if len(self.cart) == before:
            return {"error": "product_not_in_cart"}
        return self._cart_payload()

    def _cart_payload(self) -> dict[str, Any]:
        return {
            "store": self.cart_store,
            "lines": list(self.cart),
            "positions_count": len(self.cart),
            "sum": sum(line["price"] for line in self.cart),
            "weight": sum(
                _CATALOG[line["product"]]["weight"] * line["qty"]
                for line in self.cart
                if line["product"] in _CATALOG
            ),
        }

    def get_cart(self) -> dict[str, Any]:
        """Текущее состояние корзины (TC-J01-04, TC-J01-07, TC-J01-08)."""
        return self._cart_payload()

    # ------------------------------------------------------------------
    # BR-005 — проверка суммы корзины
    # BR-005 / BR-N03 — минимальная сумма (TC-J01-07)
    # ------------------------------------------------------------------
    def attempt_checkout(self) -> dict[str, Any]:
        """Шаг 2 TC-J01-00 / шаги 2–3 TC-J01-07: перейти к оформлению.

        При сумме ниже MIN_ORDER_SUM — устанавливает предупреждение
        и блокирует кнопку оформления.
        """
        cart = self._cart_payload()
        if cart["sum"] < MIN_ORDER_SUM:
            self.min_sum_warning_visible = True
            self.checkout_button_blocked_min_sum = True
            return {
                "checkout_open": False,
                "min_sum_warning_visible": True,
                "checkout_button_blocked": True,
                "current_sum": cart["sum"],
                "required_sum": MIN_ORDER_SUM,
            }
        # Порог достигнут — предупреждение снято, кнопка доступна
        self.min_sum_warning_visible = False
        self.checkout_button_blocked_min_sum = False
        self.checkout_form_open = True
        return {
            "checkout_open": True,
            "min_sum_warning_visible": False,
            "checkout_button_blocked": False,
        }

    # ------------------------------------------------------------------
    # BR-006 / BR-N02 — промокод
    # ------------------------------------------------------------------
    def apply_promocode(self, code: str) -> dict[str, Any]:
        """Шаг 16 TC-J01-00 / шаги 1, 4 TC-J01-05: применить промокод.

        Валидный WELCOME15 — даёт скидку 15 % от суммы корзины.
        Невалидный — ошибка, стоимость не меняется.
        """
        self.promo_error = None
        if code == PROMO_CODE_VALID:
            items_sum = sum(line["price"] for line in self.cart)
            discount = round(items_sum * PROMO_DISCOUNT_PCT / 100)
            self.promo_code = code
            self.promo_discount_amount = discount
            return {
                "applied": True,
                "code": code,
                "discount_pct": PROMO_DISCOUNT_PCT,
                "discount_amount": discount,
                "cart_sum_after_discount": items_sum - discount,
            }
        self.promo_code = None
        self.promo_discount_amount = 0
        self.promo_error = "invalid"
        return {
            "applied": False,
            "error": "invalid",
            "cart_sum_unchanged": sum(line["price"] for line in self.cart),
        }

    def clear_promocode_field(self) -> dict[str, Any]:
        """Шаг 3 TC-J01-05: очистка поля ввода после ошибки."""
        return {"cleared": True}

    # ------------------------------------------------------------------
    # BR-007 / ANS-03 — списание бонусов
    # ------------------------------------------------------------------
    def apply_bonuses(self, amount: int) -> dict[str, Any]:
        """Шаг 17 TC-J01-00 / шаги 1, 3 TC-J01-06: списать бонусы.

        Лимит списания — 99 % от суммы после промокода.
        При попытке ввести больше 99 % — списание усекается до 99 %.
        """
        items_after_promo = sum(line["price"] for line in self.cart) - self.promo_discount_amount
        max_spend = int(items_after_promo * 0.99)
        actual = min(amount, max_spend, self.bonus_balance)
        if actual < amount:
            # попытка превысить границу 99 % — фактическое списание усечено
            self.bonus_spent = actual
            return {
                "applied": True,
                "attempted": amount,
                "actually_spent": actual,
                "bonus_balance_after": self.bonus_balance - actual,
                "items_remaining": items_after_promo - actual,
                "limit_enforced": True,
                "max_allowed": max_spend,
            }
        self.bonus_spent = actual
        return {
            "applied": True,
            "actually_spent": actual,
            "bonus_balance_after": self.bonus_balance - actual,
            "items_remaining": items_after_promo - actual,
        }

    # ------------------------------------------------------------------
    # BR-008 / ANS-04 / ANS-17 — выбор интервала доставки
    # BR-N04 — превышение веса для курьера (TC-J01-08)
    # ------------------------------------------------------------------
    def get_delivery_options(self) -> dict[str, Any]:
        """Шаг 18 TC-J01-00 / шаг 1 TC-J01-09: список интервалов доставки.

        Если в корзине ≥ 15 позиций — добавляется рекомендация 40–60 мин
        (ANS-04).
        Если вес > 10 кг — курьерская доставка блокируется, предлагаются
        альтернативы (BR-N04).
        """
        cart = self._cart_payload()
        intervals = [DELIVERY_INTERVAL_DEFAULT]
        recommendation = None
        if cart["positions_count"] >= CART_POSITIONS_THRESHOLD:
            intervals.append(DELIVERY_INTERVAL_LARGE)
            recommendation = DELIVERY_INTERVAL_LARGE

        blocked = False
        alternatives = False
        if cart["weight"] > WEIGHT_LIMIT_KG:
            blocked = True
            alternatives = True
            self.weight_warning_visible = True
            self.courier_blocked = True
            self.alternative_methods_offered = True
        else:
            self.weight_warning_visible = False
            self.courier_blocked = False
            self.alternative_methods_offered = False

        self.delivery_intervals = intervals
        return {
            "intervals": intervals,
            "recommended_interval": recommendation,
            "default_interval": DELIVERY_INTERVAL_DEFAULT,
            "courier_available": not blocked,
            "weight_warning_visible": blocked,
            "alternative_methods_offered": alternatives,
            "current_weight": cart["weight"],
            "weight_limit": WEIGHT_LIMIT_KG,
        }

    def select_delivery_interval(self, interval: str) -> dict[str, Any]:
        """Шаг 19 TC-J01-00 / шаги 3–4 TC-J01-09: выбор интервала."""
        if interval not in self.delivery_intervals:
            return {"error": "interval_not_available"}
        self.delivery_interval = interval
        return {"selected_interval": interval}

    def select_delivery_method(self, method: str) -> dict[str, Any]:
        """Шаг 18 TC-J01-00 / шаг 2 TC-J01-08: выбор способа получения."""
        if method == DELIVERY_METHOD_COURIER and self.courier_blocked:
            return {
                "error": "courier_blocked",
                "reason": "weight_over_limit",
                "weight": self._cart_payload()["weight"],
                "limit": WEIGHT_LIMIT_KG,
            }
        self.delivery_method = method
        return {"selected_method": method}

    # ------------------------------------------------------------------
    # BR-008 — получатель, комментарий
    # ------------------------------------------------------------------
    def set_recipient(self, recipient: str) -> dict[str, Any]:
        """Шаг 20 TC-J01-00: указать получателя."""
        self.delivery_recipient = recipient
        return {"recipient": recipient}

    def set_courier_comment(self, comment: str) -> dict[str, Any]:
        """Шаг 21 TC-J01-00: комментарий курьеру."""
        self.delivery_comment = comment
        return {"comment": comment}

    # ------------------------------------------------------------------
    # BR-009 / ANS-02 — блок итогов
    # ------------------------------------------------------------------
    def get_order_summary(self) -> dict[str, Any]:
        """Шаг 22 TC-J01-00: блок итоговой стоимости заказа."""
        items_sum = sum(line["price"] for line in self.cart)
        items_after_promo = items_sum - self.promo_discount_amount
        items_after_bonuses = items_after_promo - self.bonus_spent
        total = items_after_bonuses + DELIVERY_FEE_VALUE + ASSEMBLY_FEE_VALUE
        return {
            "items_sum_after_discount_and_bonuses": items_after_bonuses,
            "delivery_fee": DELIVERY_FEE_VALUE,
            "assembly_fee": ASSEMBLY_FEE_VALUE,
            "total": total,
        }

    # ------------------------------------------------------------------
    # BR-010 / ANS-11 / ANS-28 — оплата
    # ------------------------------------------------------------------
    def get_payment_methods(self) -> dict[str, Any]:
        """Шаг 1 TC-J01-10 / шаг 23 TC-J01-00: доступные способы оплаты.

        Для клиента с картой Сбера — доступны «Карта Сбера» и «Бонусы».
        Для клиента без карты (TC-J01-10) — только «Бонусы СберСпасибо».
        """
        if self.has_sber_card:
            methods = [PAYMENT_METHOD_CARD, PAYMENT_METHOD_BONUSES]
        else:
            methods = [PAYMENT_METHOD_BONUSES]
        self.payment_methods = methods
        return {
            "methods": methods,
            "card_attached": self.has_sber_card,
        }

    def confirm_payment(self, method: str) -> dict[str, Any]:
        """Шаг 23 TC-J01-00 / шаги 3–4 TC-J01-10: подтверждение оплаты.

        Полная оплата картой — заказ создан, статус «Создан».
        Оплата бонусами без карты — заказ создан со статусом частичной
        оплаты, в деталях — остаток наличными курьеру.
        """
        if method not in self.payment_methods:
            return {"error": "payment_method_unavailable"}
        summary = self.get_order_summary()
        self.order_amount_items = summary["items_sum_after_discount_and_bonuses"]
        self.order_amount_total = summary["total"]

        if method == PAYMENT_METHOD_CARD:
            self.pay_success_screen_open = True
            self.order_partial_payment = False
            self.order_cash_due = None
            self.order_status = ORDER_STATUS_CREATED
            return {
                "pay_success_screen_open": True,
                "order_status": ORDER_STATUS_CREATED,
                "total": summary["total"],
            }

        # Оплата бонусами (частичная)
        self.pay_success_screen_open = True
        self.order_partial_payment = True
        # остаток наличными = total - bonus_spent
        cash_due = summary["total"] - self.bonus_spent
        self.order_cash_due = cash_due
        self.order_status = ORDER_STATUS_CREATED  # статус отражает частичную оплату
        return {
            "pay_success_screen_open": True,
            "order_created": True,
            "partial_payment": True,
            "cash_due_to_courier": cash_due,
            "bonus_spent": self.bonus_spent,
            "items_amount": summary["items_sum_after_discount_and_bonuses"],
            "delivery_fee": DELIVERY_FEE_VALUE,
            "assembly_fee": ASSEMBLY_FEE_VALUE,
            "screen_summary": {
                "bonus_spent": self.bonus_spent,
                "cash_due": cash_due,
                "items": summary["items_sum_after_discount_and_bonuses"],
                "delivery_fee": DELIVERY_FEE_VALUE,
                "assembly_fee": ASSEMBLY_FEE_VALUE,
            },
        }

    # ------------------------------------------------------------------
    # BR-011 / ANS-10 / ANS-27 — заказ и отслеживание
    # ------------------------------------------------------------------
    def open_created_order(self) -> dict[str, Any]:
        """Шаг 24 TC-J01-00: открыть созданный заказ."""
        order_id = "KUPER-000001"
        self.last_order_id = order_id
        self.order_address = self.current_address
        self.order_interval = self.delivery_interval
        self.order_recipient = self.delivery_recipient
        order = {
            "order_id": order_id,
            "store": self.current_store,
            "address": self.current_address,
            "interval": self.delivery_interval,
            "recipient": self.delivery_recipient,
            "status": self.order_status,
        }
        self.order_history.append(order)
        return order

    def open_tracking(self) -> dict[str, Any]:
        """Шаг 25 TC-J01-00: открыть экран отслеживания."""
        self.tracking_open = True
        self.courier_name = "Алексей Петров"
        self.courier_on_map = False
        return {
            "stages": [
                "создание",
                "сборка",
                "передача курьеру",
                "доставка",
                "завершение",
            ],
            "current_status": self.order_status,
        }

    def wait_for_status(self, target: str) -> dict[str, Any]:
        """Шаг 26 TC-J01-00: дождаться обновления статуса."""
        self.order_status = target
        if target == ORDER_STATUS_DELIVERED:
            self.courier_on_map = True
        return {
            "status": self.order_status,
            "courier_name": self.courier_name,
            "courier_on_map": self.courier_on_map,
        }

    # ------------------------------------------------------------------
    # BR-013 — выход и повторный вход
    # ------------------------------------------------------------------
    def logout(self) -> dict[str, Any]:
        """Шаг 27 TC-J01-00: выход из аккаунта.

        История и бонусы скрыты, авторизация снята.
        """
        self.authenticated = False
        self.cart = []
        self.cart_store = None
        self.promo_code = None
        self.promo_discount_amount = 0
        self.bonus_spent = 0
        self.delivery_method = None
        self.delivery_interval = None
        self.delivery_recipient = None
        self.delivery_comment = None
        self.checkout_form_open = False
        return {
            "screen": "login",
            "history_visible": False,
            "bonuses_visible": False,
        }

    def open_history(self) -> dict[str, Any]:
        """Шаг 30 TC-J01-00: открыть историю заказов."""
        return {
            "orders": list(self.order_history),
            "orders_count": len(self.order_history),
        }

    # ------------------------------------------------------------------
    # BR-N06 — истечение срока оплаты (TC-J01-11)
    # ------------------------------------------------------------------
    def expire_payment_deadline(self) -> dict[str, Any]:
        """Шаг 1 TC-J01-11: заказ автоматически отменён по истечении срока."""
        self.payment_deadline_expired = True
        self.order_status = ORDER_STATUS_AUTOCANCELLED
        self.autocancel_message_visible = True
        self.new_order_cta_visible = True
        for order in self.order_history:
            order["status"] = ORDER_STATUS_AUTOCANCELLED
        return {
            "order_status": ORDER_STATUS_AUTOCANCELLED,
            "autocancel_message_visible": True,
            "new_order_cta_visible": True,
            "history_status": ORDER_STATUS_AUTOCANCELLED,
        }

    def open_cancelled_order(self) -> dict[str, Any]:
        """Шаг 2 TC-J01-11: открыть детали отменённого заказа."""
        return {
            "recipient": self.order_recipient,
            "address": self.order_address,
            "status": self.order_status,
            "expired_message_visible": self.autocancel_message_visible,
            "new_order_cta_visible": self.new_order_cta_visible,
        }

    def click_new_order_cta(self) -> dict[str, Any]:
        """Шаг 3 TC-J01-11: нажата кнопка оформления нового заказа."""
        return {
            "screen": "checkout_form",
            "cart_prefilled": False,
        }
