# scraper

A small, config-driven web scraper for selling **price & stock monitoring**
to e-commerce teams. The package is the demo; the money comes from custom
jobs (see `PROPOSAL_TEMPLATE.md`).

## Install

```sh
pip install -r requirements.txt
```

## Run the demo

Hits [`books.toscrape.com`](http://books.toscrape.com/) — a public site built
explicitly for scraping practice.

```sh
python -m scraper examples/books.yaml -v
```

Writes `out/books.csv` with title, price, rating, stock, and detail URL for
the first 3 pages.

## Adapt to a real site

Copy `examples/price_monitor.yaml`, swap the selectors for ones from your
target site (right-click an item card → Inspect → copy selector), and run:

```sh
python -m scraper examples/price_monitor.yaml --out out/run.csv -v
```

## Config schema

```yaml
name: my_scrape                  # any label
start_urls:                      # one or more entry pages
  - https://example.com/list
item_selector: "div.card"        # repeated element you want one row per
fields:                          # column name -> selector
  title: "a.title"               # short form: text of element
  price:
    selector: "span.price"
  url:
    selector: "a.title"
    attr: href                   # any HTML attribute
  rating:
    selector: "span.stars"
    attr: class                  # class lists are joined with spaces
  stock:
    selector: "p.stock"
    transform: strip             # only "strip" supported for now
pagination:
  next_selector: "a.next"        # optional
  max_pages: 5
request:
  delay_seconds: 1.0             # be polite
  timeout: 20
  retries: 3
  rotate_user_agent: true
output:
  format: csv                    # csv | json
  path: out/run.csv
```

## Layout

```
scraper/                 # the Python package (core + CLI)
examples/books.yaml      # runnable demo against books.toscrape.com
examples/price_monitor.yaml  # template for a real e-commerce job
portfolio/index.html     # single-page portfolio (host on GitHub Pages)
PROPOSAL_TEMPLATE.md     # Upwork bid template
```

## Selling it

1. Host `portfolio/` on GitHub Pages (Settings → Pages → branch root).
2. Search Upwork for "price monitor", "competitor pricing scraper",
   "shopify price tracker". Filter to ≥$250 fixed-price jobs.
3. Bid with `PROPOSAL_TEMPLATE.md`. Attach a sample CSV from a real run
   against the prospect's site (just the first page, ~20 rows — proves you
   can do it).
4. Charge for the test run only if they ask for >1 page.

## Don't

- Scrape anything behind a login that prohibits it in ToS.
- Scrape personal data (LinkedIn profiles, etc.).
- Hit a site faster than ~1 req/sec without permission.
