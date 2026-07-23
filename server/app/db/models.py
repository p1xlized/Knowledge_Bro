from datetime import datetime, timezone
from enum import Enum
from typing import Optional

from sqlmodel import Field, Relationship, SQLModel


class ContentType(str, Enum):
    ARTICLE = "article"
    VIDEO = "video"


class ContentStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class Tag(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    description: Optional[str] = None
    color: str

    # Relationship pointing to Content
    contents: list["Content"] = Relationship(back_populates="tag")


class Content(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    type: ContentType
    link: str
    title: Optional[str] = None
    ai_summary: Optional[str] = None
    transcript_text: Optional[str] = None
    tts_audio_url: Optional[str] = None
    video_audio_url: Optional[str] = None
    status: ContentStatus = Field(default=ContentStatus.PENDING)
    error_message: Optional[str] = None

    # Seen tracking fields
    is_seen: bool = Field(default=False)
    seen_at: Optional[datetime] = Field(default=None)

    # Date & time when added / updated
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    # Foreign Key & Relationship
    tag_id: Optional[int] = Field(default=None, foreign_key="tag.id")
    tag: Optional["Tag"] = Relationship(back_populates="contents")
