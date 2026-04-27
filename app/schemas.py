from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List
from uuid import UUID

class DocumentCreate(BaseModel):
    user_id: str
    title: str
    content: str

class DocumentResponse(BaseModel):
    document_id: UUID = Field(..., alias="id")
    user_id: str
    title: str
    status: str
    summary: Optional[str]
    error_message: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]

class DocumentListResponse(BaseModel):
    documents: List[DocumentResponse]
    total: int
    page: int
    page_size: int