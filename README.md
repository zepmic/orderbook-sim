# orderbook-sim

Simulation eines Limit-Orderbuchs mit Matching-Engine und einfachen
Marktteilnehmern, um Marktmikrostruktur-Effekte (Spread, Tiefe,
Preisbildung) nachzuvollziehen. Reine Simulation und Analyse: keine
echten Orders, keine Börsenzugänge, keine API-Keys.

## Projektidee

Ein Orderbuch führt Kauf- und Verkaufslimits auf verschiedenen
Preisstufen (Ticks). Eine Matching-Engine setzt eingehende Orders
gegen das Buch um (Preis-Zeit-Priorität). Darauf aufbauend simulieren
einfache Marktteilnehmer (z. B. Market Maker, Noise Trader) Orderflow,
damit sich das Verhalten des Orderbuchs über die Zeit beobachten und
auswerten lässt.

## Struktur

```
src/orderbook_sim/   Quellcode (Orderbuch, Matching-Engine, Teilnehmer)
tests/                Tests (pytest)
```

## Beispiele

*(folgt – Platzhalter für ausführbare Beispielskripte, z. B. ein
einfacher Simulationslauf mit Ausgabe des Orderbuchzustands)*

## Entwicklung

```bash
pip install -e ".[dev]"
python -m pytest -q
```
