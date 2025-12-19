from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth, campaigns, templates, smtp, uploads, stats
from app.core.config import settings
from app.core.database import engine, Base

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup - create tables only if they don't exist
    from sqlalchemy import inspect
    async with engine.begin() as conn:
        def create_tables_if_not_exist(sync_conn):
            inspector = inspect(sync_conn)
            existing_tables = inspector.get_table_names()
            if not existing_tables:
                Base.metadata.create_all(sync_conn)
        await conn.run_sync(create_tables_if_not_exist)
    yield
    # Shutdown (if needed)

app = FastAPI(title="NovaMailer API", version="1.0.0", lifespan=lifespan)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_cors_origins(),  # From environment variable
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

app.include_router(auth.router, prefix=f"{settings.API_V1_STR}/auth", tags=["auth"])
app.include_router(campaigns.router, prefix=f"{settings.API_V1_STR}/campaigns", tags=["campaigns"])
app.include_router(templates.router, prefix=f"{settings.API_V1_STR}/templates", tags=["templates"])
app.include_router(smtp.router, prefix=f"{settings.API_V1_STR}/smtp", tags=["smtp"])
app.include_router(uploads.router, prefix=f"{settings.API_V1_STR}/uploads", tags=["uploads"])
app.include_router(stats.router, prefix=f"{settings.API_V1_STR}/stats", tags=["stats"])

@app.get("/")
async def root():
    return {"message": "Welcome to NovaMailer API"}

@app.get("/health")
async def health_check():
    return {"status": "ok"}
