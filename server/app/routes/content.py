from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.db import Content, get_session

router = APIRouter(prefix="/content", tags=["content"])


# 1. CREATE Content
@router.post("/", response_model=Content, status_code=status.HTTP_201_CREATED)
def create_content(content: Content, session: Session = Depends(get_session)):
    session.add(content)
    session.commit()
    session.refresh(content)
    return content


# 2. READ ALL Content
@router.get("/", response_model=list[Content])
def read_all_content(session: Session = Depends(get_session)):
    return session.exec(select(Content)).all()


# 3. READ ONE Content by ID
@router.get("/{content_id}", response_model=Content)
def read_content(content_id: int, session: Session = Depends(get_session)):
    content = session.get(Content, content_id)
    if not content:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Content not found"
        )
    return content


# 4. UPDATE Content
@router.put("/{content_id}", response_model=Content)
def update_content(
    content_id: int,
    content_update: Content,
    session: Session = Depends(get_session),
):
    db_content = session.get(Content, content_id)
    if not db_content:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Content not found"
        )

    # Copy updated data over the existing record
    content_data = content_update.model_dump(exclude_unset=True)
    for key, value in content_data.items():
        setattr(db_content, key, value)

    session.add(db_content)
    session.commit()
    session.refresh(db_content)
    return db_content


# 5. DELETE Content
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
