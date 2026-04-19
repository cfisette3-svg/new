from __future__ import annotations

from dataclasses import dataclass

from .adapters.rates import CashProduct, RatesAdapter
from .portfolio import Portfolio


@dataclass(frozen=True)
class CashSweepPlan:
    idle_cash: float
    best_product: CashProduct | None
    annual_yield_dollars: float
    ranked: list[CashProduct]


def plan_cash_sweep(portfolio: Portfolio, rates: RatesAdapter) -> CashSweepPlan:
    products = sorted(rates.cash_products(), key=lambda p: p.apy, reverse=True)
    eligible = [p for p in products if portfolio.cash >= p.min_balance]
    best = eligible[0] if eligible else None
    annual = round(portfolio.cash * (best.apy / 100.0), 2) if best else 0.0
    return CashSweepPlan(
        idle_cash=portfolio.cash,
        best_product=best,
        annual_yield_dollars=annual,
        ranked=products,
    )


def render(plan: CashSweepPlan) -> str:
    lines = ["## Idle-cash sweep", ""]
    lines.append(f"**Idle cash:** ${plan.idle_cash:,.2f}")
    if plan.best_product:
        lines.append(
            f"**Best option:** {plan.best_product.name} "
            f"({plan.best_product.kind}) @ {plan.best_product.apy:.2f}% APY → "
            f"**${plan.annual_yield_dollars:,.2f}/yr**"
        )
    else:
        lines.append("_No eligible product for current cash balance._")
    lines.append("")
    lines.append("### Full rate table")
    lines.append("")
    lines.append("| Product | Type | APY | Min | Notes |")
    lines.append("|---------|------|-----|-----|-------|")
    for p in plan.ranked:
        lines.append(
            f"| {p.name} | {p.kind} | {p.apy:.2f}% | ${p.min_balance:,.0f} | {p.notes} |"
        )
    lines.append("")
    return "\n".join(lines)
