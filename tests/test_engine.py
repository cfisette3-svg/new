from datetime import date
from pathlib import Path

from income_engine.adapters import SampleMarketAdapter, SampleRatesAdapter
from income_engine.cash import plan_cash_sweep
from income_engine.content import draft_posts
from income_engine.digest import build_digest
from income_engine.dividends import project_dividends
from income_engine.notify import deliver
from income_engine.options import scan_covered_calls
from income_engine.portfolio import Portfolio
from income_engine.wheel import scan_cash_secured_puts


FIXED = date(2026, 4, 19)


def _portfolio(tmp_path: Path) -> Portfolio:
    p = tmp_path / "p.yaml"
    p.write_text(
        """
cash: 10000
holdings:
  - {symbol: AAPL, shares: 150, cost_basis: 120}
  - {symbol: MSFT, shares: 100, cost_basis: 200}
  - {symbol: T,    shares: 50,  cost_basis: 18}
keywords:
  - best mechanical keyboard
""".strip()
    )
    return Portfolio.load(p)


def test_dividend_projection_is_deterministic_and_positive(tmp_path):
    portfolio = _portfolio(tmp_path)
    market = SampleMarketAdapter(today=FIXED)
    proj = project_dividends(portfolio, market, today=FIXED)
    assert proj.next_12m_total > 0
    assert all(income > 0 for income in proj.monthly_income.values())
    proj2 = project_dividends(portfolio, market, today=FIXED)
    assert proj.next_12m_total == proj2.next_12m_total


def test_covered_calls_respect_cost_basis(tmp_path):
    portfolio = _portfolio(tmp_path)
    market = SampleMarketAdapter(today=FIXED)
    ideas = scan_covered_calls(portfolio, market, today=FIXED)
    for idea in ideas:
        assert idea.call.strike > next(
            h.cost_basis for h in portfolio.holdings if h.symbol == idea.symbol
        )
        assert idea.contracts >= 1


def test_cash_sweep_picks_highest_eligible_apy(tmp_path):
    portfolio = _portfolio(tmp_path)
    plan = plan_cash_sweep(portfolio, SampleRatesAdapter())
    assert plan.best_product is not None
    assert plan.annual_yield_dollars > 0
    apys = [p.apy for p in plan.ranked if portfolio.cash >= p.min_balance]
    assert plan.best_product.apy == max(apys)


def test_content_drafts_are_generated(tmp_path):
    portfolio = _portfolio(tmp_path)
    drafts = draft_posts(list(portfolio.keywords))
    assert len(drafts) == 1
    assert "mechanical keyboard" in drafts[0].title.lower()
    assert drafts[0].slug
    assert drafts[0].affiliate_cta.startswith("> ")


def test_digest_contains_all_sections(tmp_path):
    portfolio = _portfolio(tmp_path)
    digest = build_digest(portfolio, drafts_dir=tmp_path / "drafts", today=FIXED)
    for heading in (
        "Weekly Income Digest",
        "Dividend cashflow",
        "Covered-call income ideas",
        "Cash-secured put ideas",
        "Idle-cash sweep",
        "Affiliate content pipeline",
    ):
        assert heading in digest
    assert (tmp_path / "drafts").exists()


def test_cash_secured_puts_respect_cash_budget(tmp_path):
    portfolio = _portfolio(tmp_path)
    ideas = scan_cash_secured_puts(portfolio, SampleMarketAdapter(today=FIXED), today=FIXED)
    total_collateral = sum(i.collateral_required for i in ideas)
    assert total_collateral <= portfolio.cash
    # one idea per symbol max
    assert len({i.symbol for i in ideas}) == len(ideas)
    for i in ideas:
        assert i.put.bid > 0
        assert i.effective_cost_basis == round(i.put.strike - i.put.bid, 2)


def test_notify_fails_loudly_without_config(monkeypatch):
    for key in (
        "INCOME_SMTP_HOST",
        "INCOME_EMAIL_TO",
        "INCOME_SLACK_WEBHOOK",
    ):
        monkeypatch.delenv(key, raising=False)
    results = deliver("subj", "body", ["email", "slack"])
    assert {r.channel for r in results} == {"email", "slack"}
    assert all(not r.ok for r in results)
