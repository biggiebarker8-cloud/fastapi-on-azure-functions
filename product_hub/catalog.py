from __future__ import annotations

from collections import Counter

from pydantic import BaseModel, Field


def _normalize(value: str) -> str:
    return value.strip().lower()


class ProductEntry(BaseModel):
    id: str
    name: str
    vendor: str
    category: str
    description: str
    platforms: list[str] = Field(default_factory=list)
    use_cases: list[str] = Field(default_factory=list)
    subscription: str = "free"
    ios_ready: bool = False
    extensions: list[str] = Field(default_factory=list)


PRODUCT_CATALOG: list[ProductEntry] = [
    ProductEntry(
        id="microsoft-edge-ios",
        name="Microsoft Edge",
        vendor="Microsoft",
        category="browser",
        description="Mobile browser entry point for Microsoft services, saved tabs, and sales demos on iPhone and iPad.",
        platforms=["iOS", "iPadOS", "Web"],
        use_cases=["sales", "browsing", "productivity"],
        subscription="free",
        ios_ready=True,
        extensions=["Collections", "Copilot sidebar", "Password sync"],
    ),
    ProductEntry(
        id="safari-ios",
        name="Safari",
        vendor="Apple",
        category="browser",
        description="Default Apple browser for iOS web experiences and extension-based workflows.",
        platforms=["iOS", "iPadOS", "macOS"],
        use_cases=["sales", "browsing", "demo"],
        subscription="free",
        ios_ready=True,
        extensions=["Safari Web Extensions", "Tab Groups", "Profiles"],
    ),
    ProductEntry(
        id="azure-ai-vision",
        name="Azure AI Vision",
        vendor="Microsoft",
        category="ai",
        description="Vision APIs for image analysis, OCR, and camera-assisted mobile workflows.",
        platforms=["iOS", "Web", "API"],
        use_cases=["sales", "automation", "vision"],
        subscription="azure",
        ios_ready=True,
        extensions=["OCR", "Image tagging", "Spatial analysis"],
    ),
    ProductEntry(
        id="azure-functions",
        name="Azure Functions",
        vendor="Microsoft",
        category="cloud",
        description="Serverless backend for routing product data, automation, and mobile-friendly APIs.",
        platforms=["Cloud", "API"],
        use_cases=["automation", "integration", "sales"],
        subscription="azure",
        ios_ready=False,
        extensions=["HTTP triggers", "ASGI hosting", "Timer jobs"],
    ),
    ProductEntry(
        id="m365-copilot",
        name="Microsoft 365 Copilot",
        vendor="Microsoft",
        category="ai",
        description="Assistant layer across Microsoft 365 apps for summarizing customer notes and preparing follow-ups.",
        platforms=["iOS", "Web", "Windows", "macOS"],
        use_cases=["sales", "productivity", "communication"],
        subscription="microsoft-365-copilot",
        ios_ready=True,
        extensions=["Word", "Outlook", "Teams", "Excel"],
    ),
    ProductEntry(
        id="dynamics-365-sales",
        name="Dynamics 365 Sales",
        vendor="Microsoft",
        category="crm",
        description="CRM workflow for leads, opportunities, and pipeline management aimed at sales teams.",
        platforms=["iOS", "Android", "Web"],
        use_cases=["sales", "crm", "forecasting"],
        subscription="dynamics-365-sales",
        ios_ready=True,
        extensions=["Sales accelerator", "LinkedIn connector", "Pipeline dashboards"],
    ),
    ProductEntry(
        id="power-bi",
        name="Power BI",
        vendor="Microsoft",
        category="analytics",
        description="Mobile dashboards and KPI reporting for showing product performance and account health.",
        platforms=["iOS", "Android", "Web"],
        use_cases=["sales", "analytics", "reporting"],
        subscription="power-bi-pro",
        ios_ready=True,
        extensions=["Scorecards", "Dashboards", "Alerts"],
    ),
    ProductEntry(
        id="microsoft-teams",
        name="Microsoft Teams",
        vendor="Microsoft",
        category="communication",
        description="Meetings, chat, and collaboration space for sharing sales collateral and customer updates.",
        platforms=["iOS", "Android", "Web", "Desktop"],
        use_cases=["sales", "communication", "collaboration"],
        subscription="microsoft-365",
        ios_ready=True,
        extensions=["Meetings", "Channels", "App integrations"],
    ),
    ProductEntry(
        id="onedrive",
        name="OneDrive",
        vendor="Microsoft",
        category="storage",
        description="Shared file access for decks, one-pagers, and product sheets on mobile devices.",
        platforms=["iOS", "Android", "Web", "Desktop"],
        use_cases=["sales", "storage", "productivity"],
        subscription="microsoft-365",
        ios_ready=True,
        extensions=["Camera upload", "Office sync", "Secure sharing"],
    ),
    ProductEntry(
        id="edge-add-ons",
        name="Edge Add-ons",
        vendor="Microsoft",
        category="extensions",
        description="Extension catalog for browser enhancements, research, and workflow shortcuts.",
        platforms=["Web", "Desktop"],
        use_cases=["research", "productivity", "extensions"],
        subscription="free",
        ios_ready=False,
        extensions=["Password managers", "Research tools", "CRM helpers"],
    ),
]


def subscription_accessible(product: ProductEntry, entitlements: list[str] | None = None) -> bool:
    if product.subscription == "free":
        return True
    normalized = {_normalize(item) for item in (entitlements or [])}
    return _normalize(product.subscription) in normalized


def serialize_product(product: ProductEntry, entitlements: list[str] | None = None) -> dict:
    return {
        **product.model_dump(),
        "accessible": subscription_accessible(product, entitlements),
    }


def filter_products(
    *,
    platform: str | None = None,
    use_case: str | None = None,
    available_only: bool = False,
    entitlements: list[str] | None = None,
) -> list[dict]:
    normalized_platform = _normalize(platform) if platform else None
    normalized_use_case = _normalize(use_case) if use_case else None
    items: list[dict] = []
    for product in PRODUCT_CATALOG:
        if normalized_platform and normalized_platform not in {_normalize(item) for item in product.platforms}:
            continue
        if normalized_use_case and normalized_use_case not in {_normalize(item) for item in product.use_cases}:
            continue
        serialized = serialize_product(product, entitlements)
        if available_only and not serialized["accessible"]:
            continue
        items.append(serialized)
    return items


def get_product(product_id: str, entitlements: list[str] | None = None) -> dict | None:
    for product in PRODUCT_CATALOG:
        if product.id == product_id:
            return serialize_product(product, entitlements)
    return None


def summarize_catalog(products: list[dict]) -> dict:
    categories = Counter(item["category"] for item in products)
    accessible = sum(1 for item in products if item["accessible"])
    ios_ready = sum(1 for item in products if item["ios_ready"])
    return {
        "total_products": len(products),
        "accessible_products": accessible,
        "ios_ready_products": ios_ready,
        "categories": dict(sorted(categories.items())),
    }

