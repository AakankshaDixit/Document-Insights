from sqlalchemy import select, update, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import noload
from app.models import Document, DocumentStatus
from typing import Optional, List, Tuple
from uuid import UUID

class DocumentService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_document(self, user_id: str, title: str, content: str, content_hash: str) -> Document:
        doc = Document(user_id=user_id, title=title, content=content, content_hash=content_hash)
        self.db.add(doc)
        await self.db.commit()
        await self.db.refresh(doc)
        return doc

    async def create_document_with_summary(self, user_id, title, content, content_hash, summary):
        doc = Document(
            user_id=user_id,
            title=title,
            content=content,
            content_hash=content_hash,
            summary=summary,
            status=DocumentStatus.COMPLETED,
        )
        self.db.add(doc)
        await self.db.commit()
        await self.db.refresh(doc)
        return doc

    async def get_document(self, document_id: UUID) -> Optional[Document]:
        res = await self.db.execute(select(Document).where(Document.id == document_id))
        return res.scalar_one_or_none()

    async def list_user_documents(self, user_id: str, page: int, page_size: int, status: Optional[str]) -> Tuple[List[Document], int]:
        query = select(Document).where(Document.user_id == user_id)
        if status:
            query = query.where(Document.status == status)
        total = await self.db.scalar(select(func.count()).select_from(query.subquery()))
        res = await self.db.execute(query.order_by(Document.created_at.desc()).offset((page-1)*page_size).limit(page_size))
        return res.scalars().all(), total