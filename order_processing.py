from __future__ import annotations
from abc import ABC, abstractmethod
from typing import List, Optional
from notification_system import event_manager


# --- State Pattern: Order Status Management ---
class OrderState(ABC):
    """Define a interface para todos os estados de um pedido."""

    @abstractmethod
    def next_state(self, order: Order):
        pass

    @abstractmethod
    def get_status(self) -> str:
        pass


class PendingState(OrderState):
    def next_state(self, order: Order):
        order.set_state(PaidState())
        event_manager.notify("order:paid", {"order_id": order.id, "status": "Paid"})

    def get_status(self) -> str:
        return "Pending"


class PaidState(OrderState):
    def next_state(self, order: Order):
        order.set_state(ShippedState())
        event_manager.notify("order:shipped", {"order_id": order.id, "status": "Shipped"})

    def get_status(self) -> str:
        return "Paid"


class ShippedState(OrderState):
    def next_state(self, order: Order):
        order.set_state(DeliveredState())
        event_manager.notify("order:delivered", {"order_id": order.id, "status": "Delivered"})

    def get_status(self) -> str:
        return "Shipped"


class DeliveredState(OrderState):
    def next_state(self, order: Order):
        # Estado final, nenhuma transição
        pass

    def get_status(self) -> str:
        return "Delivered"


# --- Main Object: Order ---
class Order:
    def __init__(self, order_id: int, products: List[str], total_price: float):
        self.id = order_id
        self.products = tuple(products)
        self.total_price = total_price
        self._state: OrderState = PendingState()  # Initial state

    def set_state(self, state: OrderState):
        self._state = state
        print(f"Pedido {self.id} mudou para o estado: {self._state.get_status()}")

    def proceed_to_next_status(self):
        self._state.next_state(self)

    @property
    def status(self):
        return self._state.get_status()

    def __str__(self):
        return f"Order(id={self.id}, status='{self.status}', products={self.products}, total={self.total_price})"


# --- Builder Pattern: Order Builder ---
class OrderBuilder:
    """Construtor para criar um objeto Order de forma segura."""

    def __init__(self):
        self._order_id: Optional[int] = None
        self._products: List[str] = []
        self._total_price: float = 0.0

    def set_id(self, order_id: int) -> OrderBuilder:
        self._order_id = order_id
        return self

    def add_product(self, product: str, price: float) -> OrderBuilder:
        self._products.append(product)
        self._total_price += price
        return self

    def apply_shipping(self, shipping_cost: float) -> OrderBuilder:
        self._total_price += shipping_cost
        return self

    def build(self) -> Order:
        if not self._order_id or not self._products:
            raise ValueError("ID do pedido e produtos são necessários para construir um pedido.")

        order = Order(
            order_id=self._order_id,
            products=self._products,
            total_price=self._total_price
        )
        event_manager.notify("order:created", {"order_id": order.id, "status": order.status})
        return order