from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes.dev import router as dev_router
from app.api.routes.auth import router as auth_router
from app.core.supabase import supabase
from app.api.routes.test_auth import router as test_auth_router
from app.api.routes.reports import router as reports_router
from app.api.routes.upload import router as upload_router

app = FastAPI(
    title="CAMRA API",
    description="Context-Aware Medical Report Analyzer",
    version="0.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "https://camra-frontend.onrender.com"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(auth_router)
app.include_router(dev_router)
app.include_router(test_auth_router)
app.include_router(reports_router)
app.include_router(upload_router)


@app.get("/")
def root():
    return {
        "name": "CAMRA",
        "status": "online",
        "version": "0.1.0"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }


@app.get("/test-db")
def test_database():
    response = (
        supabase
        .table("reports")
        .select("id")
        .limit(1)
        .execute()
    )

    return {
        "database": "connected",
        "data": response.data
    }