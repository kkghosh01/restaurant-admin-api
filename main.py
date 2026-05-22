from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import init_db
from routes.orders import router as orders_router

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


# ─── Startup ─────────────────────────────────────────
@app.on_event("startup")
def startup():
    init_db()
    print("✅ Admin API ready!")


# ─── Health ──────────────────────────────────────────
@app.get("/")
def root():
    return {"status": "ok", "message": "Restaurant Admin API"}