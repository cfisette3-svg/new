from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml


@dataclass(frozen=True)
class Holding:
    symbol: str
    shares: float
    cost_basis: float


@dataclass(frozen=True)
class Portfolio:
    holdings: tuple[Holding, ...]
    cash: float
    keywords: tuple[str, ...]

    @classmethod
    def load(cls, path: str | Path) -> "Portfolio":
        data = yaml.safe_load(Path(path).read_text())
        holdings = tuple(
            Holding(h["symbol"].upper(), float(h["shares"]), float(h["cost_basis"]))
            for h in data.get("holdings", [])
        )
        return cls(
            holdings=holdings,
            cash=float(data.get("cash", 0.0)),
            keywords=tuple(data.get("keywords", [])),
        )
