from fastapi import FastAPI
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware

from app.ml.model_loader import preload_models
from .core.config import settings
from app.db.session import engine, Base
from app.api.v1.endpoints import verify


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 1. Create Tables (If not exist)
    Base.metadata.create_all(bind=engine)
    print("Database tables created.")
    
    # 2. Load Models
    preload_models()
    yield
    print("Shutting down...")

app = FastAPI(
    title=settings.PROJECT_NAME,
    lifespan=lifespan,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# CORS (Allowed for everyone for now, restrict in prod)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# Register Router
app.include_router(verify.router, prefix=settings.API_V1_STR, tags=["Verification"])

@app.get("/health")
def health_check():
    return {
        "status": "active",
        "mode": settings.MODE,
        "database": "connected"
    }

if __name__ == "__main__":

    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)