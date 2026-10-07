from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.api.router import api_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    if settings.USE_MYSQL:
        from app.db.connection import verify_db_connection
        verify_db_connection()
    yield

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION,
    description="Citizen-centric government service navigator organized around life events.",
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=False if "*" in settings.CORS_ORIGINS else True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount central API router
app.include_router(api_router)

@app.get("/")
def root():
    return {
        "message": f"Welcome to {settings.PROJECT_NAME}",
        "tagline": settings.TAGLINE,
        "docs": "/docs",
        "health": "/api/v1/health"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host=settings.HOST, port=settings.PORT, reload=True)
