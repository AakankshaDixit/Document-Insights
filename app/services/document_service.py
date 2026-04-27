from sqlalchemy import select, update, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import noload
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException
import logging
from app.models import Document, DocumentStatus
from typing import Optional, List, Tuple
from uuid import UUID

class DocumentService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_document(self, user_id: str, title: str, content: str, content_hash: str) -> Document:
        try:
            doc = Document(user_id=user_id, title=title, content=content, content_hash=content_hash)
            self.db.add(doc)
            await self.db.commit()
            await self.db.refresh(doc)
            return doc
        except SQLAlchemyError as e:
            await self.db.rollback()
            logging.error(f"Database error in create_document: {e}")
            raise HTTPException(status_code=500, detail="Failed to create document")

    async def create_document_with_summary(self, user_id, title, content, content_hash, summary):
        try:
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
        except SQLAlchemyError as e:
            await self.db.rollback()
            logging.error(f"Database error in create_document_with_summary: {e}")
            raise HTTPException(status_code=500, detail="Failed to create document with summary")

    async def get_document(self, document_id: UUID) -> Optional[Document]:
        try:
            res = await self.db.execute(select(Document).where(Document.id == document_id))
            return res.scalar_one_or_none()
        except SQLAlchemyError as e:
            logging.error(f"Database error in get_document: {e}")
            raise HTTPException(status_code=500, detail="Error fetching document")

    async def list_user_documents(self, user_id: str, page: int, page_size: int, status: Optional[str]) -> Tuple[List[Document], int]:
        try:
            query = select(Document).where(Document.user_id == user_id)
            if status:
                query = query.where(Document.status == status)
            
            # Get count
            count_query = select(func.count()).select_from(query.subquery())
            total = await self.db.scalar(count_query)
            
            # Get data
            res = await self.db.execute(
                query.order_by(Document.created_at.desc())
                .offset((page - 1) * page_size)
                .limit(page_size)
            )
            return res.scalars().all(), total
        except SQLAlchemyError as e:
            logging.error(f"Database error in list_user_documents: {e}")
            raise HTTPException(status_code=500, detail="Error retrieving document list")