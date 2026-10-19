"""Core data model for orders."""

from dataclasses import dataclass
from enum import Enum


class Side(Enum):
    """Buy or sell side of an order."""

    BUY = "buy"
    SELL = "sell"


class OrderType(Enum):
    """Limit orders rest on the book, market orders execute immediately."""

    LIMIT = "limit"
    MARKET = "market"


@dataclass(frozen=True)
class Order:
    """A single order submitted to the book.

    Price and quantity are integer ticks, never floats.
    """

    id: int
    side: Side
    order_type: OrderType
    price: int | None
    qty: int
    ts: int

    def __post_init__(self) -> None:
        if not isinstance(self.side, Side):
            raise ValueError(f"side must be a Side, got {self.side!r}")
        if not isinstance(self.order_type, OrderType):
            raise ValueError(f"order_type must be an OrderType, got {self.order_type!r}")
        if self.id <= 0:
            raise ValueError(f"id must be positive, got {self.id}")
        if self.qty <= 0:
            raise ValueError(f"qty must be positive, got {self.qty}")
        if self.ts < 0:
            raise ValueError(f"ts must not be negative, got {self.ts}")
        if self.order_type is OrderType.LIMIT:
            if self.price is None or self.price <= 0:
                raise ValueError(f"limit orders need a positive price, got {self.price}")
        elif self.price is not None:
            raise ValueError("market orders must not set a price")
