from __future__ import annotations

import csv
import json
import logging
import random
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Iterator
from urllib.parse import urljoin

import requests
import yaml
from bs4 import BeautifulSoup

log = logging.getLogger(__name__)

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 "
    "(KHTML, like Gecko) Version/17.0 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
]


@dataclass
class FieldSpec:
    selector: str
    attr: str = "text"
    transform: str | None = None


@dataclass
class Config:
    name: str
    start_urls: list[str]
    item_selector: str
    fields: dict[str, FieldSpec]
    pagination_selector: str | None = None
    max_pages: int = 1
    delay_seconds: float = 0.5
    timeout: int = 20
    retries: int = 3
    rotate_user_agent: bool = True
    output_format: str = "csv"
    output_path: str = "output.csv"

    @classmethod
    def from_yaml(cls, path: Path) -> "Config":
        data = yaml.safe_load(Path(path).read_text())
        fields: dict[str, FieldSpec] = {}
        for k, v in (data.get("fields") or {}).items():
            if isinstance(v, str):
                fields[k] = FieldSpec(selector=v)
            else:
                fields[k] = FieldSpec(**v)
        pagination = data.get("pagination") or {}
        request = data.get("request") or {}
        output = data.get("output") or {}
        return cls(
            name=data["name"],
            start_urls=list(data["start_urls"]),
            item_selector=data["item_selector"],
            fields=fields,
            pagination_selector=pagination.get("next_selector"),
            max_pages=int(pagination.get("max_pages", 1)),
            delay_seconds=float(request.get("delay_seconds", 0.5)),
            timeout=int(request.get("timeout", 20)),
            retries=int(request.get("retries", 3)),
            rotate_user_agent=bool(request.get("rotate_user_agent", True)),
            output_format=output.get("format", "csv"),
            output_path=output.get("path", "output.csv"),
        )


def _fetch(url: str, cfg: Config, session: requests.Session) -> str:
    last_err: Exception | None = None
    for attempt in range(cfg.retries):
        headers: dict[str, str] = {}
        if cfg.rotate_user_agent:
            headers["User-Agent"] = random.choice(USER_AGENTS)
        try:
            r = session.get(url, headers=headers, timeout=cfg.timeout)
            r.raise_for_status()
            return r.text
        except requests.RequestException as e:
            last_err = e
            backoff = (2 ** attempt) + random.random()
            log.warning(
                "fetch failed (%s); retry %d/%d in %.1fs",
                e, attempt + 1, cfg.retries, backoff,
            )
            time.sleep(backoff)
    raise RuntimeError(f"failed to fetch {url}: {last_err}")


def _extract(item, fields: dict[str, FieldSpec]) -> dict[str, Any]:
    row: dict[str, Any] = {}
    for name, spec in fields.items():
        node = item.select_one(spec.selector)
        if node is None:
            row[name] = None
            continue
        if spec.attr == "text":
            value: Any = node.get_text(strip=True)
        else:
            value = node.get(spec.attr)
            if isinstance(value, list):
                value = " ".join(value)
        if spec.transform == "strip" and isinstance(value, str):
            value = value.strip()
        row[name] = value
    return row


def crawl(cfg: Config) -> Iterator[dict[str, Any]]:
    session = requests.Session()
    for start in cfg.start_urls:
        url: str | None = start
        pages = 0
        while url and pages < cfg.max_pages:
            log.info("fetching %s", url)
            html = _fetch(url, cfg, session)
            soup = BeautifulSoup(html, "lxml")
            for item in soup.select(cfg.item_selector):
                yield _extract(item, cfg.fields)
            pages += 1
            if cfg.pagination_selector:
                nxt = soup.select_one(cfg.pagination_selector)
                href = nxt.get("href") if nxt else None
                url = urljoin(url, href) if href else None
            else:
                url = None
            if url:
                time.sleep(cfg.delay_seconds)


def write(records: Iterable[dict[str, Any]], cfg: Config) -> int:
    path = Path(cfg.output_path)
    if path.parent and str(path.parent) not in ("", "."):
        path.parent.mkdir(parents=True, exist_ok=True)
    rows = list(records)

    if cfg.output_format == "csv":
        if not rows:
            path.write_text("")
            return 0
        fieldnames = list(rows[0].keys())
        with path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
        return len(rows)

    if cfg.output_format == "json":
        path.write_text(json.dumps(rows, indent=2, ensure_ascii=False))
        return len(rows)

    raise ValueError(f"unknown output format: {cfg.output_format}")
