from .models import KnowledgeBaseEntry, KnowledgeBaseSection


def load_default_knowledge_bases() -> dict[str, KnowledgeBaseEntry]:
    bytedanabe = KnowledgeBaseEntry(
        id="bytedanabe",
        title="ByteDanabe / ByteDance knowledge base",
        summary="Reference profile for ByteDance company context, product ecosystem, and operating model.",
        aliases=["bytedance", "byte-dance", "tiktok-company"],
        tags=["company", "ecosystem", "short-form-video", "ai", "global-platforms"],
        sections=[
            KnowledgeBaseSection(
                heading="Company overview",
                points=[
                    "ByteDance is a global technology company known for algorithm-driven content platforms.",
                    "Core strengths include recommendation systems, creator tooling, and high-scale media delivery.",
                    "The organization operates multi-product portfolios tailored for regional and global markets.",
                ],
            ),
            KnowledgeBaseSection(
                heading="Major product ecosystem",
                points=[
                    "TikTok serves global short-form entertainment and creator monetization experiences.",
                    "Douyin is the China-market short-video platform with deep local commerce and service integrations.",
                    "CapCut provides creator-first editing workflows across mobile and desktop.",
                    "Lark (Feishu) provides enterprise collaboration for messaging, docs, workflows, and automation.",
                ],
            ),
            KnowledgeBaseSection(
                heading="Business and platform patterns",
                points=[
                    "Personalized feeds are ranked using user interaction signals and content understanding models.",
                    "Monetization blends ads, creator economy, and commerce integrations where permitted.",
                    "Trust-and-safety systems combine automated moderation with human policy review processes.",
                ],
            ),
            KnowledgeBaseSection(
                heading="Engineering and execution themes",
                points=[
                    "Rapid experimentation and KPI-driven iteration are common operating practices.",
                    "Cross-functional ownership links product, data science, moderation, and infrastructure.",
                    "Reliability depends on global-scale distributed systems and observability-heavy operations.",
                ],
            ),
        ],
        references=["https://www.bytedance.com/en/", "https://newsroom.tiktok.com/"],
    )
    lark = KnowledgeBaseEntry(
        id="lark",
        title="Lark knowledge base",
        summary="Reference profile for Lark capabilities, architecture patterns, and enterprise usage scenarios.",
        aliases=["feishu", "larksuite", "lark-suite"],
        tags=["enterprise-collaboration", "docs", "workflow", "automation", "ai-assistant"],
        sections=[
            KnowledgeBaseSection(
                heading="Platform overview",
                points=[
                    "Lark is an enterprise collaboration platform combining chat, meetings, calendar, docs, and workflow tools.",
                    "It is positioned as an all-in-one workplace operating layer for teams of different sizes.",
                    "The platform emphasizes unified identity, searchable collaboration, and connected data workflows.",
                ],
            ),
            KnowledgeBaseSection(
                heading="Core capabilities",
                points=[
                    "Messaging and channels support structured project communication and decision tracking.",
                    "Docs and spreadsheets provide collaborative editing with permissions and embedded workflow context.",
                    "Base and workflow features support no-code/low-code data operations and process automation.",
                    "Meetings and calendar are integrated with shared docs, tasks, and follow-up actions.",
                ],
            ),
            KnowledgeBaseSection(
                heading="Integration and extensibility",
                points=[
                    "Open APIs and bot/app frameworks enable custom internal tools and automation.",
                    "Role-based permissions and admin controls support enterprise governance needs.",
                    "Cross-tool linking allows teams to connect chat threads, docs, approvals, and operational records.",
                ],
            ),
            KnowledgeBaseSection(
                heading="Adoption patterns",
                points=[
                    "Typical rollouts start with communication and docs, then expand into process automation.",
                    "High-value use cases include project operations, incident management, and knowledge management.",
                    "Effective adoption depends on governance conventions, templates, and workflow ownership.",
                ],
            ),
        ],
        references=["https://www.larksuite.com/", "https://open.larksuite.com/"],
    )
    wix = KnowledgeBaseEntry(
        id="wix",
        title="Wix complete knowledge base",
        summary="Comprehensive Wix reference for building, launching, and scaling websites and online businesses.",
        aliases=["wix-com", "wix-studio", "editor-x"],
        tags=["website-builder", "design", "seo", "ecommerce", "cms", "automation"],
        sections=[
            KnowledgeBaseSection(
                heading="Wix platform fundamentals",
                points=[
                    "Wix provides no-code and low-code site building across classic editor, Wix Studio, and developer tooling.",
                    "The platform combines hosting, security, templates, visual editing, and integrated business apps.",
                    "Common workflows include brochure sites, portfolios, service businesses, content sites, and online stores.",
                ],
            ),
            KnowledgeBaseSection(
                heading="Site architecture and planning",
                points=[
                    "Start with clear goals, target audience, and primary conversion actions per page.",
                    "Define information architecture with concise navigation, shallow click depth, and explicit page hierarchy.",
                    "Map required business features early: forms, bookings, memberships, blog, store, and multilingual support.",
                ],
            ),
            KnowledgeBaseSection(
                heading="Design system and content",
                points=[
                    "Use a consistent design system: typography scale, spacing rhythm, reusable sections, and color tokens.",
                    "Prioritize readability and hierarchy with strong headings, scannable blocks, and clear calls to action.",
                    "Build mobile-first layouts and verify breakpoints for tablet and desktop in editor previews.",
                ],
            ),
            KnowledgeBaseSection(
                heading="Wix CMS and dynamic pages",
                points=[
                    "Use Wix CMS collections for structured content such as services, team profiles, FAQs, and case studies.",
                    "Connect repeaters and dynamic pages to collections to reduce duplication and simplify maintenance.",
                    "Define collection fields and validation rules to protect data integrity and editorial consistency.",
                ],
            ),
            KnowledgeBaseSection(
                heading="Business features and monetization",
                points=[
                    "Wix Stores supports catalog setup, variants, pricing rules, discounts, and checkout workflows.",
                    "Bookings, Events, Restaurants, and Memberships support service-led and community-led business models.",
                    "Subscription and recurring service patterns require clear cancellation, billing, and support flows.",
                ],
            ),
            KnowledgeBaseSection(
                heading="SEO, analytics, and growth",
                points=[
                    "Configure page titles, meta descriptions, canonical URLs, structured content, and clean slugs.",
                    "Publish XML sitemap, verify indexing, and monitor crawl issues via search tooling.",
                    "Use analytics dashboards and funnel events to optimize traffic sources, conversion paths, and retention.",
                ],
            ),
            KnowledgeBaseSection(
                heading="Performance, accessibility, and trust",
                points=[
                    "Optimize image sizes, lazy loading usage, font choices, and script footprint for page speed.",
                    "Meet accessibility expectations: semantic structure, alt text, contrast, keyboard reachability, and labels.",
                    "Establish trust with transparent policies, contact methods, social proof, and security disclosures.",
                ],
            ),
            KnowledgeBaseSection(
                heading="Automation, integrations, and operations",
                points=[
                    "Use automations for lead routing, booking confirmations, abandoned carts, and post-purchase follow-ups.",
                    "Integrate CRM, email marketing, payment processors, and external systems where needed.",
                    "Maintain content freshness, test critical journeys monthly, and track uptime and conversion health.",
                ],
            ),
        ],
        references=[
            "https://www.wix.com/",
            "https://www.wix.com/studio",
            "https://support.wix.com/",
        ],
    )
    website_building = KnowledgeBaseEntry(
        id="website-building",
        title="Website building knowledge base",
        summary="End-to-end website building playbook from strategy and UX to launch, measurement, and maintenance.",
        aliases=["web-building", "site-building", "website-guide"],
        tags=["strategy", "ux", "content", "seo", "security", "maintenance", "conversion"],
        sections=[
            KnowledgeBaseSection(
                heading="Strategy and discovery",
                points=[
                    "Define business objectives, audience segments, success metrics, and conversion priorities.",
                    "Audit competitors and adjacent products to identify differentiators and baseline expectations.",
                    "Translate goals into measurable KPIs such as leads, sales, bookings, activation, and retention.",
                ],
            ),
            KnowledgeBaseSection(
                heading="Information architecture and UX",
                points=[
                    "Create clear navigation labels, predictable user flows, and task-oriented page structures.",
                    "Use wireframes to validate hierarchy and interaction patterns before visual polish.",
                    "Design with progressive disclosure to avoid overwhelming users with dense content blocks.",
                ],
            ),
            KnowledgeBaseSection(
                heading="Content system",
                points=[
                    "Build a content model for page types, reusable components, metadata, and governance ownership.",
                    "Write concise, benefit-first copy with explicit calls to action and consistent voice.",
                    "Create media standards for image style, dimensions, compression, and attribution.",
                ],
            ),
            KnowledgeBaseSection(
                heading="Technical foundation",
                points=[
                    "Select platform and architecture based on team skill, scale needs, and integration constraints.",
                    "Ensure responsive design, semantic markup, and cross-browser compatibility on key journeys.",
                    "Establish environment management, backup strategy, and change control before launch.",
                ],
            ),
            KnowledgeBaseSection(
                heading="SEO and discoverability",
                points=[
                    "Optimize on-page elements: titles, descriptions, headings, internal links, and schema where relevant.",
                    "Improve technical SEO with crawlable navigation, canonicalization, sitemap hygiene, and index controls.",
                    "Plan content expansion around search intent clusters and evergreen audience questions.",
                ],
            ),
            KnowledgeBaseSection(
                heading="Performance and reliability",
                points=[
                    "Improve Core Web Vitals by reducing render-blocking resources and optimizing media delivery.",
                    "Monitor availability, latency, and error rates with alerting for customer-impacting incidents.",
                    "Load-test or scenario-test checkout, form submission, and login-critical paths.",
                ],
            ),
            KnowledgeBaseSection(
                heading="Accessibility and compliance",
                points=[
                    "Use accessible color contrast, keyboard navigation, descriptive labels, and logical heading order.",
                    "Provide text alternatives for non-text content and transcripts/captions where applicable.",
                    "Address legal and policy obligations for privacy, cookies, terms, and data handling.",
                ],
            ),
            KnowledgeBaseSection(
                heading="Conversion optimization and experimentation",
                points=[
                    "Instrument funnels and track drop-off points to prioritize UX fixes with highest impact.",
                    "Run structured A/B tests with clear hypotheses and predefined success thresholds.",
                    "Iterate landing pages, offer framing, and trust signals based on evidence rather than intuition.",
                ],
            ),
            KnowledgeBaseSection(
                heading="Post-launch operations",
                points=[
                    "Create a maintenance cadence for content updates, dependency patches, and quality checks.",
                    "Review analytics weekly and align roadmap decisions to measured user behavior.",
                    "Maintain an incident playbook for outages, regressions, and security events.",
                ],
            ),
        ],
        references=[
            "https://web.dev/",
            "https://developer.mozilla.org/",
            "https://www.w3.org/WAI/",
        ],
    )
    shopify = KnowledgeBaseEntry(
        id="shopify",
        title="Shopify complete knowledge base",
        summary="Comprehensive Shopify guide for store setup, growth operations, conversion, and analytics at scale.",
        aliases=["shopify-store", "shopify-plus", "shopify-commerce"],
        tags=["ecommerce", "storefront", "checkout", "retention", "analytics", "operations"],
        sections=[
            KnowledgeBaseSection(
                heading="Platform and store setup",
                points=[
                    "Shopify supports fast launch paths for direct-to-consumer storefronts with integrated payments and hosting.",
                    "Set up core store objects first: products, collections, navigation, policies, and checkout settings.",
                    "Choose a theme that prioritizes speed, conversion clarity, and mobile usability from day one.",
                ],
            ),
            KnowledgeBaseSection(
                heading="Catalog and merchandising",
                points=[
                    "Create standardized product data with clear titles, attributes, variant logic, and media guidelines.",
                    "Use collection architecture to support both discovery browsing and campaign-specific landing pathways.",
                    "Apply pricing, bundles, and promotional logic consistently across product and checkout surfaces.",
                ],
            ),
            KnowledgeBaseSection(
                heading="Checkout, payments, and fulfillment",
                points=[
                    "Reduce checkout friction with streamlined fields, clear shipping expectations, and trusted payment methods.",
                    "Configure tax and shipping profiles carefully to avoid margin leakage and post-purchase support load.",
                    "Align fulfillment SLAs, inventory synchronization, and return workflows with customer communication.",
                ],
            ),
            KnowledgeBaseSection(
                heading="Growth and acquisition",
                points=[
                    "Drive acquisition through channel mix testing across paid social, search, email capture, and affiliates.",
                    "Use campaign-specific landing pages with clear offer framing and consistency from ad-to-product page.",
                    "Measure contribution margin, not just top-line revenue, when scaling paid channels.",
                ],
            ),
            KnowledgeBaseSection(
                heading="Retention and lifecycle",
                points=[
                    "Use segmentation for win-back, post-purchase education, replenishment, and cross-sell automations.",
                    "Improve repeat purchase rates with loyalty mechanisms, bundles, and personalized recommendations.",
                    "Track customer lifetime value by cohort to guide channel spend and merchandising priorities.",
                ],
            ),
            KnowledgeBaseSection(
                heading="Store analytics and experimentation",
                points=[
                    "Track funnel metrics across sessions, add-to-cart, checkout start, purchase completion, and repeat orders.",
                    "Monitor average order value, conversion rate, return rate, and net revenue after discounts and refunds.",
                    "Run controlled experiments on product pages, offers, and checkout UX with clear hypotheses.",
                ],
            ),
            KnowledgeBaseSection(
                heading="Operations and scaling",
                points=[
                    "Document operating playbooks for merchandising, incident response, catalog QA, and launch governance.",
                    "Integrate ERP, CRM, and support tooling while preserving source-of-truth ownership for product data.",
                    "For larger merchants, Shopify Plus capabilities can support advanced B2B and multi-market operations.",
                ],
            ),
        ],
        references=[
            "https://www.shopify.com/",
            "https://help.shopify.com/",
            "https://www.shopify.com/plus",
        ],
    )
    amazon = KnowledgeBaseEntry(
        id="amazon",
        title="Amazon complete knowledge base",
        summary="Comprehensive Amazon commerce guide for marketplace operations, advertising, catalog health, and growth analytics.",
        aliases=["amazon-seller", "amazon-marketplace", "seller-central"],
        tags=["marketplace", "fba", "catalog", "ads", "profitability", "analytics"],
        sections=[
            KnowledgeBaseSection(
                heading="Marketplace foundations",
                points=[
                    "Amazon selling models include third-party marketplace operations with Seller Central account management.",
                    "Winning on Amazon depends on listing quality, price competitiveness, inventory reliability, and service metrics.",
                    "Define a channel strategy that separates marketplace goals from owned-store goals and margin constraints.",
                ],
            ),
            KnowledgeBaseSection(
                heading="Catalog and listing optimization",
                points=[
                    "Build high-quality listings with strong title structure, keyword intent, rich media, and persuasive bullets.",
                    "Maintain variation families and attribute completeness to improve discoverability and conversion performance.",
                    "Track content suppression risks and policy compliance to prevent hidden or inactive detail pages.",
                ],
            ),
            KnowledgeBaseSection(
                heading="Fulfillment and logistics",
                points=[
                    "Evaluate FBA versus seller-fulfilled approaches based on margins, control, and service-level needs.",
                    "Inventory health depends on demand forecasting, reorder points, and aging stock mitigation.",
                    "Operational reliability includes prep standards, inbound planning, and returns triage discipline.",
                ],
            ),
            KnowledgeBaseSection(
                heading="Advertising and demand generation",
                points=[
                    "Use Sponsored Products, Sponsored Brands, and Sponsored Display with portfolio-level budget governance.",
                    "Campaign structure should separate branded, category, and competitor intent for optimization clarity.",
                    "Manage bids and negatives with profitability thresholds rather than click volume alone.",
                ],
            ),
            KnowledgeBaseSection(
                heading="Ranking and Buy Box dynamics",
                points=[
                    "Search rank signals include relevance, conversion velocity, pricing, and listing performance consistency.",
                    "Buy Box outcomes are influenced by price, availability, fulfillment type, and seller performance metrics.",
                    "Sustained rank gains require balancing velocity campaigns with margin protection and stock stability.",
                ],
            ),
            KnowledgeBaseSection(
                heading="Compliance and account health",
                points=[
                    "Monitor account health dashboards for policy warnings, late shipment risks, and return defect trends.",
                    "Maintain defensible documentation for authenticity, product safety, and restricted category requirements.",
                    "Build SOPs for policy incident response and escalation pathways to reduce listing downtime.",
                ],
            ),
            KnowledgeBaseSection(
                heading="Amazon analytics and decisioning",
                points=[
                    "Track sessions, unit session percentage, conversion, TACoS, ACoS, contribution margin, and return burden.",
                    "Use cohort and SKU-level analysis to identify profitable growth versus ad-dependent revenue spikes.",
                    "Integrate ad metrics with organic sales and inventory data for full-funnel optimization decisions.",
                ],
            ),
        ],
        references=[
            "https://sell.amazon.com/",
            "https://sellercentral.amazon.com/",
            "https://advertising.amazon.com/",
        ],
    )
    sales_strategies_analytics = KnowledgeBaseEntry(
        id="sales-strategies-analytics",
        title="Sales strategies and analytics knowledge base",
        summary="End-to-end playbook for revenue strategy, funnel design, experimentation, and analytics-driven growth.",
        aliases=["sales-analytics", "growth-strategy", "revenue-analytics"],
        tags=["sales", "strategy", "analytics", "experimentation", "forecasting", "retention"],
        sections=[
            KnowledgeBaseSection(
                heading="Go-to-market strategy",
                points=[
                    "Clarify target segments, positioning, core offer, and channel fit before scaling acquisition spend.",
                    "Align pricing and packaging to customer value perception and margin requirements.",
                    "Define leading and lagging indicators for each stage of the demand funnel.",
                ],
            ),
            KnowledgeBaseSection(
                heading="Funnel architecture and conversion",
                points=[
                    "Map awareness, consideration, conversion, and retention stages with measurable transition events.",
                    "Identify top drop-off points and prioritize fixes with highest revenue impact per effort.",
                    "Use persuasive proof elements such as testimonials, guarantees, and case studies near decisions.",
                ],
            ),
            KnowledgeBaseSection(
                heading="Sales operations and enablement",
                points=[
                    "Standardize lead qualification criteria and handoff rules between marketing and sales teams.",
                    "Build repeatable playbooks for outreach, objection handling, and deal progression stages.",
                    "Create a closed-loop feedback process from sales conversations back to product and messaging.",
                ],
            ),
            KnowledgeBaseSection(
                heading="Measurement framework",
                points=[
                    "Track CAC, payback period, LTV, conversion rates, average order value, and gross margin by channel.",
                    "Use cohort reporting to separate one-time campaign spikes from durable performance improvements.",
                    "Enforce metric definitions and data governance so teams make decisions from consistent numbers.",
                ],
            ),
            KnowledgeBaseSection(
                heading="Experimentation and optimization",
                points=[
                    "Prioritize tests by expected impact, confidence, and implementation complexity.",
                    "Define hypotheses, success metrics, and stopping criteria before launching experiments.",
                    "Roll out winning experiments with monitoring to catch regressions after scale-up.",
                ],
            ),
            KnowledgeBaseSection(
                heading="Forecasting and planning",
                points=[
                    "Use scenario planning (base, upside, downside) to guide inventory, budget, and staffing decisions.",
                    "Connect demand forecasts to supply and fulfillment capacity to prevent service-level breakdowns.",
                    "Re-forecast on a fixed cadence with variance analysis and corrective actions.",
                ],
            ),
            KnowledgeBaseSection(
                heading="Executive analytics and reporting",
                points=[
                    "Build dashboards by audience: operators need diagnostics; executives need trend and risk visibility.",
                    "Include anomaly detection and contextual notes to reduce misinterpretation of volatile metrics.",
                    "Tie every dashboard to explicit decisions it is intended to support.",
                ],
            ),
        ],
        references=[
            "https://www.shopify.com/enterprise/ecommerce-marketing",
            "https://advertising.amazon.com/library/guides",
            "https://web.dev/case-studies/",
        ],
    )
    return {
        bytedanabe.id: bytedanabe,
        lark.id: lark,
        wix.id: wix,
        website_building.id: website_building,
        shopify.id: shopify,
        amazon.id: amazon,
        sales_strategies_analytics.id: sales_strategies_analytics,
    }
