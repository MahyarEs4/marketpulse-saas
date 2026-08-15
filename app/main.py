from fastapi import FastAPI
from app.api.routes.price_snapshots import router as price_snapshots_router
from app.api.routes.competitors import router as competitors_router
from app.api.routes.price_changes import router as price_changes_router
from app.api.routes.auth import router as auth_router

app = FastAPI(title="MarketPulse SaaS")

app.include_router(competitors_router)
app.include_router(price_snapshots_router)
app.include_router(price_changes_router)
app.include_router(auth_router)