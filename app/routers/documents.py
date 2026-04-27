from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis
from app.db import get_db
from app.dependencies import get_redis
from app.schemas import DocumentCreate, DocumentResponse
from app.services.document_service import DocumentService
from app.services.cache_service import CacheService
from app.services.rate_limit_service import RateLimitService
from app.utils import compute_content_hash

router = APIRouter()

@router.post("", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def submit_document(
    doc_in: DocumentCreate,
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis)
):
    content_hash = compute_content_hash(doc_in.content)
    doc_service = DocumentService(db)
    cache = CacheService(redis)
    limiter = RateLimitService(redis)

    cached = await cache.get_cached_summary(content_hash)
    if cached:
        doc = await doc_service.create_document_with_summary(doc_in.user_id, doc_in.title, doc_in.content, content_hash, cached)
        return doc

    count = await limiter.get_active_count(doc_in.user_id)
    if count >= limiter.limit:
        raise HTTPException(status_code=429, detail="Rate limit exceeded")

    await limiter.increment(doc_in.user_id)
    doc = await doc_service.create_document(doc_in.user_id, doc_in.title, doc_in.content, content_hash)
    return doc


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(document_id: str, db: AsyncSession = Depends(get_db)):
    doc_service = DocumentService(db)
    doc = await doc_service.get_document(document_id)
    if not doc:
        raise HTTPException(404, "Not found")
    return doc
