# Upwork / freelance bid template

Paste, then replace anything in `{{ ... }}`. Keep it under 150 words — bids
that read like essays get skipped.

---

Hi {{ first name }},

I build price &amp; stock monitors for e-commerce teams. For
**{{ target site }}** I'd deliver:

- A scraper that pulls **{{ field list, e.g. SKU, title, price, stock, URL }}**
  for every product in **{{ which categories }}**
- **{{ daily / hourly }}** runs to your **{{ S3 / Drive / email / webhook }}**
- A change log so you can see when a SKU's price or stock flipped
- Polite request rate, UA rotation, retries — nothing the site will block

**Timeline:** {{ 2 / 3 }} days from go-ahead.
**Price:** ${{ 250–900 depending on scope }} setup, ${{ 80–200 }}/mo if you want it ongoing.

I've attached a sample CSV from a recent job and a link to my portfolio. Happy
to do a quick paid test run on 1 category before you commit to the full job.

— {{ your name }}

---

## Attachment checklist

- [ ] One sample CSV (~20 rows) with the fields they asked for
- [ ] Link to portfolio page (`portfolio/index.html` hosted on GitHub Pages)
- [ ] One-line note on robots.txt / ToS — shows you checked

## Pricing rules of thumb

| Scope | Setup | Monthly |
|---|---|---|
| One-off, &le;5k items, static HTML | $250 | — |
| Daily, 1 site, &le;1k SKUs | $400 | $80 |
| Daily, 3 sites, &le;5k SKUs | $900 | $200 |
| JS-heavy site (Playwright/Selenium) | +50% | +50% |
| Logged-in / cart-required | quote case-by-case | — |

Refuse: anything behind login that violates ToS, anything personal-data heavy
(PII, scraped LinkedIn, etc.), anything you wouldn't want on the front page of
HN.
