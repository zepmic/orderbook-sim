from decimal import Decimal

import pytest

from orderbook_sim.model import Order, OrderType, Side, Trade
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


def test_crossing_order_does_not_rest():
    book = OrderBook()
    book.add_limit(make_order(1, Side.SELL, 100, qty=5))
    trades = book.add_limit(make_order(2, Side.BUY, 100, qty=5))
    assert trades == [Trade(price=100, qty=5, taker_order_id=2, maker_order_id=1, ts=0)]
    assert len(book.asks) == 0
    assert len(book.bids) == 0


def test_non_crossing_order_rests_without_trades():
    book = OrderBook()
    book.add_limit(make_order(1, Side.SELL, 101, qty=5))
    trades = book.add_limit(make_order(2, Side.BUY, 100, qty=5))
    assert trades == []
    assert book.bids.level(100)[0].id == 2
    assert book.asks.level(101)[0].id == 1


def test_taker_trades_at_maker_price_not_taker_price():
    book = OrderBook()
    book.add_limit(make_order(1, Side.SELL, 98, qty=5))
    trades = book.add_limit(make_order(2, Side.BUY, 100, qty=5))
    assert trades[0].price == 98


def test_partial_fill_leaves_remainder_resting():
    book = OrderBook()
    book.add_limit(make_order(1, Side.SELL, 100, qty=3))
    trades = book.add_limit(make_order(2, Side.BUY, 100, qty=5))
    assert trades == [Trade(price=100, qty=3, taker_order_id=2, maker_order_id=1, ts=0)]
    assert len(book.asks) == 0
    resting = book.bids.level(100)
    assert len(resting) == 1
    assert resting[0].id == 2
    assert resting[0].qty == 2


def test_maker_keeps_remaining_qty_when_taker_is_smaller():
    book = OrderBook()
    book.add_limit(make_order(1, Side.SELL, 100, qty=5))
    trades = book.add_limit(make_order(2, Side.BUY, 100, qty=3))
    assert trades == [Trade(price=100, qty=3, taker_order_id=2, maker_order_id=1, ts=0)]
    assert len(book.bids) == 0
    resting = book.asks.level(100)
    assert len(resting) == 1
    assert resting[0].id == 1
    assert resting[0].qty == 2


def test_matching_respects_time_priority_at_same_price():
    book = OrderBook()
    book.add_limit(make_order(1, Side.SELL, 100, qty=3, ts=0))
    book.add_limit(make_order(2, Side.SELL, 100, qty=3, ts=1))
    trades = book.add_limit(make_order(3, Side.BUY, 100, qty=3))
    assert trades == [Trade(price=100, qty=3, taker_order_id=3, maker_order_id=1, ts=0)]
    assert book.asks.level(100) == [make_order(2, Side.SELL, 100, qty=3, ts=1)]


def test_matching_respects_price_priority_across_levels():
    book = OrderBook()
    book.add_limit(make_order(1, Side.SELL, 101, qty=5))
    book.add_limit(make_order(2, Side.SELL, 100, qty=5))
    trades = book.add_limit(make_order(3, Side.BUY, 101, qty=5))
    assert trades == [Trade(price=100, qty=5, taker_order_id=3, maker_order_id=2, ts=0)]
    assert book.asks.level(100) == []
    assert len(book.asks.level(101)) == 1


def test_order_can_sweep_multiple_price_levels():
    book = OrderBook()
    book.add_limit(make_order(1, Side.SELL, 100, qty=3))
    book.add_limit(make_order(2, Side.SELL, 101, qty=4))
    trades = book.add_limit(make_order(3, Side.BUY, 101, qty=5))
    assert trades == [
        Trade(price=100, qty=3, taker_order_id=3, maker_order_id=1, ts=0),
        Trade(price=101, qty=2, taker_order_id=3, maker_order_id=2, ts=0),
    ]
    assert len(book.asks) == 1
    assert book.asks.level(101)[0].qty == 2
    assert len(book.bids) == 0


def test_partial_sweep_then_price_limit_rests_remainder_at_own_price():
    book = OrderBook()
    book.add_limit(make_order(1, Side.SELL, 99, qty=2))
    book.add_limit(make_order(2, Side.SELL, 105, qty=10))
    trades = book.add_limit(make_order(3, Side.BUY, 100, qty=5))
    assert trades == [Trade(price=99, qty=2, taker_order_id=3, maker_order_id=1, ts=0)]
    assert book.asks.level(99) == []
    assert book.asks.level(105)[0].qty == 10
    resting = book.bids.level(100)
    assert len(resting) == 1
    assert resting[0].id == 3
    assert resting[0].qty == 3


def test_add_limit_rejects_duplicate_id_after_resting_as_maker():
    book = OrderBook()
    book.add_limit(make_order(1, Side.SELL, 100, qty=3))
    book.add_limit(make_order(2, Side.BUY, 100, qty=1))
    with pytest.raises(ValueError):
        book.add_limit(make_order(1, Side.BUY, 100))
