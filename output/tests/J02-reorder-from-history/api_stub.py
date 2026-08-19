"""
api_stub.py — deterministic API stub for J02-reorder-from-history.

Each public method returns the same result for the same input.
State mutates between calls to model the journey flow.

State model:
- auth: unauthenticated -> sber_popup -> authenticated
- cart: populated by reorder(), mutated by confirm_*()
- new_order: created by pay()
"""
from __future__ import annotations

from typing import Any

from .test_data import (
    APPLE_AVAILABLE_QTY,
    AUTH_OPTION_PHONE,
    AUTH_OPTION_SBER_ID,
    BONUS_LABEL,
    CARD_PAYMENT,
    CART_TOTAL_AFTER_CONFIRM,
    DELIVERY_ADDRESS,
    DELIVERY_FEE,
    DELIVERY_INTERVAL,
    DELIVERY_METHOD,
    GRAND_TOTAL,
    NEW_ORDER_NUMBER,
    NEW_ORDER_STATUS,
    ORDER_DATE_4711,
    ORDER_NUMBER_4711,
    ORDER_STATUS_DELIVERED,
    PACKING_FEE,
    PRODUCT_APPLE,
    PRODUCT_APPLE_PRICE,
    PRODUCT_BANANA,
    PRODUCT_BANANA_PRICE,
    PRODUCT_BANANA_REPLACEMENT,
    PRODUCT_BANANA_REPLACEMENT_PRICE,
    PRODUCT_MILK,
    PRODUCT_MILK_NEW_PRICE,
    PRODUCT_MILK_OLD_PRICE,
    RECIPIENT_NAME,
    STORE_NAME,
)


def _rub(amount: int) -> str:
    """Format integer rubles with the ruble sign."""
    return f"{amount} \u20bd"


class KuperApiStub:
    """Deterministic stub of the 'Kuper' web API for J02."""

    def __init__(self) -> None:
        # Auth state
        self._auth_state: str = "unauthenticated"
        self._sber_popup_open: bool = False

        # Source order 4711 detail items (mutable for variants)
        self._order_4711_items: list[dict[str, Any]] = [
            {"name": PRODUCT_MILK, "price": PRODUCT_MILK_OLD_PRICE, "qty": 1},
            {"name": PRODUCT_BANANA, "price": PRODUCT_BANANA_PRICE, "qty": 1},
            {"name": PRODUCT_APPLE, "price": PRODUCT_APPLE_PRICE, "qty": 1},
        ]

        # History list (visible orders only)
        self._history: list[dict[str, Any]] = [
            {
                "number": ORDER_NUMBER_4711,
                "date": ORDER_DATE_4711,
                "store": STORE_NAME,
                "status": ORDER_STATUS_DELIVERED,
            }
        ]

        # Cart (after reorder, before confirmations)
        self._cart: list[dict[str, Any]] = []
        self._cart_total_rub: int = 0

        # Dialog state
        self._open_dialog: dict[str, Any] | None = None

        # Checkout state
        self._checkout_open: bool = False

        # Bonus + payment
        self._bonus_applied_rub: int = 0
        self._payment_done: bool = False
        self._new_order: dict[str, Any] | None = None

    # ------------------------------------------------------------------
    # Setup helpers (test-only, NOT API methods)
    # ------------------------------------------------------------------
    def reset(self) -> None:
        """Reset stub to initial state."""
        self.__init__()

    def add_history_order(
        self,
        number: str,
        date: str,
        status: str,
        store: str = STORE_NAME,
    ) -> None:
        """Add an order to the history list (for sort/cancel variants)."""
        self._history.append(
            {"number": number, "date": date, "store": store, "status": status}
        )
        self._history.sort(key=lambda o: o["date"], reverse=True)

    def set_order_4711_item_qty(self, item_name: str, qty: int) -> None:
        """Override qty of an item in source order 4711 (for TC-J02-05)."""
        for item in self._order_4711_items:
            if item["name"] == item_name:
                item["qty"] = qty
                return

    def set_history_orders(self, orders: list[dict[str, Any]]) -> None:
        """Replace history entirely with given list (sorted desc)."""
        self._history = sorted(
            list(orders), key=lambda o: o["date"], reverse=True
        )

    # ------------------------------------------------------------------
    # BR-001, BR-013 — authentication
    # ------------------------------------------------------------------
    def open_login_screen(self) -> dict[str, Any]:
        """Get the login screen content."""
        return {
            "options": [AUTH_OPTION_SBER_ID, AUTH_OPTION_PHONE],
            "state": "unauthenticated",
        }

    def start_sber_id_auth(self) -> dict[str, Any]:
        """Click 'Log in via Sber ID' button."""
        self._sber_popup_open = True
        return {"popup_open": True, "type": "sber_id"}

    def confirm_sber_id_auth(self) -> dict[str, Any]:
        """Confirm authorization in Sber ID popup."""
        self._sber_popup_open = False
        self._auth_state = "authenticated"
        return {
            "popup_open": False,
            "state": "authenticated",
            "history_available": True,
            "bonuses_available": True,
        }

    # ------------------------------------------------------------------
    # BR-012, ANS-20, ANS-12, ANS-10 — order history
    # ------------------------------------------------------------------
    def get_history(self) -> list[dict[str, Any]]:
        """Return visible (non-cancelled) orders sorted by date desc."""
        visible = [
            o for o in self._history if o["status"] != "Отменён"
        ]
        return list(visible)

    def get_history_all_including_cancelled(self) -> list[dict[str, Any]]:
        """Return raw history (used only to prove cancelled is hidden)."""
        return list(self._history)

    def is_in_history(self, order_id: str) -> bool:
        """Check whether a given order is visible in the history list."""
        return any(
            o["number"] == order_id for o in self.get_history()
        )

    def attempt_direct_access_to_order(self, order_id: str) -> dict[str, Any]:
        """Direct navigation to an order detail (TC-J02-01 step 3)."""
        for o in self._history:
            if o["number"] == order_id and o["status"] != "Отменён":
                return {"accessible": True, "order_id": order_id}
        return {
            "accessible": False,
            "reason": "not_found_or_cancelled",
            "order_id": order_id,
        }

    def get_order_detail(self, order_id: str) -> dict[str, Any]:
        """Return detail dict for the given order id."""
        if order_id == ORDER_NUMBER_4711:
            return {
                "number": order_id,
                "date": ORDER_DATE_4711,
                "store": STORE_NAME,
                "address": DELIVERY_ADDRESS,
                "recipient": RECIPIENT_NAME,
                "interval": DELIVERY_INTERVAL,
                "method": DELIVERY_METHOD,
                "status": ORDER_STATUS_DELIVERED,
                "items": [dict(i) for i in self._order_4711_items],
            }
        for o in self._history:
            if o["number"] == order_id:
                return {
                    "number": order_id,
                    "date": o["date"],
                    "store": o.get("store", STORE_NAME),
                    "status": o["status"],
                    "items": [],
                }
        return {"number": order_id, "found": False}

    # ------------------------------------------------------------------
    # BR-004, BR-012 — reorder
    # ------------------------------------------------------------------
    def reorder(self, order_id: str) -> dict[str, Any]:
        """Trigger reorder — cart is populated from source order."""
        if order_id != ORDER_NUMBER_4711:
            return {"success": False, "reason": "unknown_order"}
        self._cart = []
        for item in self._order_4711_items:
            self._cart.append(
                {
                    "name": item["name"],
                    "price": item["price"],
                    "qty": item["qty"],
                    "confirmed": False,
                    "replacement_of": None,
                    "excluded_qty": 0,
                }
            )
        self._cart_total_rub = self._compute_total()
        return {
            "cart": [dict(i) for i in self._cart],
            "total": _rub(self._cart_total_rub),
        }

    def _compute_total(self) -> int:
        total = 0
        for item in self._cart:
            price_rub = int(item["price"].replace(" \u20bd", ""))
            total += price_rub * item["qty"]
        return total

    def get_cart(self) -> dict[str, Any]:
        """Return the current cart contents and total."""
        return {
            "items": [dict(i) for i in self._cart],
            "total": _rub(self._cart_total_rub),
        }

    # ------------------------------------------------------------------
    # ANS-05, ANS-08 — price-change dialog
    # ------------------------------------------------------------------
    def open_item_card(self, item_name: str) -> dict[str, Any]:
        """Open an item's card. Returns the dialog if any."""
        item = next((i for i in self._cart if i["name"] == item_name), None)
        if item is None:
            return {"found": False}
        if item_name == PRODUCT_MILK and not item["confirmed"]:
            self._open_dialog = {
                "type": "price_change",
                "item": PRODUCT_MILK,
                "old_price": PRODUCT_MILK_OLD_PRICE,
                "new_price": PRODUCT_MILK_NEW_PRICE,
                "has_confirm": True,
                "has_cancel": True,
            }
        elif item_name == PRODUCT_BANANA and not item["confirmed"]:
            self._open_dialog = {
                "type": "replacement",
                "item": PRODUCT_BANANA,
                "unavailable": True,
                "replacement_name": PRODUCT_BANANA_REPLACEMENT,
                "replacement_price": PRODUCT_BANANA_REPLACEMENT_PRICE,
                "has_confirm": True,
                "has_cancel": True,
            }
        elif item_name == PRODUCT_APPLE and not item["confirmed"]:
            available = min(item["qty"], APPLE_AVAILABLE_QTY)
            self._open_dialog = {
                "type": "partial_availability",
                "item": PRODUCT_APPLE,
                "original_qty": item["qty"],
                "available_qty": available,
                "excluded_qty": item["qty"] - available,
                "price": PRODUCT_APPLE_PRICE,
                "has_confirm": True,
            }
        else:
            self._open_dialog = None
        return {"dialog": self._open_dialog, "item": dict(item)}

    def get_open_dialog(self) -> dict[str, Any] | None:
        """Return the currently open dialog, or None."""
        return self._open_dialog

    def confirm_price_change(
        self, item_name: str, new_price: str = PRODUCT_MILK_NEW_PRICE
    ) -> dict[str, Any]:
        """Confirm new price for the given item."""
        for item in self._cart:
            if item["name"] == item_name:
                item["price"] = new_price
                item["confirmed"] = True
                break
        self._open_dialog = None
        self._cart_total_rub = self._compute_total()
        return {
            "cart": [dict(i) for i in self._cart],
            "total": _rub(self._cart_total_rub),
        }

    # ------------------------------------------------------------------
    # BR-N05, ANS-06 — replacement dialog
    # ------------------------------------------------------------------
    def confirm_replacement(
        self,
        original: str,
        replacement: str = PRODUCT_BANANA_REPLACEMENT,
        replacement_price: str = PRODUCT_BANANA_REPLACEMENT_PRICE,
    ) -> dict[str, Any]:
        """Confirm replacement for the given item."""
        for item in self._cart:
            if item["name"] == original:
                item["name"] = replacement
                item["price"] = replacement_price
                item["replacement_of"] = original
                item["confirmed"] = True
                break
        self._open_dialog = None
        self._cart_total_rub = self._compute_total()
        return {
            "cart": [dict(i) for i in self._cart],
            "total": _rub(self._cart_total_rub),
        }

    # ------------------------------------------------------------------
    # ANS-21 — partial addition dialog
    # ------------------------------------------------------------------
    def confirm_partial_addition(self, item_name: str) -> dict[str, Any]:
        """Confirm partial addition (only available qty stays)."""
        for item in self._cart:
            if item["name"] == item_name:
                item["qty"] = APPLE_AVAILABLE_QTY
                item["excluded_qty"] = self._order_4711_items_apples_qty() - APPLE_AVAILABLE_QTY
                item["confirmed"] = True
                break
        self._open_dialog = None
        self._cart_total_rub = self._compute_total()
        return {
            "cart": [dict(i) for i in self._cart],
            "total": _rub(self._cart_total_rub),
        }

    def _order_4711_items_apples_qty(self) -> int:
        for item in self._order_4711_items:
            if item["name"] == PRODUCT_APPLE:
                return item["qty"]
        return 1

    # ------------------------------------------------------------------
    # BR-005 — cart quantity management
    # ------------------------------------------------------------------
    def decrease_quantity(self, item_name: str, to_qty: int) -> dict[str, Any]:
        """Decrease item qty; if <= 0 the item is removed."""
        for i, item in enumerate(self._cart):
            if item["name"] == item_name:
                if to_qty <= 0:
                    self._cart.pop(i)
                else:
                    item["qty"] = to_qty
                break
        self._cart_total_rub = self._compute_total()
        return {
            "cart": [dict(i) for i in self._cart],
            "total": _rub(self._cart_total_rub),
        }

    # ------------------------------------------------------------------
    # ANS-07, BR-008 — checkout form
    # ------------------------------------------------------------------
    def open_checkout_form(self) -> dict[str, Any]:
        """Open the checkout form."""
        self._checkout_open = True
        return {
            "open": True,
            "selected_method": DELIVERY_METHOD,
            "available_methods": [DELIVERY_METHOD],
        }

    def get_delivery_data(self) -> dict[str, Any]:
        """Return the delivery data block of the checkout form."""
        return {
            "address": DELIVERY_ADDRESS,
            "recipient": RECIPIENT_NAME,
            "interval": DELIVERY_INTERVAL,
            "method": DELIVERY_METHOD,
            "address_editable": True,
            "recipient_editable": True,
            "interval_editable": True,
        }

    # ------------------------------------------------------------------
    # BR-009 — totals block
    # ------------------------------------------------------------------
    def get_totals(self) -> dict[str, Any]:
        """Return the totals block of the checkout form."""
        items_total_rub = self._cart_total_rub
        delivery_rub = int(DELIVERY_FEE.replace(" \u20bd", ""))
        packing_rub = int(PACKING_FEE.replace(" \u20bd", ""))
        grand_rub = items_total_rub + delivery_rub + packing_rub
        return {
            "items_total": _rub(items_total_rub),
            "delivery_fee": DELIVERY_FEE,
            "packing_fee": PACKING_FEE,
            "grand_total": _rub(grand_rub),
        }

    # ------------------------------------------------------------------
    # ANS-03 — partial bonus payment
    # ------------------------------------------------------------------
    def apply_bonus(self, amount: int) -> dict[str, Any]:
        """Apply a bonus amount; returns new remainder."""
        self._bonus_applied_rub = amount
        items_total_rub = self._cart_total_rub
        delivery_rub = int(DELIVERY_FEE.replace(" \u20bd", ""))
        packing_rub = int(PACKING_FEE.replace(" \u20bd", ""))
        grand_rub = items_total_rub + delivery_rub + packing_rub
        remaining_rub = grand_rub - amount
        return {
            "bonus_label": BONUS_LABEL,
            "bonus_applied": amount,
            "card_remainder": _rub(remaining_rub),
        }

    # ------------------------------------------------------------------
    # BR-010 — payment
    # ------------------------------------------------------------------
    def pay(self) -> dict[str, Any]:
        """Execute payment with the bound card."""
        self._payment_done = True
        items_total_rub = self._cart_total_rub
        delivery_rub = int(DELIVERY_FEE.replace(" \u20bd", ""))
        packing_rub = int(PACKING_FEE.replace(" \u20bd", ""))
        grand_rub = items_total_rub + delivery_rub + packing_rub
        card_rub = grand_rub - self._bonus_applied_rub
        self._new_order = {
            "number": NEW_ORDER_NUMBER,
            "store": STORE_NAME,
            "address": DELIVERY_ADDRESS,
            "recipient": RECIPIENT_NAME,
            "interval": DELIVERY_INTERVAL,
            "method": DELIVERY_METHOD,
            "status": NEW_ORDER_STATUS,
            "card_charged": _rub(card_rub),
            "bonus_applied": self._bonus_applied_rub,
        }
        # Append the new order to history (newest first).
        self._history.insert(
            0,
            {
                "number": NEW_ORDER_NUMBER,
                "date": "2026-08-18",
                "store": STORE_NAME,
                "status": NEW_ORDER_STATUS,
            },
        )
        return {
            "success": True,
            "new_order": dict(self._new_order),
        }

    # ------------------------------------------------------------------
    # BR-011, BR-012 — post-payment state
    # ------------------------------------------------------------------
    def get_new_order(self) -> dict[str, Any] | None:
        """Return the freshly created order, if any."""
        return self._new_order

    def get_history_after_reorder(self) -> list[dict[str, Any]]:
        """Return visible history after the new order is created."""
        return self.get_history()

    def clear_cart(self) -> None:
        """Empty the cart (matches post-payment state in TC-J02-00)."""
        self._cart = []
        self._cart_total_rub = 0
