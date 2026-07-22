from fastapi import APIRouter, Depends
from sqlmodel import Session, select

from app.db import Tag, get_session

# The prefix '/tags' applies to all routes in this file
router = APIRouter(prefix="/tags", tags=["tags"])


@router.post("/", response_model=Tag)
def create_tag(tag: Tag, session: Session = Depends(get_session)):
    session.add(tag)
    session.commit()
    session.refresh(tag)
    return tag


@router.get("/", response_model=list[Tag])
def read_tags(session: Session = Depends(get_session)):
    return session.exec(select(Tag)).all()
