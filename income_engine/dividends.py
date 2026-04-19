from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from datetime import date, timedelta

from .adapters.market import DividendEvent, MarketAdapter
from .portfolio import Portfolio


@dataclass(frozen=True)
class DividendProjection:
    monthly_income: dict[str, float]  # "YYYY-MM" -> dollars
    next_12m_total: float
    upcoming_ex_dates: list[DividendEvent]  # next 30 days, sorted


def project_dividends(
    portfolio: Portfolio, market: MarketAdapter, today: date | None = None
) -> DividendProjection:
    today = today or date.today()
    horizon = today + timedelta(days=365)
    soon = today + timedelta(days=30)

    monthly: dict[str, float] = defaultdict(float)
    upcoming: list[DividendEvent] = []
    total = 0.0

    shares_by_symbol = {h.symbol: h.shares for h in portfolio.holdings}
    for symbol, shares in shares_by_symbol.items():
        for event in market.upcoming_dividends(symbol, horizon_days=365):
            if event.pay_date > horizon:
                continue
            income = round(shares * event.amount_per_share, 2)
            key = event.pay_date.strftime("%Y-%m")
            monthly[key] += income
            total += income
            if today <= event.ex_date <= soon:
                upcoming.append(event)

    return DividendProjection(
        monthly_income=dict(sorted(monthly.items())),
        next_12m_total=round(total, 2),
        upcoming_ex_dates=sorted(upcoming, key=lambda e: e.ex_date),
    )


def render(projection: DividendProjection) -> str:
    lines = ["## Dividend cashflow", ""]
    lines.append(f"**Next 12 months projected:** ${projection.next_12m_total:,.2f}")
    lines.append("")
    if projection.upcoming_ex_dates:
        lines.append("### Ex-dividend dates in the next 30 days")
        lines.append("")
        lines.append("| Symbol | Ex-date | Pay date | $/share |")
        lines.append("|--------|---------|----------|---------|")
        for e in projection.upcoming_ex_dates:
            lines.append(
                f"| {e.symbol} | {e.ex_date} | {e.pay_date} | ${e.amount_per_share:.2f} |"
            )
        lines.append("")
    if projection.monthly_income:
        lines.append("### Monthly projection")
        lines.append("")
        lines.append("| Month | Income |")
        lines.append("|-------|--------|")
        for month, income in projection.monthly_income.items():
            lines.append(f"| {month} | ${income:,.2f} |")
        lines.append("")
    return "\n".join(lines)
