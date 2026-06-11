"""
app/api/v1/router.py
─────────────────────
Central v1 router — assembles all sub-routers.
Imported once in main.py.
"""
from fastapi import APIRouter

from app.api.v1 import auth, events, tasks, wallet

v1_router = APIRouter()

v1_router.include_router(auth.router)
v1_router.include_router(events.router)
v1_router.include_router(tasks.router)
v1_router.include_router(wallet.router)
