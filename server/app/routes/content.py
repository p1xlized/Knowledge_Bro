from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from sqlmodel import Session, SQLModel, select

from app.db import Content, ContentType, get_session
from app.services import process_content_background
from app.utils import fallback_name

router = APIRouter(prefix="/content", tags=["content"])


# --- Request Schemas ---


class ContentCreate(SQLModel):
    link: str
    type: ContentType
    title: Optional[str] = None
    tag_id: Optional[int] = None


# --- Routes ---


# 1. CREATE Content
@router.post("/", response_model=Content, status_code=status.HTTP_201_CREATED)
def create_content(
    payload: ContentCreate,
    background_tasks: BackgroundTasks,
    session: Session = Depends(get_session),
):
    content_title = payload.title or fallback_name(payload.link)

    db_content = Content(
        title=content_title,
        link=payload.link,
        type=payload.type,
        tag_id=payload.tag_id,
    )

    session.add(db_content)
    session.commit()
    session.refresh(db_content)

    # Trigger background pipeline for async processing
    background_tasks.add_task(process_content_background, db_content.id)

    return db_content


# 2. READ ALL Content (Unseen first, then newest first)
@router.get("/", response_model=list[Content])
def read_all_content(
    is_seen: Optional[bool] = None,
    tag_id: Optional[int] = None,
    session: Session = Depends(get_session),
):
    statement = select(Content)

    # Optional query filter for /content?is_seen=false
    if is_seen is not None:
        statement = statement.where(Content.is_seen == is_seen)

    # Optional query filter for /content?tag_id=1
    if tag_id is not None:
        statement = statement.where(Content.tag_id == tag_id)

    # Primary sort: is_seen ASC (False/0 comes before True/1)
    # Secondary sort: created_at DESC (Newest items on top)
    statement = statement.order_by(Content.is_seen.asc(), Content.created_at.desc())

    return session.exec(statement).all()


# 3. READ ONE Content by ID
@router.get("/{content_id}", response_model=Content)
def read_content(content_id: int, session: Session = Depends(get_session)):
    content = session.get(Content, content_id)
    if not content:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Content not found"
        )
    return content


# 4. MARK AS SEEN
@router.patch("/{content_id}/see", response_model=Content)
def mark_as_seen(content_id: int, session: Session = Depends(get_session)):
    content = session.get(Content, content_id)
    if not content:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Content not found"
        )

    now = datetime.now(timezone.utc)
    content.is_seen = True
    content.seen_at = now
    content.updated_at = now

    session.add(content)
    session.commit()
    session.refresh(content)
    return content


# 5. MARK AS UNSEEN
@router.patch("/{content_id}/unsee", response_model=Content)
def mark_as_unseen(content_id: int, session: Session = Depends(get_session)):
    content = session.get(Content, content_id)
    if not content:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Content not found"
        )

    now = datetime.now(timezone.utc)
    content.is_seen = False
    content.seen_at = None
    content.updated_at = now

    session.add(content)
    session.commit()
    session.refresh(content)
    return content


# 6. DELETE Content
@router.delete("/{content_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_content(content_id: int, session: Session = Depends(get_session)):
    content = session.get(Content, content_id)
    if not content:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Content not found"
        )

    session.delete(content)
    session.commit()
    return None
