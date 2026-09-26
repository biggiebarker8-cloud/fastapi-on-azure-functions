from __future__ import annotations

from collections import defaultdict
from html import escape

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse

from .catalog import filter_products, get_product, summarize_catalog

app = FastAPI(title="Product Hub", version="1.0.0")


def _render_dashboard(products: list[dict], summary: dict, entitlements: list[str]) -> str:
    grouped: dict[str, list[dict]] = defaultdict(list)
    for product in products:
        grouped[product["category"]].append(product)

    cards: list[str] = []
    for category, items in sorted(grouped.items()):
        entries = []
        for item in items:
            status = "Available" if item["accessible"] else f"Requires {item['subscription']}"
            extensions = ", ".join(item["extensions"]) or "None listed"
            tags = ", ".join(item["platforms"])
            use_cases = ", ".join(item["use_cases"])
            entries.append(
                f"""
                <article class="card">
                  <h3>{escape(item["name"])}</h3>
                  <p>{escape(item["description"])}</p>
                  <ul>
                    <li><strong>Vendor:</strong> {escape(item["vendor"])}</li>
                    <li><strong>Platforms:</strong> {escape(tags)}</li>
                    <li><strong>Use cases:</strong> {escape(use_cases)}</li>
                    <li><strong>Extensions:</strong> {escape(extensions)}</li>
                    <li><strong>Status:</strong> {escape(status)}</li>
                    <li><strong>iOS ready:</strong> {"Yes" if item["ios_ready"] else "No"}</li>
                  </ul>
                </article>
                """
            )
        cards.append(f"<section><h2>{escape(category.title())}</h2><div class='grid'>{''.join(entries)}</div></section>")

    active = ", ".join(entitlements) if entitlements else "None"
    return f"""
    <!doctype html>
    <html lang="en">
      <head>
        <meta charset="utf-8">
        <title>Product Hub</title>
        <style>
          body {{ font-family: Arial, sans-serif; margin: 2rem; background: #f5f7fb; color: #1f2937; }}
          .summary {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 1rem; margin-bottom: 2rem; }}
          .tile, .card {{ background: white; border-radius: 12px; padding: 1rem; box-shadow: 0 2px 8px rgba(15, 23, 42, 0.08); }}
          .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 1rem; }}
          ul {{ padding-left: 1.2rem; }}
          code {{ background: #e5e7eb; padding: 0.1rem 0.3rem; border-radius: 4px; }}
        </style>
      </head>
      <body>
        <header>
          <h1>Product Hub</h1>
          <p>One folder view of Microsoft, Apple, Azure, browser, and extension products for iOS-focused and sales-focused workflows.</p>
          <p><strong>Active subscriptions:</strong> {escape(active)}</p>
        </header>
        <section class="summary">
          <div class="tile"><strong>Total products</strong><div>{summary["total_products"]}</div></div>
          <div class="tile"><strong>Accessible now</strong><div>{summary["accessible_products"]}</div></div>
          <div class="tile"><strong>iOS ready</strong><div>{summary["ios_ready_products"]}</div></div>
          <div class="tile"><strong>Sales view tip</strong><div>Use <code>?use_case=sales&amp;platform=iOS</code></div></div>
        </section>
        {''.join(cards)}
      </body>
    </html>
    """


@app.get("/", response_class=HTMLResponse)
def dashboard(
    platform: str | None = None,
    use_case: str | None = None,
    available_only: bool = False,
    entitlement: list[str] = Query(default_factory=list),
):
    products = filter_products(
        platform=platform,
        use_case=use_case,
        available_only=available_only,
        entitlements=entitlement,
    )
    return HTMLResponse(_render_dashboard(products, summarize_catalog(products), entitlement))


@app.get("/api/products")
def list_products(
    platform: str | None = None,
    use_case: str | None = None,
    available_only: bool = False,
    entitlement: list[str] = Query(default_factory=list),
):
    products = filter_products(
        platform=platform,
        use_case=use_case,
        available_only=available_only,
        entitlements=entitlement,
    )
    return {"items": products, "summary": summarize_catalog(products)}


@app.get("/api/products/{product_id}")
def product_detail(product_id: str, entitlement: list[str] = Query(default_factory=list)):
    product = get_product(product_id, entitlement)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found.")
    return product


@app.get("/api/summary")
def catalog_summary(
    platform: str | None = None,
    use_case: str | None = None,
    available_only: bool = False,
    entitlement: list[str] = Query(default_factory=list),
):
    products = filter_products(
        platform=platform,
        use_case=use_case,
        available_only=available_only,
        entitlements=entitlement,
    )
    return summarize_catalog(products)

