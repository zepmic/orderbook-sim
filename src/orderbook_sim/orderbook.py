"""The order book: both sides together, with insertion but no matching yet."""

from .book import BookSide
from .model import Order, OrderType, Side


class OrderBook:
    """Holds the resting buy and sell orders for one instrument."""

    def __init__(self) -> None:
        self.bids = BookSide(Side.BUY)
        self.asks = BookSide(Side.SELL)
        self._resting_ids: set[int] = set()

    def add_limit(self, order: Order) -> None:
        """Insert a limit order into the book, without matching it against the other side."""
        if order.order_type is not OrderType.LIMIT:
            raise ValueError("only limit orders can be inserted without matching")
        if order.id in self._resting_ids:
            raise ValueError(f"order id {order.id} is already resting on the book")
        side = self.bids if order.side is Side.BUY else self.asks
        side.add(order)
        self._resting_ids.add(order.id)
