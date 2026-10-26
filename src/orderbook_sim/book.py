"""One side of the order book: resting limit orders grouped by price level."""

from collections import deque

from .model import Order, OrderType, Side


class BookSide:
    """Resting limit orders for one side, kept in FIFO queues per price level.

    Orders at the same price are matched in arrival order (time priority).
    The best price is the highest for a buy side and the lowest for a sell side.
    """

    def __init__(self, side: Side) -> None:
        self.side = side
        self._levels: dict[int, deque[Order]] = {}

    def add(self, order: Order) -> None:
        """Add a resting limit order to the back of its price level's queue."""
        if order.order_type is not OrderType.LIMIT:
            raise ValueError("only limit orders can rest on the book")
        if order.side is not self.side:
            raise ValueError(f"order side {order.side} does not match book side {self.side}")
        self._levels.setdefault(order.price, deque()).append(order)

    def remove(self, order_id: int) -> Order:
        """Remove and return the resting order with the given id."""
        for price, queue in list(self._levels.items()):
            for order in queue:
                if order.id == order_id:
                    queue.remove(order)
                    if not queue:
                        del self._levels[price]
                    return order
        raise KeyError(f"no resting order with id {order_id}")

    def best_price(self) -> int | None:
        """Return the best price on this side, or None if the side is empty."""
        if not self._levels:
            return None
        return max(self._levels) if self.side is Side.BUY else min(self._levels)

    def peek(self) -> Order | None:
        """Return the order at the front of the best price level, or None if empty."""
        best = self.best_price()
        if best is None:
            return None
        return self._levels[best][0]

    def level(self, price: int) -> list[Order]:
        """Return the orders resting at a price level, in queue order."""
        return list(self._levels.get(price, ()))

    def __len__(self) -> int:
        return sum(len(queue) for queue in self._levels.values())
