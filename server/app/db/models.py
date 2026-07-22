from enum import Enum
from typing import Optional

from sqlmodel import Field, Relationship, SQLModel


# 1. Define your Enum
class ContentType(str, Enum):
    VIDEO = "video"
    ARTICLE = "article"
    POST = "post"
    PODCAST = "podcast"
    BOOK = "book"


class Tag(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    description: Optional[str] = None
    color: str

    contents: list["Content"] = Relationship(back_populates="tag")


class Content(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    link: str

    # 2. Use ContentType as the type annotation
    type: ContentType = Field(default=ContentType.ARTICLE)

    tag_id: Optional[int] = Field(default=None, foreign_key="tag.id")
    tag: Optional[Tag] = Relationship(back_populates="contents")
