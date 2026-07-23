from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Depends, Header, Request
from fastapi.responses import HTMLResponse, Response
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select

from app.db import Content, ContentType, get_session

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

# Resolve app/templates path dynamically relative to this file
BASE_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=BASE_DIR / "templates")


# Helper to return full page vs fragment depending on HTMX request header
def render_list_or_page(
    request: Request, items: list[Content], hx_request: Optional[str]
) -> HTMLResponse:
    template_name = "components/content_list.html" if hx_request else "dashboard.html"
    return templates.TemplateResponse(
        request=request,
        name=template_name,
        context={"items": items},
    )


# 1. Main Dashboard Feed + Dynamic HTMX Filters
@router.get("", response_class=HTMLResponse)
def dashboard_view(
    request: Request,
    is_seen: Optional[bool] = None,
    type: Optional[ContentType] = None,
    date_filter: Optional[str] = None,  # 'today', 'week', 'month'
    tag_id: Optional[int] = None,
    session: Session = Depends(get_session),
    hx_request: Optional[str] = Header(None, alias="HX-Request"),
):
    statement = select(Content)

    # Filter: Read status
    if is_seen is not None:
        statement = statement.where(Content.is_seen == is_seen)

    # Filter: Content type (ARTICLE / VIDEO)
    if type is not None:
        statement = statement.where(Content.type == type)

    # Filter: Tag
    if tag_id is not None:
        statement = statement.where(Content.tag_id == tag_id)

    # Filter: Date range
    now = datetime.now(timezone.utc)
    if date_filter == "today":
        start_of_today = now.replace(hour=0, minute=0, second=0, microsecond=0)
        statement = statement.where(Content.created_at >= start_of_today)
    elif date_filter == "week":
        one_week_ago = now - timedelta(days=7)
        statement = statement.where(Content.created_at >= one_week_ago)
    elif date_filter == "month":
        thirty_days_ago = now - timedelta(days=30)
        statement = statement.where(Content.created_at >= thirty_days_ago)

    # Sorting: Unseen on top, newest first
    statement = statement.order_by(Content.is_seen.asc(), Content.created_at.desc())
    items = session.exec(statement).all()

    return render_list_or_page(request, items, hx_request)


# 2. HTMX Polling Endpoint for Processing Row
@router.get("/row/{content_id}", response_class=HTMLResponse)
def get_content_row(
    request: Request, content_id: int, session: Session = Depends(get_session)
):
    content = session.get(Content, content_id)
    if not content:
        return Response(status_code=404)
    return templates.TemplateResponse(
        request=request,
        name="components/content_row.html",
        context={"item": content},
    )


# 3. Toggle Seen / Unseen Status
@router.patch("/row/{content_id}/toggle-seen", response_class=HTMLResponse)
def toggle_seen(
    request: Request, content_id: int, session: Session = Depends(get_session)
):
    content = session.get(Content, content_id)
    if not content:
        return Response(status_code=404)

    now = datetime.now(timezone.utc)
    content.is_seen = not content.is_seen
    content.seen_at = now if content.is_seen else None
    content.updated_at = now

    session.add(content)
    session.commit()
    session.refresh(content)

    return templates.TemplateResponse(
        request=request,
        name="components/content_row.html",
        context={"item": content},
    )


# 4. Delete Row
@router.delete("/row/{content_id}", response_class=HTMLResponse)
def delete_content_row(content_id: int, session: Session = Depends(get_session)):
    content = session.get(Content, content_id)
    if content:
        session.delete(content)
        session.commit()
    return Response(content="")
