from __future__ import annotations

from pathlib import Path

import click

from . import cash, content, dividends, notify, options, wheel
from .adapters import SampleMarketAdapter, SampleRatesAdapter
from .adapters.market import MarketAdapter
from .digest import build_digest
from .portfolio import Portfolio


def _market(use_live: bool) -> MarketAdapter:
    if not use_live:
        return SampleMarketAdapter()
    from .adapters.yfinance_adapter import YFinanceMarketAdapter

    return YFinanceMarketAdapter()


def _load(portfolio_path: str) -> Portfolio:
    return Portfolio.load(portfolio_path)


@click.group()
def main() -> None:
    """Weekly passive-income automation."""


@main.command("dividends")
@click.option("--portfolio", "portfolio_path", required=True, type=click.Path(exists=True))
@click.option("--live", is_flag=True, help="Use yfinance instead of sample data")
def cmd_dividends(portfolio_path: str, live: bool) -> None:
    portfolio = _load(portfolio_path)
    projection = dividends.project_dividends(portfolio, _market(live))
    click.echo(dividends.render(projection))


@main.command("options")
@click.option("--portfolio", "portfolio_path", required=True, type=click.Path(exists=True))
@click.option("--live", is_flag=True, help="Use yfinance instead of sample data")
def cmd_options(portfolio_path: str, live: bool) -> None:
    portfolio = _load(portfolio_path)
    ideas = options.scan_covered_calls(portfolio, _market(live))
    click.echo(options.render(ideas))


@main.command("wheel")
@click.option("--portfolio", "portfolio_path", required=True, type=click.Path(exists=True))
@click.option("--live", is_flag=True, help="Use yfinance instead of sample data")
def cmd_wheel(portfolio_path: str, live: bool) -> None:
    portfolio = _load(portfolio_path)
    ideas = wheel.scan_cash_secured_puts(portfolio, _market(live))
    click.echo(wheel.render(ideas))


@main.command("content")
@click.option("--portfolio", "portfolio_path", required=True, type=click.Path(exists=True))
@click.option("--out-dir", default="drafts", type=click.Path())
def cmd_content(portfolio_path: str, out_dir: str) -> None:
    portfolio = _load(portfolio_path)
    drafts = content.draft_posts(list(portfolio.keywords))
    out = Path(out_dir)
    if drafts:
        out.mkdir(parents=True, exist_ok=True)
        for d in drafts:
            (out / f"{d.slug}.md").write_text(d.body)
    click.echo(content.render(drafts))


@main.command("cash")
@click.option("--portfolio", "portfolio_path", required=True, type=click.Path(exists=True))
def cmd_cash(portfolio_path: str) -> None:
    portfolio = _load(portfolio_path)
    plan = cash.plan_cash_sweep(portfolio, SampleRatesAdapter())
    click.echo(cash.render(plan))


@main.command("run")
@click.option("--portfolio", "portfolio_path", required=True, type=click.Path(exists=True))
@click.option("--out", default="digest.md", type=click.Path())
@click.option("--drafts-dir", default="drafts", type=click.Path())
@click.option("--live", is_flag=True, help="Use yfinance instead of sample data")
@click.option(
    "--notify",
    "notify_channels",
    multiple=True,
    type=click.Choice(["email", "slack"]),
    help="Deliver the digest via these channels (repeatable)",
)
def cmd_run(
    portfolio_path: str,
    out: str,
    drafts_dir: str,
    live: bool,
    notify_channels: tuple[str, ...],
) -> None:
    portfolio = _load(portfolio_path)
    digest = build_digest(portfolio, market=_market(live), drafts_dir=Path(drafts_dir))
    Path(out).write_text(digest)
    click.echo(f"Wrote digest to {out}")
    if notify_channels:
        subject = digest.splitlines()[0].lstrip("# ").strip() or "Weekly Income Digest"
        for result in notify.deliver(subject, digest, list(notify_channels)):
            status = "ok" if result.ok else "FAIL"
            click.echo(f"[{result.channel}] {status}: {result.detail}")


if __name__ == "__main__":
    main()
