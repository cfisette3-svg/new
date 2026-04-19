from __future__ import annotations

import hashlib
from dataclasses import dataclass
from datetime import date, timedelta
from typing import Protocol


@dataclass(frozen=True)
class DividendEvent:
    symbol: str
    ex_date: date
    pay_date: date
    amount_per_share: float


@dataclass(frozen=True)
class OptionQuote:
    symbol: str
    strike: float
    expiration: date
    bid: float
    implied_vol: float


@dataclass(frozen=True)
class Quote:
    symbol: str
    price: float


class MarketAdapter(Protocol):
    def quote(self, symbol: str) -> Quote: ...
    def upcoming_dividends(self, symbol: str, horizon_days: int = 365) -> list[DividendEvent]: ...
    def weekly_calls(self, symbol: str, spot: float) -> list[OptionQuote]: ...


def _seed(symbol: str) -> int:
    """Deterministic per-symbol seed so sample data is stable across runs."""
    return int(hashlib.sha256(symbol.encode()).hexdigest()[:8], 16)


class SampleMarketAdapter:
    """Offline adapter producing deterministic pseudo-real data.

    Swap this out for a real provider (yfinance, Polygon, Tradier) by
    implementing the MarketAdapter protocol.
    """

    def __init__(self, today: date | None = None) -> None:
        self._today = today or date.today()

    def quote(self, symbol: str) -> Quote:
        s = _seed(symbol)
        price = 20 + (s % 45000) / 100.0
        return Quote(symbol=symbol, price=round(price, 2))

    def upcoming_dividends(self, symbol: str, horizon_days: int = 365) -> list[DividendEvent]:
        s = _seed(symbol)
        if s % 5 == 0:
            return []  # roughly 20% of symbols do not pay a dividend
        yield_bps = 150 + (s % 450)  # 1.5% - 6.0%
        spot = self.quote(symbol).price
        annual = spot * yield_bps / 10000.0
        per_quarter = round(annual / 4.0, 2)
        first_offset = (s % 85) + 5
        events: list[DividendEvent] = []
        cursor = self._today + timedelta(days=first_offset)
        while (cursor - self._today).days <= horizon_days:
            events.append(
                DividendEvent(
                    symbol=symbol,
                    ex_date=cursor,
                    pay_date=cursor + timedelta(days=21),
                    amount_per_share=per_quarter,
                )
            )
            cursor += timedelta(days=91)
        return events

    def weekly_calls(self, symbol: str, spot: float) -> list[OptionQuote]:
        s = _seed(symbol)
        expiration = self._next_friday()
        out: list[OptionQuote] = []
        for i, pct in enumerate((1.01, 1.02, 1.03, 1.05)):
            strike = round(spot * pct, 1)
            iv = 0.22 + ((s >> (i * 3)) % 40) / 100.0
            intrinsic = max(0.0, spot - strike)
            extrinsic = spot * iv * 0.04 * (1.05 - pct)
            bid = round(max(0.02, intrinsic + extrinsic), 2)
            out.append(
                OptionQuote(
                    symbol=symbol,
                    strike=strike,
                    expiration=expiration,
                    bid=bid,
                    implied_vol=round(iv, 3),
                )
            )
        return out

    def _next_friday(self) -> date:
        t = self._today
        delta = (4 - t.weekday()) % 7
        if delta == 0:
            delta = 7
        return t + timedelta(days=delta)
