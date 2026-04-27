from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.db import get_db
from app.services.document_service import DocumentService
from app.schemas import DocumentListResponse
from app.models import DocumentStatus

router = APIRouter()

@router.get("/{user_id}/documents", response_model=DocumentListResponse)
async def list_documents(
    user_id: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, le=100),
    status: str | None = None,
    db: AsyncSession = Depends(get_db)
):
    doc_service = DocumentService(db)
    docs, total = await doc_service.list_user_documents(user_id, page, page_size, status)
    return {"documents": docs, "total": total, "page": page, "page_size": page_size}
