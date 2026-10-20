import pytest

from orderbook_sim.model import Order, OrderType, Side, Trade


def test_create_limit_order():
    order = Order(id=1, side=Side.BUY, order_type=OrderType.LIMIT, price=100, qty=5, ts=0)
    assert order.side is Side.BUY
    assert order.order_type is OrderType.LIMIT
    assert order.price == 100
    assert order.qty == 5
    assert order.ts == 0


def test_create_market_order_has_no_price():
    order = Order(id=1, side=Side.SELL, order_type=OrderType.MARKET, price=None, qty=5, ts=0)
    assert order.price is None


@pytest.mark.parametrize("bad_id", [0, -1])
def test_id_must_be_positive(bad_id):
    with pytest.raises(ValueError):
        Order(id=bad_id, side=Side.BUY, order_type=OrderType.LIMIT, price=100, qty=5, ts=0)


@pytest.mark.parametrize("bad_qty", [0, -5])
def test_qty_must_be_positive(bad_qty):
    with pytest.raises(ValueError):
        Order(id=1, side=Side.BUY, order_type=OrderType.LIMIT, price=100, qty=bad_qty, ts=0)


def test_ts_must_not_be_negative():
    with pytest.raises(ValueError):
        Order(id=1, side=Side.BUY, order_type=OrderType.LIMIT, price=100, qty=5, ts=-1)


@pytest.mark.parametrize("bad_price", [None, 0, -10])
def test_limit_order_needs_positive_price(bad_price):
    with pytest.raises(ValueError):
        Order(id=1, side=Side.BUY, order_type=OrderType.LIMIT, price=bad_price, qty=5, ts=0)


def test_market_order_rejects_price():
    with pytest.raises(ValueError):
        Order(id=1, side=Side.BUY, order_type=OrderType.MARKET, price=100, qty=5, ts=0)


def test_side_must_be_enum_member():
    with pytest.raises(ValueError):
        Order(id=1, side="buy", order_type=OrderType.LIMIT, price=100, qty=5, ts=0)


def test_order_type_must_be_enum_member():
    with pytest.raises(ValueError):
        Order(id=1, side=Side.BUY, order_type="limit", price=100, qty=5, ts=0)


def test_create_trade():
    trade = Trade(price=100, qty=5, taker_order_id=2, maker_order_id=1, ts=0)
    assert trade.price == 100
    assert trade.qty == 5
    assert trade.taker_order_id == 2
    assert trade.maker_order_id == 1
    assert trade.ts == 0


@pytest.mark.parametrize("bad_price", [0, -10])
def test_trade_price_must_be_positive(bad_price):
    with pytest.raises(ValueError):
        Trade(price=bad_price, qty=5, taker_order_id=2, maker_order_id=1, ts=0)


@pytest.mark.parametrize("bad_qty", [0, -5])
def test_trade_qty_must_be_positive(bad_qty):
    with pytest.raises(ValueError):
        Trade(price=100, qty=bad_qty, taker_order_id=2, maker_order_id=1, ts=0)


@pytest.mark.parametrize("bad_id", [0, -1])
def test_trade_taker_order_id_must_be_positive(bad_id):
    with pytest.raises(ValueError):
        Trade(price=100, qty=5, taker_order_id=bad_id, maker_order_id=1, ts=0)


@pytest.mark.parametrize("bad_id", [0, -1])
def test_trade_maker_order_id_must_be_positive(bad_id):
    with pytest.raises(ValueError):
        Trade(price=100, qty=5, taker_order_id=2, maker_order_id=bad_id, ts=0)


def test_trade_taker_and_maker_must_differ():
    with pytest.raises(ValueError):
        Trade(price=100, qty=5, taker_order_id=1, maker_order_id=1, ts=0)


def test_trade_ts_must_not_be_negative():
    with pytest.raises(ValueError):
        Trade(price=100, qty=5, taker_order_id=2, maker_order_id=1, ts=-1)
