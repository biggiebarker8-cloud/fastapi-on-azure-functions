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
    return {bytedanabe.id: bytedanabe, lark.id: lark}
