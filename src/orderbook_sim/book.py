"""One side of the order book: resting limit orders grouped by price level."""

from collections import deque
from dataclasses import replace

from .model import Order, OrderType, PriceLevel, Side


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

    def get(self, order_id: int) -> Order | None:
        """Return the resting order with the given id without removing it, or None."""
        for queue in self._levels.values():
            for order in queue:
                if order.id == order_id:
                    return order
        return None

    def reduce_qty(self, order_id: int, new_qty: int) -> Order:
        """Lower a resting order's quantity while keeping its place in the queue.

        Leaving the order at its existing position preserves its time
        priority among the other orders at the same price level. Raises
        KeyError if no resting order with the given id exists, and
        ValueError if new_qty is not strictly smaller than the order's
        current quantity.
        """
        for queue in self._levels.values():
            for i, order in enumerate(queue):
                if order.id == order_id:
                    if new_qty >= order.qty:
                        raise ValueError(f"new_qty {new_qty} is not a reduction from {order.qty}")
                    queue[i] = replace(order, qty=new_qty)
                    return queue[i]
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

    def fill_front(self, qty: int) -> Order:
        """Reduce the order at the front of the best price level by qty.

        Removes the order once it is fully filled, otherwise keeps it at the
        front of its queue with the remaining quantity, preserving time
        priority. Returns the order as it was before the fill.
        """
        best = self.best_price()
        if best is None:
            raise KeyError("no resting orders to fill")
        queue = self._levels[best]
        front = queue[0]
        if qty > front.qty:
            raise ValueError(f"fill qty {qty} exceeds resting qty {front.qty}")
        if qty == front.qty:
            queue.popleft()
            if not queue:
                del self._levels[best]
        else:
            queue[0] = replace(front, qty=front.qty - qty)
        return front

    def level(self, price: int) -> list[Order]:
        """Return the orders resting at a price level, in queue order."""
        return list(self._levels.get(price, ()))

    def top_levels(self, n: int) -> list[PriceLevel]:
        """Return the n best price levels with their total resting quantity.

        Levels are ordered best price first. If the side has fewer than n
        levels, all of them are returned.
        """
        if n <= 0:
            raise ValueError(f"n must be positive, got {n}")
        prices = sorted(self._levels, reverse=self.side is Side.BUY)
        return [
            PriceLevel(price=price, qty=sum(order.qty for order in self._levels[price]))
            for price in prices[:n]
        ]

    def __len__(self) -> int:
        return sum(len(queue) for queue in self._levels.values())
