from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import init_db
from routes.orders import router as orders_router
from routes.payments import router as payments_router
from routes.menu import router as menu_router


app = FastAPI(title="Restaurant Admin API")

# ─── CORS ────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # production-এ React URL দেবে
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Routes ──────────────────────────────────────────
app.include_router(orders_router)
app.include_router(payments_router)
app.include_router(menu_router)


# ─── Startup ─────────────────────────────────────────
@app.on_event("startup")
def startup():
    init_db()
    print("[OK] Admin API ready!")



# ─── Health ──────────────────────────────────────────
@app.get("/")
def root():
    return {"status": "ok", "message": "Restaurant Admin API"}
