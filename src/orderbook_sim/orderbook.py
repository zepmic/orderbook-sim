"""The order book: both sides together, with insertion but no matching yet."""

from decimal import Decimal

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

    def best_bid(self) -> int | None:
        """Return the highest resting buy price, or None if there are no bids."""
        return self.bids.best_price()

    def best_ask(self) -> int | None:
        """Return the lowest resting sell price, or None if there are no asks."""
        return self.asks.best_price()

    def spread(self) -> int | None:
        """Return best ask minus best bid, or None if either side is empty."""
        bid, ask = self.best_bid(), self.best_ask()
        if bid is None or ask is None:
            return None
        return ask - bid

    def mid_price(self) -> Decimal | None:
        """Return the average of best bid and best ask, or None if either side is empty."""
        bid, ask = self.best_bid(), self.best_ask()
        if bid is None or ask is None:
            return None
        return Decimal(bid + ask) / 2
