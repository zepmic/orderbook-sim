from decimal import Decimal

import pytest

from orderbook_sim.model import Order, OrderType, Side
from orderbook_sim.orderbook import OrderBook


def make_order(id, side, price, qty=1, ts=0):
    return Order(id=id, side=side, order_type=OrderType.LIMIT, price=price, qty=qty, ts=ts)


def test_add_limit_puts_buy_order_on_bids():
    book = OrderBook()
    order = make_order(1, Side.BUY, 100)
    book.add_limit(order)
    assert book.bids.level(100) == [order]
    assert len(book.asks) == 0


def test_add_limit_puts_sell_order_on_asks():
    book = OrderBook()
    order = make_order(1, Side.SELL, 100)
    book.add_limit(order)
    assert book.asks.level(100) == [order]
    assert len(book.bids) == 0


def test_add_limit_keeps_both_sides_independent():
    book = OrderBook()
    buy = make_order(1, Side.BUY, 99)
    sell = make_order(2, Side.SELL, 101)
    book.add_limit(buy)
    book.add_limit(sell)
    assert book.bids.best_price() == 99
    assert book.asks.best_price() == 101


def test_add_limit_rejects_market_order():
    book = OrderBook()
    market_order = Order(id=1, side=Side.BUY, order_type=OrderType.MARKET, price=None, qty=1, ts=0)
    with pytest.raises(ValueError):
        book.add_limit(market_order)


def test_add_limit_rejects_duplicate_id_across_sides():
    book = OrderBook()
    book.add_limit(make_order(1, Side.BUY, 100))
    with pytest.raises(ValueError):
        book.add_limit(make_order(1, Side.SELL, 101))


def test_best_bid_and_ask_reflect_top_of_book():
    book = OrderBook()
    book.add_limit(make_order(1, Side.BUY, 99))
    book.add_limit(make_order(2, Side.BUY, 100))
    book.add_limit(make_order(3, Side.SELL, 102))
    book.add_limit(make_order(4, Side.SELL, 101))
    assert book.best_bid() == 100
    assert book.best_ask() == 101


def test_best_bid_and_ask_are_none_on_empty_book():
    book = OrderBook()
    assert book.best_bid() is None
    assert book.best_ask() is None


def test_spread_and_mid_price():
    book = OrderBook()
    book.add_limit(make_order(1, Side.BUY, 99))
    book.add_limit(make_order(2, Side.SELL, 102))
    assert book.spread() == 3
    assert book.mid_price() == Decimal("100.5")


def test_spread_and_mid_price_are_none_when_one_side_is_empty():
    book = OrderBook()
    book.add_limit(make_order(1, Side.BUY, 99))
    assert book.spread() is None
    assert book.mid_price() is None
