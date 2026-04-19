from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from .adapters.market import MarketAdapter, OptionQuote
from .portfolio import Portfolio


@dataclass(frozen=True)
class CoveredCallIdea:
    symbol: str
    contracts: int
    spot: float
    call: OptionQuote
    premium_dollars: float
    annualized_yield: float  # premium/notional annualized from days-to-exp
    breakeven_if_called: float  # strike + premium
    above_cost_basis: bool


def scan_covered_calls(
    portfolio: Portfolio, market: MarketAdapter, today: date | None = None
) -> list[CoveredCallIdea]:
    today = today or date.today()
    ideas: list[CoveredCallIdea] = []

    for holding in portfolio.holdings:
        contracts = int(holding.shares // 100)
        if contracts == 0:
            continue
        spot = market.quote(holding.symbol).price
        best: CoveredCallIdea | None = None
        for call in market.weekly_calls(holding.symbol, spot):
            days = max(1, (call.expiration - today).days)
            premium = call.bid * 100 * contracts
            notional = call.strike * 100 * contracts
            annualized = (call.bid / call.strike) * (365.0 / days)
            idea = CoveredCallIdea(
                symbol=holding.symbol,
                contracts=contracts,
                spot=spot,
                call=call,
                premium_dollars=round(premium, 2),
                annualized_yield=round(annualized, 4),
                breakeven_if_called=round(call.strike + call.bid, 2),
                above_cost_basis=call.strike > holding.cost_basis,
            )
            if best is None or idea.annualized_yield > best.annualized_yield:
                best = idea
        if best and best.above_cost_basis:
            ideas.append(best)

    ideas.sort(key=lambda i: i.annualized_yield, reverse=True)
    return ideas


def render(ideas: list[CoveredCallIdea]) -> str:
    lines = ["## Covered-call income ideas", ""]
    if not ideas:
        lines.append("_No candidates where the best strike exceeded cost basis._")
        lines.append("")
        return "\n".join(lines)

    lines.append(
        "Sold against shares you already own. Strike > cost basis so assignment "
        "locks in a gain."
    )
    lines.append("")
    lines.append(
        "| Symbol | Contracts | Spot | Strike | Exp | Premium | Ann. yield |"
    )
    lines.append(
        "|--------|-----------|------|--------|-----|---------|------------|"
    )
    for i in ideas:
        lines.append(
            f"| {i.symbol} | {i.contracts} | ${i.spot:.2f} | ${i.call.strike:.2f} | "
            f"{i.call.expiration} | ${i.premium_dollars:,.2f} | "
            f"{i.annualized_yield * 100:.1f}% |"
        )
    lines.append("")
    return "\n".join(lines)
