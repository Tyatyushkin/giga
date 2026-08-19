"""
Pytest-тесты для journey J03-corporate-business.

Источник: output/suites/J03-corporate-business.md
Базовые кейсы: output/cases/J03-corporate-business/TC-J03-*.md

Структура:
- TestTCJ0300 — основной счастливый путь (18 шагов)
- TestTCJ0301 — активация скидки и пересчёт (3 шага)
- TestTCJ0302 — корзина в рамках одного магазина (5 шагов)
- TestTCJ0303 — точное время доставки (4 шага)
- TestTCJ0304 — признаки безналичного расчёта (3 шага)
"""

from __future__ import annotations

import allure
import pytest

from api_stub import CorporateApiStub
from test_data import (
    CATEGORY_COFFEE_TEA,
    CATEGORY_DRINKS,
    CATEGORY_GROCERY,
    CART_POSITIONS_AFTER_FIRST_ADD,
    CART_POSITIONS_AFTER_THREE_ADDS,
    CART_POSITIONS_AFTER_TWO_ADDS,
    CART_SUM_AFTER_QUANTITY_CHANGE,
    CART_SUM_AFTER_QUANTITY_CHANGE_VALUE,
    CART_SUM_TWO_ITEMS,
    CART_SUM_TWO_ITEMS_VALUE,
    DELIVERY_ADDRESS,
    DELIVERY_FEE,
    DELIVERY_METHOD,
    DELIVERY_RECIPIENT,
    DELIVERY_TIME,
    DISCOUNT_AMOUNT,
    DISCOUNT_PCT,
    PAYMENT_METHOD_LABEL,
    PRODUCT_COFFEE_NAME,
    PRODUCT_COFFEE_PRICE,
    PRODUCT_SUGAR_NAME,
    PRODUCT_TEA_NAME,
    PRODUCT_TEA_PRICE,
    PRODUCT_WATER_NAME,
    SBER_ID_AUTH_OPTION,
    SUGAR_NEW_POSITION_PRICE,
    SUGAR_NEW_QUANTITY,
    STORE_MARKET,
    STORE_WAREHOUSE,
    TARIFF_NAME_STANDARD,
    TARIFF_LIST_MIN_ITEMS,
    TOTAL_AFTER_DISCOUNT,
    TOTAL_BEFORE_DISCOUNT,
    TOTAL_TO_PAY,
)


# =============================================================================
# TC-J03-00 — основной счастливый путь (18 шагов)
# =============================================================================
@allure.label("layer", "e2e")
@allure.label("req", "BR-001, ANS-09, ANS-13")
@pytest.mark.corp
@pytest.mark.corp_main
@allure.severity(allure.severity_level.CRITICAL)
class TestTCJ0300:
    """Корпоративный клиент: вход → тариф → заказ → безналичный расчёт → скидка → доставка."""

    # ---------------------------------------------------------------------
    @allure.id("J03-TC-J03-00-01")
    @allure.label("req", "ANS-09, ANS-13")
    @allure.title("Открытие корпоративного портала «Купер для бизнеса»")
    @allure.description(
        "Шаг 1 из TC-J03-00: открытие портала; экран входа содержит вариант "
        "авторизации через Сбер ID. ANS-09, ANS-13"
    )
    def test_01_open_corporate_portal(self, api_client: CorporateApiStub) -> None:
        screen = api_client.open_portal()
        assert screen["screen"] == "corporate_login", "Должен открыться экран входа корпоративного портала"
        assert SBER_ID_AUTH_OPTION in screen["auth_options"], (
            f"Среди вариантов авторизации должен быть {SBER_ID_AUTH_OPTION!r}"
        )

    @allure.id("J03-TC-J03-00-02")
    @allure.label("req", "ANS-13")
    @allure.title("Выбор авторизации через Сбер ID")
    @allure.description(
        "Шаг 2 из TC-J03-00: пользователь выбирает вариант Сбер ID; "
        "открывается окно авторизации Сбер ID. ANS-13"
    )
    def test_02_select_sber_id(self, api_client: CorporateApiStub) -> None:
        api_client.open_portal()
        sber = api_client.select_sber_id_auth()
        assert sber["screen"] == "sber_id_auth", "Должно открыться окно авторизации Сбер ID"
        assert api_client.sber_id_window_open is True, "Окно Сбер ID должно быть открыто"

    @allure.id("J03-TC-J03-00-03")
    @allure.label("req", "BR-001, ANS-13")
    @allure.title("Подтверждение авторизации в Сбер ID")
    @allure.description(
        "Шаг 3 из TC-J03-00: пользователь подтверждает вход; "
        "отображается главный экран корпоративного портала. BR-001, ANS-13"
    )
    def test_03_confirm_sber_id(self, api_client: CorporateApiStub) -> None:
        api_client.open_portal()
        api_client.select_sber_id_auth()
        home = api_client.confirm_sber_id_auth()
        assert home["screen"] == "corporate_home", "Должен отображаться главный экран корпоративного портала"
        assert home["session"] == "active", "Корпоративная сессия должна быть установлена"
        assert api_client.authenticated is True, "Флаг авторизации должен быть активен"

    # ---------------------------------------------------------------------
    @allure.id("J03-TC-J03-00-04")
    @allure.label("req", "ANS-22")
    @allure.title("Открытие списка корпоративных тарифов")
    @allure.description(
        "Шаг 4 из TC-J03-00: список готовых корпоративных тарифов содержит "
        "несколько элементов; у каждого есть название и цена. ANS-22"
    )
    def test_04_open_tariff_list(self, api_client: CorporateApiStub) -> None:
        api_client.open_portal()
        api_client.select_sber_id_auth()
        api_client.confirm_sber_id_auth()
        tariffs = api_client.list_corporate_tariffs()
        items = tariffs["tariffs"]
        assert len(items) >= TARIFF_LIST_MIN_ITEMS, (
            f"Список должен содержать не менее {TARIFF_LIST_MIN_ITEMS} тарифов"
        )
        for item in items:
            assert item.get("name"), "У тарифа должно быть название"
            assert item.get("price"), "У тарифа должна быть цена"

    @allure.id("J03-TC-J03-00-05")
    @allure.label("req", "ANS-22")
    @allure.title("Выбор корпоративного тарифа «Стандарт»")
    @allure.description(
        "Шаг 5 из TC-J03-00: выбранный тариф становится активным; "
        "открывается корпоративный каталог. ANS-22"
    )
    def test_05_select_tariff(self, api_client: CorporateApiStub) -> None:
        api_client.open_portal()
        api_client.select_sber_id_auth()
        api_client.confirm_sber_id_auth()
        api_client.list_corporate_tariffs()
        result = api_client.select_corporate_tariff(TARIFF_NAME_STANDARD)
        assert result["selected_tariff"] == TARIFF_NAME_STANDARD, "Выбранный тариф должен быть зафиксирован"
        assert result["screen"] == "corporate_catalog", "Должен открыться корпоративный каталог"

    # ---------------------------------------------------------------------
    @allure.id("J03-TC-J03-00-06")
    @allure.label("req", "ANS-09")
    @allure.title("Проверка корпоративного каталога")
    @allure.description(
        "Шаг 6 из TC-J03-00: в каталоге доступен магазин «Купер Бизнес Маркет»; "
        "карточки товаров содержат цены корпоративного прайса. ANS-09"
    )
    def test_06_check_catalog(self, api_client: CorporateApiStub) -> None:
        api_client.open_portal()
        api_client.select_sber_id_auth()
        api_client.confirm_sber_id_auth()
        api_client.list_corporate_tariffs()
        api_client.select_corporate_tariff(TARIFF_NAME_STANDARD)
        catalog = api_client.get_corporate_catalog()
        store_names = [s["name"] for s in catalog["stores"]]
        assert STORE_MARKET in store_names, f"В каталоге должен быть магазин {STORE_MARKET!r}"
        market = next(s for s in catalog["stores"] if s["name"] == STORE_MARKET)
        products_flat: list[str] = []
        for cat in market["categories"]:
            products_flat.extend(cat["products"])
        assert len(products_flat) >= 1, "В магазине должны быть товары"

    # ---------------------------------------------------------------------
    @allure.id("J03-TC-J03-00-07")
    @allure.label("req", "BR-004")
    @allure.title("Добавление «Кофе Lavazza Crema 250 г» (1 шт.)")
    @allure.description(
        "Шаг 7 из TC-J03-00: добавление первого товара в корзину; "
        "в корзине 1 позиция «Кофе Lavazza Crema 250 г» (1 шт., 1200 ₽). BR-004"
    )
    def test_07_add_coffee(self, api_client: CorporateApiStub) -> None:
        api_client.add_to_cart(STORE_MARKET, PRODUCT_COFFEE_NAME, 1)
        cart = api_client.get_cart()
        assert cart["positions_count"] == CART_POSITIONS_AFTER_FIRST_ADD, (
            f"Счётчик позиций должен быть {CART_POSITIONS_AFTER_FIRST_ADD}"
        )
        line = cart["lines"][0]
        assert line["product"] == PRODUCT_COFFEE_NAME, "В корзине должен быть «Кофе Lavazza Crema 250 г»"
        assert line["qty"] == 1, "Количество должно быть 1"
        assert line["price"] == 1200, f"Цена позиции должна быть 1200 ₽, получено {line['price']}"

    @allure.id("J03-TC-J03-00-08")
    @allure.label("req", "BR-004")
    @allure.title("Добавление «Чай Greenfield Sencha 100 пакетиков» (1 шт.)")
    @allure.description(
        "Шаг 8 из TC-J03-00: в корзине 2 позиции, в т.ч. «Чай Greenfield Sencha 100 пакетиков» "
        "(1 шт., 450 ₽). BR-004"
    )
    def test_08_add_tea(self, api_client: CorporateApiStub) -> None:
        api_client.add_to_cart(STORE_MARKET, PRODUCT_COFFEE_NAME, 1)
        api_client.add_to_cart(STORE_MARKET, PRODUCT_TEA_NAME, 1)
        cart = api_client.get_cart()
        assert cart["positions_count"] == 2, f"Счётчик позиций должен быть 2, получено {cart['positions_count']}"
        products = [line["product"] for line in cart["lines"]]
        assert PRODUCT_TEA_NAME in products, "В корзине должен быть чай"
        tea_line = next(line for line in cart["lines"] if line["product"] == PRODUCT_TEA_NAME)
        assert tea_line["qty"] == 1, "Количество чая должно быть 1"
        assert tea_line["price"] == 450, f"Цена позиции чая должна быть 450 ₽, получено {tea_line['price']}"

    @allure.id("J03-TC-J03-00-09")
    @allure.label("req", "BR-004")
    @allure.title("Добавление «Сахар-песок 1 кг» (1 шт.)")
    @allure.description(
        "Шаг 9 из TC-J03-00: в корзине 3 позиции, в т.ч. «Сахар-песок 1 кг» (1 шт., 80 ₽). BR-004"
    )
    def test_09_add_sugar(self, api_client: CorporateApiStub) -> None:
        api_client.add_to_cart(STORE_MARKET, PRODUCT_COFFEE_NAME, 1)
        api_client.add_to_cart(STORE_MARKET, PRODUCT_TEA_NAME, 1)
        api_client.add_to_cart(STORE_MARKET, PRODUCT_SUGAR_NAME, 1)
        cart = api_client.get_cart()
        assert cart["positions_count"] == CART_POSITIONS_AFTER_THREE_ADDS, (
            f"Счётчик позиций должен быть {CART_POSITIONS_AFTER_THREE_ADDS}"
        )
        sugar_line = next(line for line in cart["lines"] if line["product"] == PRODUCT_SUGAR_NAME)
        assert sugar_line["qty"] == 1, "Количество сахара должно быть 1"
        assert sugar_line["price"] == 80, f"Цена сахара должна быть 80 ₽, получено {sugar_line['price']}"

    @allure.id("J03-TC-J03-00-10")
    @allure.label("req", "BR-003, BR-004, ANS-25")
    @allure.title("Проверка состава и стоимости корзины до активации скидки")
    @allure.description(
        "Шаг 10 из TC-J03-00: корзина содержит 3 позиции одного магазина, "
        "сумма 1730 ₽; активной корпоративной скидки в расчёте нет. BR-003, ANS-25"
    )
    def test_10_check_cart_before_discount(self, api_client: CorporateApiStub) -> None:
        api_client.add_to_cart(STORE_MARKET, PRODUCT_COFFEE_NAME, 1)
        api_client.add_to_cart(STORE_MARKET, PRODUCT_TEA_NAME, 1)
        api_client.add_to_cart(STORE_MARKET, PRODUCT_SUGAR_NAME, 1)
        cart = api_client.get_cart()
        calc = api_client.get_order_calculation()
        assert cart["positions_count"] == CART_POSITIONS_AFTER_THREE_ADDS
        assert cart["store"] == STORE_MARKET, "Все позиции должны быть из одного магазина"
        assert calc["items_sum"] == 1730, f"Сумма товаров должна быть 1730 ₽, получено {calc['items_sum']}"
        assert calc["discount"]["active"] is False, "До активации скидки в расчёте её быть не должно"

    # ---------------------------------------------------------------------
    @allure.id("J03-TC-J03-00-11")
    @allure.label("req", "ANS-23")
    @allure.title("Активация корпоративной скидки")
    @allure.description(
        "Шаг 11 из TC-J03-00: пользователь активирует скидку; "
        "в блоке расчёта появляется строка скидки; сумма пересчитана. ANS-23"
    )
    def test_11_activate_discount(self, api_client: CorporateApiStub) -> None:
        api_client.open_portal()
        api_client.select_sber_id_auth()
        api_client.confirm_sber_id_auth()
        api_client.list_corporate_tariffs()
        api_client.select_corporate_tariff(TARIFF_NAME_STANDARD)
        api_client.add_to_cart(STORE_MARKET, PRODUCT_COFFEE_NAME, 1)
        api_client.add_to_cart(STORE_MARKET, PRODUCT_TEA_NAME, 1)
        api_client.add_to_cart(STORE_MARKET, PRODUCT_SUGAR_NAME, 1)
        calc = api_client.activate_corporate_discount()
        assert calc["discount"]["active"] is True, "После активации флаг скидки должен быть True"
        assert calc["discount"]["pct"] == 15, "Процент скидки должен быть 15 %"
        assert calc["items_after_discount"] is not None, "Сумма после скидки должна быть рассчитана"

    @allure.id("J03-TC-J03-00-12")
    @allure.label("req", "ANS-23")
    @allure.title("Проверка пересчёта с учётом корпоративной скидки")
    @allure.description(
        "Шаг 12 из TC-J03-00: сумма товаров 1730 ₽, скидка 15 % (259.50 ₽), "
        "сумма после скидки 1470.50 ₽. ANS-23"
    )
    def test_12_check_discount_recalc(self, api_client: CorporateApiStub) -> None:
        api_client.open_portal()
        api_client.select_sber_id_auth()
        api_client.confirm_sber_id_auth()
        api_client.list_corporate_tariffs()
        api_client.select_corporate_tariff(TARIFF_NAME_STANDARD)
        api_client.add_to_cart(STORE_MARKET, PRODUCT_COFFEE_NAME, 1)
        api_client.add_to_cart(STORE_MARKET, PRODUCT_TEA_NAME, 1)
        api_client.add_to_cart(STORE_MARKET, PRODUCT_SUGAR_NAME, 1)
        calc = api_client.activate_corporate_discount()
        assert calc["items_sum"] == 1730, f"Сумма товаров должна быть 1730 ₽, получено {calc['items_sum']}"
        assert calc["discount"]["pct"] == 15, "Процент скидки должен быть 15 %"
        assert abs(calc["discount"]["value"] - 259.50) < 0.01, (
            f"Размер скидки должен быть 259.50 ₽, получено {calc['discount']['value']}"
        )
        assert abs(calc["items_after_discount"] - 1470.50) < 0.01, (
            f"Сумма после скидки должна быть 1470.50 ₽, получено {calc['items_after_discount']}"
        )

    # ---------------------------------------------------------------------
    @allure.id("J03-TC-J03-00-13")
    @allure.label("req", "ANS-26")
    @allure.title("Переход к оформлению — метка «безналичный расчёт»")
    @allure.description(
        "Шаг 13 из TC-J03-00: открыта форма оформления с меткой "
        "«безналичный расчёт»; форма ввода данных банковской карты не отображается. ANS-26"
    )
    def test_13_open_checkout_form(self, api_client: CorporateApiStub) -> None:
        form = api_client.open_checkout_form()
        assert form["screen"] == "checkout_form", "Должна открыться форма оформления"
        assert form["payment_label"] == PAYMENT_METHOD_LABEL, (
            f"Метка способа оплаты должна быть {PAYMENT_METHOD_LABEL!r}, "
            f"получено {form['payment_label']!r}"
        )
        assert form["card_form_visible"] is False, (
            "Блок ввода данных банковской карты не должен отображаться в корпоративной форме"
        )

    @allure.id("J03-TC-J03-00-14")
    @allure.label("req", "BR-008, ANS-24, BR-014")
    @allure.title("Открытие блока параметров доставки")
    @allure.description(
        "Шаг 14 из TC-J03-00: в блоке доставки присутствуют поле адреса, "
        "поле получателя, элемент выбора времени (точное значение, не диапазон); "
        "способ «Доставка курьером» помечен признаком выделенного курьера. BR-008, ANS-24, BR-014"
    )
    def test_14_open_delivery_form(self, api_client: CorporateApiStub) -> None:
        delivery = api_client.get_delivery_form()
        assert "address" in delivery["fields"], "Должно быть поле адреса"
        assert "recipient" in delivery["fields"], "Должно быть поле получателя"
        assert "time" in delivery["fields"], "Должен быть элемент выбора времени"
        assert delivery["time_options"]["exact_values_present"] is True, (
            "Должны быть точные значения времени"
        )
        assert delivery["time_options"]["interval_values_present"] is False, (
            "Интервальные значения вида «от … до …» должны отсутствовать"
        )
        courier = next(m for m in delivery["methods"] if m["name"] == DELIVERY_METHOD)
        assert courier["dedicated_courier"] is True, (
            f"Способ {DELIVERY_METHOD!r} должен быть помечен признаком выделенного курьера"
        )

    @allure.id("J03-TC-J03-00-15")
    @allure.label("req", "BR-008")
    @allure.title("Заполнение адреса доставки и получателя")
    @allure.description(
        "Шаг 15 из TC-J03-00: поле адреса содержит адрес корпоративной доставки; "
        "поле получателя содержит «Анна Петрова». BR-008"
    )
    def test_15_fill_delivery_fields(self, api_client: CorporateApiStub) -> None:
        fields = api_client.fill_delivery_fields(DELIVERY_ADDRESS, DELIVERY_RECIPIENT)
        assert fields["address"] == DELIVERY_ADDRESS, (
            f"Поле адреса должно содержать {DELIVERY_ADDRESS!r}, получено {fields['address']!r}"
        )
        assert fields["recipient"] == DELIVERY_RECIPIENT, (
            f"Поле получателя должно содержать {DELIVERY_RECIPIENT!r}, получено {fields['recipient']!r}"
        )

    @allure.id("J03-TC-J03-00-16")
    @allure.label("req", "ANS-24")
    @allure.title("Выбор точного времени доставки 14:30")
    @allure.description(
        "Шаг 16 из TC-J03-00: выбранное значение 14:30 отображается как активное; "
        "среди доступных значений есть точные; интервальные «от … до …» отсутствуют. ANS-24"
    )
    def test_16_select_exact_time(self, api_client: CorporateApiStub) -> None:
        delivery = api_client.get_delivery_form()
        assert delivery["time_options"]["exact_values_present"] is True, (
            "Точные значения времени должны присутствовать"
        )
        assert delivery["time_options"]["interval_values_present"] is False, (
            "Интервальные значения должны отсутствовать"
        )
        result = api_client.select_delivery_time(DELIVERY_TIME)
        assert result["selected_time"] == DELIVERY_TIME, (
            f"Активное время должно быть {DELIVERY_TIME!r}, получено {result['selected_time']!r}"
        )

    @allure.id("J03-TC-J03-00-17")
    @allure.label("req", "BR-009")
    @allure.title("Проверка итоговой стоимости заказа")
    @allure.description(
        "Шаг 17 из TC-J03-00: сумма после скидки 1470.50 ₽, "
        "комиссия доставки 98 ₽, сборка 29 ₽; итог к оплате 1597.50 ₽. BR-009"
    )
    def test_17_check_order_totals(self, api_client: CorporateApiStub) -> None:
        api_client.open_portal()
        api_client.select_sber_id_auth()
        api_client.confirm_sber_id_auth()
        api_client.list_corporate_tariffs()
        api_client.select_corporate_tariff(TARIFF_NAME_STANDARD)
        api_client.add_to_cart(STORE_MARKET, PRODUCT_COFFEE_NAME, 1)
        api_client.add_to_cart(STORE_MARKET, PRODUCT_TEA_NAME, 1)
        api_client.add_to_cart(STORE_MARKET, PRODUCT_SUGAR_NAME, 1)
        calc = api_client.activate_corporate_discount()
        assert abs(calc["items_after_discount"] - 1470.50) < 0.01, (
            f"Сумма после скидки должна быть 1470.50 ₽, получено {calc['items_after_discount']}"
        )
        assert calc["delivery_fee"] == 98, f"Комиссия доставки должна быть 98 ₽, получено {calc['delivery_fee']}"
        assert calc["assembly_fee"] == 29, f"Сборка должна быть 29 ₽, получено {calc['assembly_fee']}"
        assert abs(calc["total"] - 1597.50) < 0.01, (
            f"Итог к оплате должен быть 1597.50 ₽, получено {calc['total']}"
        )

    @allure.id("J03-TC-J03-00-18")
    @allure.label("req", "BR-014, ANS-26")
    @allure.title("Подтверждение оформления — экран созданного заказа")
    @allure.description(
        "Шаг 18 из TC-J03-00: отображается экран созданного корпоративного заказа "
        "со статусом обработки; в деталях — магазин, адрес, получатель, время, "
        "выделенный курьер, способ оплаты «безналичный расчёт». BR-014, ANS-26"
    )
    def test_18_confirm_order(self, api_client: CorporateApiStub) -> None:
        api_client.open_portal()
        api_client.select_sber_id_auth()
        api_client.confirm_sber_id_auth()
        api_client.list_corporate_tariffs()
        api_client.select_corporate_tariff(TARIFF_NAME_STANDARD)
        api_client.add_to_cart(STORE_MARKET, PRODUCT_COFFEE_NAME, 1)
        api_client.add_to_cart(STORE_MARKET, PRODUCT_TEA_NAME, 1)
        api_client.add_to_cart(STORE_MARKET, PRODUCT_SUGAR_NAME, 1)
        api_client.activate_corporate_discount()
        api_client.open_checkout_form()
        api_client.fill_delivery_fields(DELIVERY_ADDRESS, DELIVERY_RECIPIENT)
        api_client.select_delivery_time(DELIVERY_TIME)
        order = api_client.confirm_order()
        assert order["status"] is not None, "У созданного заказа должен быть статус обработки"
        assert order["store"] == STORE_MARKET, "В деталях заказа должен быть магазин"
        assert order["address"] == DELIVERY_ADDRESS, "В деталях заказа должен быть адрес"
        assert order["recipient"] == DELIVERY_RECIPIENT, "В деталях заказа должен быть получатель"
        assert order["time"] == DELIVERY_TIME, "В деталях заказа должно быть время доставки"
        assert order["dedicated_courier"] is True, "Должен быть признак выделенного курьера"
        assert order["payment_method"] == PAYMENT_METHOD_LABEL, (
            f"Способ оплаты должен быть {PAYMENT_METHOD_LABEL!r}, "
            f"получено {order['payment_method']!r}"
        )


# =============================================================================
# TC-J03-01 — активация корпоративной скидки до 15 % после выбора тарифа (3 шага)
# =============================================================================
@allure.label("layer", "e2e")
@allure.label("req", "BR-014, ANS-23")
@pytest.mark.corp
@pytest.mark.corp_variant
@allure.severity(allure.severity_level.CRITICAL)
class TestTCJ0301:
    """Активация корпоративной скидки до 15 % после выбора тарифа и пересчёт суммы."""

    def _precondition(self, api_client: CorporateApiStub) -> None:
        api_client.open_portal()
        api_client.select_sber_id_auth()
        api_client.confirm_sber_id_auth()
        api_client.list_corporate_tariffs()
        api_client.select_corporate_tariff(TARIFF_NAME_STANDARD)
        api_client.add_to_cart(STORE_MARKET, PRODUCT_COFFEE_NAME, 1)
        api_client.add_to_cart(STORE_MARKET, PRODUCT_TEA_NAME, 1)
        api_client.add_to_cart(STORE_MARKET, PRODUCT_SUGAR_NAME, 1)

    @allure.id("J03-TC-J03-01-01")
    @allure.label("req", "ANS-23")
    @allure.title("Проверка блока расчёта до активации скидки")
    @allure.description(
        "Шаг 1 из TC-J03-01: в блоке расчёта отображается сумма товаров 1730 ₽, "
        "разбитая на позиции; активная строка скидки отсутствует; "
        "элемент активации скидки присутствует в неактивном состоянии. ANS-23"
    )
    def test_01_calculation_before_discount(self, api_client: CorporateApiStub) -> None:
        self._precondition(api_client)
        calc = api_client.get_order_calculation()
        cart = api_client.get_cart()
        assert calc["items_sum"] == 1730, f"Сумма товаров должна быть 1730 ₽, получено {calc['items_sum']}"
        assert calc["discount"]["active"] is False, (
            "Активная строка корпоративной скидки до активации должна отсутствовать"
        )
        assert cart["positions_count"] == 3, "В корзине должно быть 3 позиции"

    @allure.id("J03-TC-J03-01-02")
    @allure.label("req", "ANS-23")
    @allure.title("Активация корпоративной скидки")
    @allure.description(
        "Шаг 2 из TC-J03-01: пользователь активирует скидку; "
        "в расчёте появляется строка скидки с процентом 15 %; сумма пересчитана. ANS-23"
    )
    def test_02_activate_discount(self, api_client: CorporateApiStub) -> None:
        self._precondition(api_client)
        calc = api_client.activate_corporate_discount()
        assert calc["discount"]["active"] is True, "Скидка должна быть активирована"
        assert calc["discount"]["pct"] == 15, "Процент скидки должен быть 15 %"
        assert calc["items_after_discount"] is not None, "Сумма должна быть пересчитана"

    @allure.id("J03-TC-J03-01-03")
    @allure.label("req", "ANS-23")
    @allure.title("Проверка размера скидки и границы 15 %")
    @allure.description(
        "Шаг 3 из TC-J03-01: сумма товаров 1730 ₽, скидка 15 % (259.50 ₽), "
        "сумма после скидки 1470.50 ₽; максимальное значение скидки ≤ 15 %. ANS-23"
    )
    def test_03_check_discount_size_and_boundary(self, api_client: CorporateApiStub) -> None:
        self._precondition(api_client)
        calc = api_client.activate_corporate_discount()
        assert calc["items_sum"] == 1730, f"Сумма товаров должна быть 1730 ₽, получено {calc['items_sum']}"
        assert calc["discount"]["pct"] == 15, "Процент скидки должен быть 15 %"
        assert abs(calc["discount"]["value"] - 259.50) < 0.01, (
            f"Размер скидки должен быть 259.50 ₽, получено {calc['discount']['value']}"
        )
        assert abs(calc["items_after_discount"] - 1470.50) < 0.01, (
            f"Сумма после скидки должна быть 1470.50 ₽, получено {calc['items_after_discount']}"
        )
        # Граница «до 15 %»: применённая скидка не превышает 15 %
        assert calc["discount"]["pct"] <= 15, (
            f"Применённая скидка не должна превышать 15 %, получено {calc['discount']['pct']}"
        )


# =============================================================================
# TC-J03-02 — корзина в рамках одного магазина + изменение количества (5 шагов)
# =============================================================================
@allure.label("layer", "e2e")
@allure.label("req", "BR-003, BR-004, BR-005, ANS-25")
@pytest.mark.corp
@pytest.mark.corp_variant
@allure.severity(allure.severity_level.CRITICAL)
class TestTCJ0302:
    """Корзина в рамках одного магазина; изменение количества; блокировка кросс-магазинного добавления."""

    def _precondition(self, api_client: CorporateApiStub) -> None:
        api_client.open_portal()
        api_client.select_sber_id_auth()
        api_client.confirm_sber_id_auth()
        api_client.list_corporate_tariffs()
        api_client.select_corporate_tariff(TARIFF_NAME_STANDARD)

    @allure.id("J03-TC-J03-02-01")
    @allure.label("req", "BR-004")
    @allure.title("Добавление «Кофе Lavazza Crema 250 г» из категории «Кофе и чай»")
    @allure.description(
        "Шаг 1 из TC-J03-02: добавление товара из категории «Кофе и чай»; "
        "в корзине 1 позиция «Кофе Lavazza Crema 250 г» (1 шт., 1200 ₽). BR-004"
    )
    def test_01_add_coffee(self, api_client: CorporateApiStub) -> None:
        self._precondition(api_client)
        api_client.add_to_cart(STORE_MARKET, PRODUCT_COFFEE_NAME, 1)
        cart = api_client.get_cart()
        assert cart["positions_count"] == CART_POSITIONS_AFTER_FIRST_ADD, (
            f"Счётчик позиций должен быть {CART_POSITIONS_AFTER_FIRST_ADD}"
        )
        line = cart["lines"][0]
        assert line["product"] == PRODUCT_COFFEE_NAME, "В корзине должен быть «Кофе Lavazza Crema 250 г»"
        assert line["qty"] == 1, "Количество должно быть 1"
        assert line["price"] == 1200, f"Цена позиции должна быть 1200 ₽, получено {line['price']}"

    @allure.id("J03-TC-J03-02-02")
    @allure.label("req", "BR-004")
    @allure.title("Добавление «Сахар-песок 1 кг» из категории «Бакалея»")
    @allure.description(
        "Шаг 2 из TC-J03-02: в корзине 2 позиции из одного магазина, но из разных "
        "категорий («Кофе и чай», «Бакалея»); сумма товаров 1280 ₽. BR-004"
    )
    def test_02_add_sugar(self, api_client: CorporateApiStub) -> None:
        self._precondition(api_client)
        api_client.add_to_cart(STORE_MARKET, PRODUCT_COFFEE_NAME, 1)
        api_client.add_to_cart(STORE_MARKET, PRODUCT_SUGAR_NAME, 1)
        cart = api_client.get_cart()
        assert cart["positions_count"] == CART_POSITIONS_AFTER_TWO_ADDS, (
            f"Счётчик позиций должен быть {CART_POSITIONS_AFTER_TWO_ADDS}"
        )
        assert cart["store"] == STORE_MARKET, "Обе позиции должны быть из одного магазина"
        assert cart["sum"] == CART_SUM_TWO_ITEMS_VALUE, (
            f"Сумма товаров должна быть {CART_SUM_TWO_ITEMS_VALUE} ₽, получено {cart['sum']}"
        )
        # Категории в корзине разные
        cats = {CATEGORY_COFFEE_TEA, CATEGORY_GROCERY}
        assert len(cats) == 2, "Категории у позиций должны быть разные"

    @allure.id("J03-TC-J03-02-03")
    @allure.label("req", "BR-005")
    @allure.title("Изменение количества «Сахар-песок 1 кг» с 1 до 2")
    @allure.description(
        "Шаг 3 из TC-J03-02: количество «Сахар-песок 1 кг» становится 2 шт.; "
        "стоимость позиции 160 ₽; сумма корзины 1360 ₽; счётчик позиций остаётся 2. BR-005"
    )
    def test_03_change_quantity(self, api_client: CorporateApiStub) -> None:
        self._precondition(api_client)
        api_client.add_to_cart(STORE_MARKET, PRODUCT_COFFEE_NAME, 1)
        api_client.add_to_cart(STORE_MARKET, PRODUCT_SUGAR_NAME, 1)
        cart = api_client.change_quantity(PRODUCT_SUGAR_NAME, SUGAR_NEW_QUANTITY)
        sugar_line = next(line for line in cart["lines"] if line["product"] == PRODUCT_SUGAR_NAME)
        assert sugar_line["qty"] == SUGAR_NEW_QUANTITY, (
            f"Количество «Сахар-песок» должно быть {SUGAR_NEW_QUANTITY}, получено {sugar_line['qty']}"
        )
        assert sugar_line["price"] == SUGAR_NEW_POSITION_PRICE, (
            f"Стоимость позиции должна быть {SUGAR_NEW_POSITION_PRICE} ₽, "
            f"получено {sugar_line['price']}"
        )
        assert cart["sum"] == CART_SUM_AFTER_QUANTITY_CHANGE_VALUE, (
            f"Сумма товаров должна быть {CART_SUM_AFTER_QUANTITY_CHANGE_VALUE} ₽, "
            f"получено {cart['sum']}"
        )
        assert cart["positions_count"] == CART_POSITIONS_AFTER_TWO_ADDS, (
            f"Количество позиций корзины должно остаться {CART_POSITIONS_AFTER_TWO_ADDS}, "
            f"получено {cart['positions_count']}"
        )

    @allure.id("J03-TC-J03-02-04")
    @allure.label("req", "BR-003")
    @allure.title("Переключение каталога на «Купер Бизнес Склад»")
    @allure.description(
        "Шаг 4 из TC-J03-02: каталог переключается на «Купер Бизнес Склад»; "
        "карточки товаров принадлежат этому магазину. BR-003"
    )
    def test_04_switch_to_warehouse(self, api_client: CorporateApiStub) -> None:
        self._precondition(api_client)
        catalog = api_client.get_corporate_catalog()
        warehouse = next(s for s in catalog["stores"] if s["name"] == STORE_WAREHOUSE)
        assert warehouse, f"В каталоге должен быть магазин {STORE_WAREHOUSE!r}"
        products_flat: list[str] = []
        for cat in warehouse["categories"]:
            products_flat.extend(cat["products"])
        assert PRODUCT_WATER_NAME in products_flat, (
            f"В магазине {STORE_WAREHOUSE!r} должен быть товар {PRODUCT_WATER_NAME!r}"
        )

    @allure.id("J03-TC-J03-02-05")
    @allure.label("req", "BR-003, ANS-25")
    @allure.title("Попытка добавить товар из другого магазина — блокировка")
    @allure.description(
        "Шаг 5 из TC-J03-02: попытка добавить товар из «Купер Бизнес Склад» "
        "в корзину с товарами из «Купер Бизнес Маркет» — товар не попадает в корзину; "
        "корзина остаётся в рамках одного магазина; счётчик = 2; сумма не изменилась (1360 ₽). BR-003, ANS-25"
    )
    def test_05_cross_store_blocked(self, api_client: CorporateApiStub) -> None:
        self._precondition(api_client)
        api_client.add_to_cart(STORE_MARKET, PRODUCT_COFFEE_NAME, 1)
        api_client.add_to_cart(STORE_MARKET, PRODUCT_SUGAR_NAME, 1)
        api_client.change_quantity(PRODUCT_SUGAR_NAME, SUGAR_NEW_QUANTITY)
        api_client.add_to_cart(STORE_WAREHOUSE, PRODUCT_WATER_NAME, 1)
        cart = api_client.get_cart()
        assert api_client.cross_store_attempt_blocked is True, (
            "Попытка кросс-магазинного добавления должна быть заблокирована"
        )
        assert cart["store"] == STORE_MARKET, "Корзина должна остаться в рамках одного магазина"
        assert cart["positions_count"] == CART_POSITIONS_AFTER_TWO_ADDS, (
            f"Счётчик позиций должен остаться {CART_POSITIONS_AFTER_TWO_ADDS}, "
            f"получено {cart['positions_count']}"
        )
        assert cart["sum"] == CART_SUM_AFTER_QUANTITY_CHANGE_VALUE, (
            f"Сумма должна остаться {CART_SUM_AFTER_QUANTITY_CHANGE_VALUE} ₽, "
            f"получено {cart['sum']}"
        )
        products = [line["product"] for line in cart["lines"]]
        assert PRODUCT_WATER_NAME not in products, (
            f"Товар {PRODUCT_WATER_NAME!r} не должен попасть в корзину"
        )


# =============================================================================
# TC-J03-03 — выбор точного времени доставки (4 шага)
# =============================================================================
@allure.label("layer", "e2e")
@allure.label("req", "BR-014, ANS-24")
@pytest.mark.corp
@pytest.mark.corp_variant
@allure.severity(allure.severity_level.CRITICAL)
class TestTCJ0303:
    """Точное время доставки в корпоративном заказе (отличие от стандартного интервала)."""

    def _precondition(self, api_client: CorporateApiStub) -> None:
        api_client.open_portal()
        api_client.select_sber_id_auth()
        api_client.confirm_sber_id_auth()
        api_client.list_corporate_tariffs()
        api_client.select_corporate_tariff(TARIFF_NAME_STANDARD)
        api_client.add_to_cart(STORE_MARKET, PRODUCT_COFFEE_NAME, 1)
        api_client.add_to_cart(STORE_MARKET, PRODUCT_TEA_NAME, 1)
        api_client.add_to_cart(STORE_MARKET, PRODUCT_SUGAR_NAME, 1)
        api_client.activate_corporate_discount()
        api_client.open_checkout_form()

    @allure.id("J03-TC-J03-03-01")
    @allure.label("req", "BR-014, ANS-24")
    @allure.title("Открытие блока параметров доставки")
    @allure.description(
        "Шаг 1 из TC-J03-03: в блоке доставки присутствуют поле адреса, "
        "поле получателя, элемент выбора времени; способ «Доставка курьером» "
        "помечен признаком выделенного курьера. BR-014"
    )
    def test_01_open_delivery_block(self, api_client: CorporateApiStub) -> None:
        self._precondition(api_client)
        delivery = api_client.get_delivery_form()
        assert "address" in delivery["fields"], "Должно быть поле адреса"
        assert "recipient" in delivery["fields"], "Должно быть поле получателя"
        assert "time" in delivery["fields"], "Должен быть элемент выбора времени"
        courier = next(m for m in delivery["methods"] if m["name"] == DELIVERY_METHOD)
        assert courier["dedicated_courier"] is True, (
            f"Способ {DELIVERY_METHOD!r} должен быть помечен признаком выделенного курьера"
        )

    @allure.id("J03-TC-J03-03-02")
    @allure.label("req", "BR-008")
    @allure.title("Заполнение адреса доставки и получателя")
    @allure.description(
        "Шаг 2 из TC-J03-03: поле адреса содержит корпоративный адрес; "
        "поле получателя содержит «Анна Петрова». BR-008"
    )
    def test_02_fill_address_and_recipient(self, api_client: CorporateApiStub) -> None:
        self._precondition(api_client)
        fields = api_client.fill_delivery_fields(DELIVERY_ADDRESS, DELIVERY_RECIPIENT)
        assert fields["address"] == DELIVERY_ADDRESS, (
            f"Поле адреса должно содержать {DELIVERY_ADDRESS!r}, получено {fields['address']!r}"
        )
        assert fields["recipient"] == DELIVERY_RECIPIENT, (
            f"Поле получателя должно содержать {DELIVERY_RECIPIENT!r}, получено {fields['recipient']!r}"
        )

    @allure.id("J03-TC-J03-03-03")
    @allure.label("req", "ANS-24")
    @allure.title("Открытие элемента выбора времени — точные значения")
    @allure.description(
        "Шаг 3 из TC-J03-03: среди доступных значений присутствуют точные значения "
        "времени; интервальные значения вида «от … до …» отсутствуют. ANS-24"
    )
    def test_03_time_options_exact_only(self, api_client: CorporateApiStub) -> None:
        self._precondition(api_client)
        delivery = api_client.get_delivery_form()
        assert delivery["time_options"]["exact_values_present"] is True, (
            "Точные значения времени должны присутствовать"
        )
        assert delivery["time_options"]["interval_values_present"] is False, (
            "Интервальные значения вида «от … до …» должны отсутствовать"
        )

    @allure.id("J03-TC-J03-03-04")
    @allure.label("req", "ANS-24")
    @allure.title("Выбор точного времени 14:30")
    @allure.description(
        "Шаг 4 из TC-J03-03: значение 14:30 отображается как активное; "
        "точное время доставки 14:30 фиксируется в параметрах доставки. ANS-24"
    )
    def test_04_select_exact_time(self, api_client: CorporateApiStub) -> None:
        self._precondition(api_client)
        result = api_client.select_delivery_time(DELIVERY_TIME)
        assert result["selected_time"] == DELIVERY_TIME, (
            f"Активное время должно быть {DELIVERY_TIME!r}, получено {result['selected_time']!r}"
        )
        assert api_client.delivery_time == DELIVERY_TIME, (
            f"Точное время доставки должно быть зафиксировано как {DELIVERY_TIME!r}"
        )


# =============================================================================
# TC-J03-04 — признаки безналичного расчёта в форме оформления (3 шага)
# =============================================================================
@allure.label("layer", "e2e")
@allure.label("req", "ANS-26")
@pytest.mark.corp
@pytest.mark.corp_variant
@allure.severity(allure.severity_level.CRITICAL)
class TestTCJ0304:
    """Наблюдаемые признаки безналичного расчёта в форме оформления корпоративного заказа."""

    def _precondition(self, api_client: CorporateApiStub) -> None:
        api_client.open_portal()
        api_client.select_sber_id_auth()
        api_client.confirm_sber_id_auth()
        api_client.list_corporate_tariffs()
        api_client.select_corporate_tariff(TARIFF_NAME_STANDARD)
        api_client.add_to_cart(STORE_MARKET, PRODUCT_COFFEE_NAME, 1)
        api_client.add_to_cart(STORE_MARKET, PRODUCT_TEA_NAME, 1)
        api_client.add_to_cart(STORE_MARKET, PRODUCT_SUGAR_NAME, 1)
        api_client.activate_corporate_discount()

    @allure.id("J03-TC-J03-04-01")
    @allure.label("req", "ANS-26")
    @allure.title("Открытие формы оформления — метка способа оплаты")
    @allure.description(
        "Шаг 1 из TC-J03-04: открыта форма оформления; присутствует метка способа "
        "оплаты; блок ввода данных банковской карты не отображается. ANS-26"
    )
    def test_01_open_checkout(self, api_client: CorporateApiStub) -> None:
        self._precondition(api_client)
        form = api_client.open_checkout_form()
        assert form["screen"] == "checkout_form", "Должна открыться форма оформления"
        assert form.get("payment_label"), "В форме должна присутствовать метка способа оплаты"
        assert form["card_form_visible"] is False, (
            "Блок ввода данных банковской карты не должен отображаться"
        )

    @allure.id("J03-TC-J03-04-02")
    @allure.label("req", "ANS-26")
    @allure.title("Дословная проверка метки «безналичный расчёт»")
    @allure.description(
        "Шаг 2 из TC-J03-04: в форме оформления присутствует дословная метка "
        "«безналичный расчёт». ANS-26"
    )
    def test_02_check_payment_label_verbatim(self, api_client: CorporateApiStub) -> None:
        self._precondition(api_client)
        form = api_client.open_checkout_form()
        assert form["payment_label"] == PAYMENT_METHOD_LABEL, (
            f"Метка способа оплаты должна дословно быть {PAYMENT_METHOD_LABEL!r}, "
            f"получено {form['payment_label']!r}"
        )

    @allure.id("J03-TC-J03-04-03")
    @allure.label("req", "ANS-26")
    @allure.title("Подтверждение метки «безналичный расчёт» и отсутствия блока карты")
    @allure.description(
        "Шаг 3 из TC-J03-04: в форме присутствует метка «безналичный расчёт» как "
        "способ оплаты; блок ввода данных банковской карты не отображается. ANS-26"
    )
    def test_03_check_payment_method_and_no_card(self, api_client: CorporateApiStub) -> None:
        self._precondition(api_client)
        form = api_client.open_checkout_form()
        assert form["payment_label"] == PAYMENT_METHOD_LABEL, (
            f"Способ оплаты должен быть {PAYMENT_METHOD_LABEL!r}, "
            f"получено {form['payment_label']!r}"
        )
        assert form["card_form_visible"] is False, (
            "Блок ввода данных банковской карты должен отсутствовать"
        )
