"""Optional yfinance-backed market adapter.

Requires `pip install yfinance`. Import lazily so the rest of the package
works without the dependency installed.
"""

from __future__ import annotations

from datetime import date, datetime, timedelta

from .market import DividendEvent, OptionQuote, Quote


class YFinanceMarketAdapter:
    def __init__(self, today: date | None = None) -> None:
        try:
            import yfinance  # noqa: F401
        except ImportError as exc:
            raise ImportError(
                "YFinanceMarketAdapter requires `pip install yfinance`"
            ) from exc
        self._today = today or date.today()
        self._cache: dict[str, object] = {}

    def _ticker(self, symbol: str):
        import yfinance as yf

        if symbol not in self._cache:
            self._cache[symbol] = yf.Ticker(symbol)
        return self._cache[symbol]

    def quote(self, symbol: str) -> Quote:
        t = self._ticker(symbol)
        info = getattr(t, "fast_info", None) or t.info
        price = float(info.get("last_price") or info.get("regularMarketPrice") or 0.0)
        return Quote(symbol=symbol, price=round(price, 2))

    def upcoming_dividends(self, symbol: str, horizon_days: int = 365) -> list[DividendEvent]:
        t = self._ticker(symbol)
        series = t.dividends
        if series is None or len(series) == 0:
            return []
        last = series.tail(8)
        if len(last) < 2:
            return []
        timestamps = list(last.index)
        gaps = [
            (timestamps[i + 1] - timestamps[i]).days for i in range(len(timestamps) - 1)
        ]
        cadence = int(sum(gaps) / len(gaps)) or 91
        last_ex = timestamps[-1].date()
        last_amt = float(last.iloc[-1])

        events: list[DividendEvent] = []
        cursor = last_ex + timedelta(days=cadence)
        while (cursor - self._today).days <= horizon_days:
            if cursor >= self._today:
                events.append(
                    DividendEvent(
                        symbol=symbol,
                        ex_date=cursor,
                        pay_date=cursor + timedelta(days=21),
                        amount_per_share=round(last_amt, 4),
                    )
                )
            cursor += timedelta(days=cadence)
        return events

    def weekly_calls(self, symbol: str, spot: float) -> list[OptionQuote]:
        t = self._ticker(symbol)
        expirations = list(t.options or [])
        if not expirations:
            return []
        # pick the nearest expiration within 10 days (weekly)
        target = None
        for exp_str in expirations:
            exp = datetime.strptime(exp_str, "%Y-%m-%d").date()
            if 0 < (exp - self._today).days <= 10:
                target = (exp_str, exp)
                break
        if target is None:
            exp_str = expirations[0]
            target = (exp_str, datetime.strptime(exp_str, "%Y-%m-%d").date())

        chain = t.option_chain(target[0])
        calls = chain.calls
        out: list[OptionQuote] = []
        otm = calls[calls["strike"] >= spot].head(6)
        for _, row in otm.iterrows():
            out.append(
                OptionQuote(
                    symbol=symbol,
                    strike=float(row["strike"]),
                    expiration=target[1],
                    bid=float(row["bid"] or 0.0),
                    implied_vol=float(row.get("impliedVolatility") or 0.0),
                )
            )
        return out

    def weekly_puts(self, symbol: str, spot: float) -> list[OptionQuote]:
        t = self._ticker(symbol)
        expirations = list(t.options or [])
        if not expirations:
            return []
        target = None
        for exp_str in expirations:
            exp = datetime.strptime(exp_str, "%Y-%m-%d").date()
            if 0 < (exp - self._today).days <= 10:
                target = (exp_str, exp)
                break
        if target is None:
            exp_str = expirations[0]
            target = (exp_str, datetime.strptime(exp_str, "%Y-%m-%d").date())

        chain = t.option_chain(target[0])
        puts = chain.puts
        out: list[OptionQuote] = []
        otm = puts[puts["strike"] <= spot].tail(6)
        for _, row in otm.iterrows():
            out.append(
                OptionQuote(
                    symbol=symbol,
                    strike=float(row["strike"]),
                    expiration=target[1],
                    bid=float(row["bid"] or 0.0),
                    implied_vol=float(row.get("impliedVolatility") or 0.0),
                )
            )
        return out
