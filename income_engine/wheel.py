"""Cash-secured put scanner ("wheel" strategy, sell side).

For a configurable watchlist of tickers you'd be happy to own, finds
the weekly put that maximizes annualized premium yield while keeping
the collateral requirement within your available cash.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from .adapters.market import MarketAdapter, OptionQuote
from .portfolio import Portfolio


@dataclass(frozen=True)
class CashSecuredPutIdea:
    symbol: str
    contracts: int
    spot: float
    put: OptionQuote
    premium_dollars: float
    collateral_required: float
    annualized_yield: float
    effective_cost_basis: float  # strike - premium per share


def scan_cash_secured_puts(
    portfolio: Portfolio,
    market: MarketAdapter,
    watchlist: list[str] | None = None,
    today: date | None = None,
) -> list[CashSecuredPutIdea]:
    today = today or date.today()
    # Default watchlist: tickers already held (conviction proxy).
    symbols = watchlist or [h.symbol for h in portfolio.holdings]
    cash_remaining = portfolio.cash
    ideas: list[CashSecuredPutIdea] = []

    candidates: list[CashSecuredPutIdea] = []
    for symbol in symbols:
        spot = market.quote(symbol).price
        for put in market.weekly_puts(symbol, spot):
            if put.bid <= 0:
                continue
            days = max(1, (put.expiration - today).days)
            per_contract_collateral = put.strike * 100
            # single-contract sizing; multi-contract can be layered later.
            premium = put.bid * 100
            annualized = (put.bid / put.strike) * (365.0 / days)
            candidates.append(
                CashSecuredPutIdea(
                    symbol=symbol,
                    contracts=1,
                    spot=spot,
                    put=put,
                    premium_dollars=round(premium, 2),
                    collateral_required=round(per_contract_collateral, 2),
                    annualized_yield=round(annualized, 4),
                    effective_cost_basis=round(put.strike - put.bid, 2),
                )
            )

    # greedy allocator: best yield first, skip if collateral blows the cash budget
    candidates.sort(key=lambda i: i.annualized_yield, reverse=True)
    for idea in candidates:
        if idea.collateral_required > cash_remaining:
            continue
        # one idea per symbol
        if any(existing.symbol == idea.symbol for existing in ideas):
            continue
        ideas.append(idea)
        cash_remaining -= idea.collateral_required

    return ideas


def render(ideas: list[CashSecuredPutIdea]) -> str:
    lines = ["## Cash-secured put ideas (the wheel)", ""]
    if not ideas:
        lines.append("_No puts fit within your cash budget this week._")
        lines.append("")
        return "\n".join(lines)
    lines.append(
        "Sell puts on tickers you'd be happy to own. If assigned, "
        "effective cost basis = strike − premium."
    )
    lines.append("")
    lines.append(
        "| Symbol | Spot | Strike | Exp | Premium | Collateral | Eff. basis | Ann. yield |"
    )
    lines.append(
        "|--------|------|--------|-----|---------|------------|------------|------------|"
    )
    for i in ideas:
        lines.append(
            f"| {i.symbol} | ${i.spot:.2f} | ${i.put.strike:.2f} | "
            f"{i.put.expiration} | ${i.premium_dollars:,.2f} | "
            f"${i.collateral_required:,.2f} | ${i.effective_cost_basis:.2f} | "
            f"{i.annualized_yield * 100:.1f}% |"
        )
    lines.append("")
    return "\n".join(lines)
