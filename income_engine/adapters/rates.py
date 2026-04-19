from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class CashProduct:
    name: str
    kind: str  # "HYSA" | "MMF" | "T-Bill"
    apy: float
    min_balance: float
    notes: str


class RatesAdapter(Protocol):
    def cash_products(self) -> list[CashProduct]: ...


class SampleRatesAdapter:
    """Stand-in rate table. Replace with a scraper / API in production."""

    def cash_products(self) -> list[CashProduct]:
        return [
            CashProduct("Wealthfront Cash", "HYSA", 4.50, 1, "FDIC, instant transfer"),
            CashProduct("Ally Savings", "HYSA", 4.20, 0, "FDIC, no min"),
            CashProduct("Vanguard VMFXX", "MMF", 5.27, 3000, "Treasury-heavy MMF"),
            CashProduct("Fidelity SPAXX", "MMF", 4.95, 0, "Default core position"),
            CashProduct("4-week T-Bill", "T-Bill", 5.31, 100, "State-tax exempt"),
            CashProduct("13-week T-Bill", "T-Bill", 5.25, 100, "State-tax exempt"),
        ]
