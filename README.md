# orderbook-sim

A limit order book with a matching engine, plus a few simple simulated traders. The goal is to watch how spread and depth come out of order flow. It is a simulation only: no real orders, no exchange connections, no API keys.

## Idea

The book holds buy and sell limit orders at price levels (ticks). Incoming orders are matched against it with price-time priority. On top of that, simple agents such as a market maker and noise traders generate order flow, so the book can be observed and measured over time.

## Layout

```
src/orderbook_sim/   source code (order book, matching engine, agents)
tests/               pytest tests
```

## Examples

Not written yet. Runnable example scripts will go here, starting with a basic simulation run that prints the state of the book.

## Development

```bash
pip install -e ".[dev]"
python -m pytest -q
```
