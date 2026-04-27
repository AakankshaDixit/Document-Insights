from fastapi import FastAPI
from app.routers import documents, users, health
from app.utils import configure_logging

app = FastAPI(title="Document Insights API (Postgres Version)")
configure_logging()

app.include_router(health.router, tags=["Health"])
app.include_router(documents.router, prefix="/documents", tags=["Documents"])
app.include_router(users.router, prefix="/users", tags=["Users"])