from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass


@dataclass(frozen=True)
class PostDraft:
    keyword: str
    slug: str
    title: str
    meta_description: str
    outline: list[str]
    body: str
    affiliate_cta: str


def _slugify(text: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return s or "post"


def _angle(keyword: str) -> str:
    h = int(hashlib.sha256(keyword.encode()).hexdigest()[:8], 16) % 5
    return (
        "Best",
        "Honest Review of the",
        "5 Things Nobody Tells You About",
        "How to Choose a",
        "Is It Worth It? The",
    )[h]


def draft_posts(keywords: list[str], affiliate_tag: str = "yourtag-20") -> list[PostDraft]:
    drafts: list[PostDraft] = []
    for kw in keywords:
        kw_clean = kw.strip()
        if not kw_clean:
            continue
        angle = _angle(kw_clean)
        title = f"{angle} {kw_clean.title()} (Updated Guide)"
        meta = (
            f"Hands-on guide to {kw_clean.lower()}: who it's for, how to pick one, "
            f"and what we'd actually buy today."
        )
        outline = [
            f"Who should care about {kw_clean.lower()}",
            "What to look for before buying",
            "Our top pick and why",
            "Runner-up for tighter budgets",
            "Common mistakes to avoid",
            "FAQ",
        ]
        body_parts = [
            f"# {title}",
            "",
            meta,
            "",
        ]
        for section in outline:
            body_parts.append(f"## {section}")
            body_parts.append("")
            body_parts.append(
                f"_Fill this in with 120–180 words about {section.lower()} as it "
                f"relates to {kw_clean.lower()}. Reference a specific product and "
                f"drop an affiliate link with tag `{affiliate_tag}`._"
            )
            body_parts.append("")
        cta = (
            f"> **Our pick:** [Check today's price on the top {kw_clean.lower()}]"
            f"(https://www.amazon.com/dp/EXAMPLE?tag={affiliate_tag})"
        )
        body_parts.append(cta)
        drafts.append(
            PostDraft(
                keyword=kw_clean,
                slug=_slugify(title),
                title=title,
                meta_description=meta,
                outline=outline,
                body="\n".join(body_parts),
                affiliate_cta=cta,
            )
        )
    return drafts


def render(drafts: list[PostDraft]) -> str:
    lines = ["## Affiliate content pipeline", ""]
    if not drafts:
        lines.append("_No keywords supplied. Add a `keywords:` list to your portfolio._")
        lines.append("")
        return "\n".join(lines)
    lines.append(f"Drafted **{len(drafts)}** posts. Slugs written to `./drafts/`.")
    lines.append("")
    lines.append("| Slug | Title |")
    lines.append("|------|-------|")
    for d in drafts:
        lines.append(f"| `{d.slug}.md` | {d.title} |")
    lines.append("")
    return "\n".join(lines)
