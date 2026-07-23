from .content import router as content_router
from .dashboard import router as dashboard_router
from .tags import router as tags_router

__all__ = ["tags_router", "content_router", "dashboard_router"]
