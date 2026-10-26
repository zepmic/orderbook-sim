import pytest

from orderbook_sim.book import BookSide
from orderbook_sim.model import Order, OrderType, Side


def make_order(id, side, price, qty=1, ts=0):
    return Order(id=id, side=side, order_type=OrderType.LIMIT, price=price, qty=qty, ts=ts)


def test_empty_side_has_no_best_price_and_no_peek():
    side = BookSide(Side.BUY)
    assert side.best_price() is None
    assert side.peek() is None
    assert len(side) == 0


def test_buy_side_best_price_is_highest():
    side = BookSide(Side.BUY)
    side.add(make_order(1, Side.BUY, 100))
    side.add(make_order(2, Side.BUY, 101))
    side.add(make_order(3, Side.BUY, 99))
    assert side.best_price() == 101


def test_sell_side_best_price_is_lowest():
    side = BookSide(Side.SELL)
    side.add(make_order(1, Side.SELL, 100))
    side.add(make_order(2, Side.SELL, 99))
    side.add(make_order(3, Side.SELL, 101))
    assert side.best_price() == 99


def test_orders_at_same_level_are_fifo():
    side = BookSide(Side.BUY)
    first = make_order(1, Side.BUY, 100, ts=0)
    second = make_order(2, Side.BUY, 100, ts=1)
    side.add(first)
    side.add(second)
    assert side.level(100) == [first, second]
    assert side.peek() is first


def test_remove_takes_order_out_of_its_level():
    side = BookSide(Side.BUY)
    first = make_order(1, Side.BUY, 100)
    second = make_order(2, Side.BUY, 100)
    side.add(first)
    side.add(second)
    removed = side.remove(1)
    assert removed is first
    assert side.level(100) == [second]


def test_remove_drops_level_once_empty():
    side = BookSide(Side.BUY)
    side.add(make_order(1, Side.BUY, 100))
    side.remove(1)
    assert side.best_price() is None
    assert side.level(100) == []


def test_remove_unknown_order_raises():
    side = BookSide(Side.BUY)
    side.add(make_order(1, Side.BUY, 100))
    with pytest.raises(KeyError):
        side.remove(999)


def test_add_rejects_market_order():
    side = BookSide(Side.BUY)
    market_order = Order(id=1, side=Side.BUY, order_type=OrderType.MARKET, price=None, qty=1, ts=0)
    with pytest.raises(ValueError):
        side.add(market_order)


def test_add_rejects_order_from_other_side():
    side = BookSide(Side.BUY)
    with pytest.raises(ValueError):
        side.add(make_order(1, Side.SELL, 100))


def test_len_counts_all_resting_orders_across_levels():
    side = BookSide(Side.BUY)
    side.add(make_order(1, Side.BUY, 100))
    side.add(make_order(2, Side.BUY, 100))
    side.add(make_order(3, Side.BUY, 99))
    assert len(side) == 3
