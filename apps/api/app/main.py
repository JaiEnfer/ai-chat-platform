from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.analytics import router as analytics_router
from app.api.chat import router as chat_router
from app.api.companies import router as companies_router
from app.api.conversation_messages import router as conversation_messages_router
from app.api.health import router as health_router
from app.api.knowledge_items import router as knowledge_items_router
from app.api.leads import router as leads_router
from app.core.config import settings
from app.api.health import build_health_payload


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        version="0.1.0",
    )

    @app.get("/")
    def root() -> dict[str, str]:
        return build_health_payload()

    @app.get("/health")
    def health() -> dict[str, str]:
        return build_health_payload()

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_allowed_origins,
        allow_origin_regex=r"https://.*\.vercel\.app",
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(health_router, prefix=settings.api_prefix, tags=["health"])
    app.include_router(companies_router, prefix=settings.api_prefix, tags=["companies"])
    app.include_router(leads_router, prefix=settings.api_prefix, tags=["leads"])
    app.include_router(
        knowledge_items_router,
        prefix=settings.api_prefix,
        tags=["knowledge-items"],
    )
    app.include_router(chat_router, prefix=settings.api_prefix, tags=["chat"])
    app.include_router(
        conversation_messages_router,
        prefix=settings.api_prefix,
        tags=["conversation-messages"],
    )
    app.include_router(analytics_router, prefix=settings.api_prefix, tags=["analytics"])

    return app


app = create_app()
