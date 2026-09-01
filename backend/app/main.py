from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database.session import Base, engine
from app.models import models  # noqa: F401 ensures models are registered before create_all

from app.api import (
    auth, profile, transactions, goals, loans, insurance, investments,
    literacy, risk, behavior, financial_health, recommendations, notifications, dashboard,
)

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AI-Based Intelligent Financial Advisory System",
    description=(
        "Personalized, explainable financial guidance based on income, expenses, savings, "
        "investments, goals, risk tolerance, and financial literacy. Educational use only — "
        "not professional financial, investment, insurance, tax, or legal advice."
    ),
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"http://(localhost|127\.0\.0\.1):\d+",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api")
app.include_router(profile.router, prefix="/api")
app.include_router(transactions.router, prefix="/api")
app.include_router(goals.router, prefix="/api")
app.include_router(loans.router, prefix="/api")
app.include_router(insurance.router, prefix="/api")
app.include_router(investments.router, prefix="/api")
app.include_router(literacy.router, prefix="/api")
app.include_router(risk.router, prefix="/api")
app.include_router(behavior.router, prefix="/api")
app.include_router(financial_health.router, prefix="/api")
app.include_router(recommendations.router, prefix="/api")
app.include_router(notifications.router, prefix="/api")
app.include_router(dashboard.router, prefix="/api")


@app.get("/api/health")
def health_check():
    return {"status": "ok"}


@app.get("/")
def root():
    return {
        "message": "AI-Based Intelligent Financial Advisory System API",
        "docs": "/docs",
        "disclaimer": (
            "This system provides educational and personalized financial guidance based on the "
            "information provided by the user. It does not constitute professional financial, "
            "investment, insurance, tax, or legal advice."
        ),
    }
