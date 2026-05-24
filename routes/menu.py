from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import json

from database import get_db, refresh_menu_cache
from models import MenuItem
from schemas import (
    MenuItemResponse,
    UpdatePriceRequest,
    CreateMenuItemRequest,
    UpdateActiveRequest,
)

router = APIRouter(prefix="/menu", tags=["menu"])


# ─── Get All Menu Items ─────────────────────────────
@router.get("/", response_model=list[MenuItemResponse])
def get_menu(db: Session = Depends(get_db)):
    items = db.query(MenuItem).order_by(MenuItem.name).all()
    response_items = []
    for item in items:
        try:
            bangla_list = json.loads(item.bangla) if item.bangla else []
        except Exception:
            bangla_list = []
        try:
            aliases_list = json.loads(item.aliases) if item.aliases else []
        except Exception:
            aliases_list = []

        response_items.append(
            MenuItemResponse(
                id=item.id,
                category=item.category,
                name=item.name,
                bangla=bangla_list,
                aliases=aliases_list,
                price=item.price,
                active=item.active,
            )
        )
    return response_items


# ─── Get Single Menu Item ───────────────────────────
@router.get("/{item_id}", response_model=MenuItemResponse)
def get_menu_item(item_id: int, db: Session = Depends(get_db)):
    item = db.query(MenuItem).filter(MenuItem.id == item_id).first()

    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    try:
        bangla_list = json.loads(item.bangla) if item.bangla else []
    except Exception:
        bangla_list = []
    try:
        aliases_list = json.loads(item.aliases) if item.aliases else []
    except Exception:
        aliases_list = []

    return MenuItemResponse(
        id=item.id,
        category=item.category,
        name=item.name,
        bangla=bangla_list,
        aliases=aliases_list,
        price=item.price,
        active=item.active,
    )


# ─── Add New Menu Item ──────────────────────────────
@router.post("/", response_model=MenuItemResponse)
def create_menu_item(
    payload: CreateMenuItemRequest, db: Session = Depends(get_db)
):
    # Quick duplicate check
    existing = db.query(MenuItem).filter(MenuItem.name == payload.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Item name already exists")

    # Generate search aliases: lowercase name + lowercase bangla keywords
    aliases_list = [payload.name.lower()]
    for tag in payload.bangla:
        cleaned_tag = tag.strip().lower()
        if cleaned_tag and cleaned_tag not in aliases_list:
            aliases_list.append(cleaned_tag)

    item = MenuItem(
        category=payload.category,
        name=payload.name,
        bangla=json.dumps(payload.bangla, ensure_ascii=False),
        aliases=json.dumps(aliases_list, ensure_ascii=False),
        price=payload.price,
        active=payload.active,
    )

    db.add(item)
    db.commit()
    db.refresh(item)

    # ✅ Refresh bot cache
    try:
        refresh_menu_cache()
    except Exception as e:
        print(f"⚠️ Failed to refresh bot cache: {e}")

    return MenuItemResponse(
        id=item.id,
        category=item.category,
        name=item.name,
        bangla=payload.bangla,
        aliases=aliases_list,
        price=item.price,
        active=item.active,
    )


# ─── Update Price ───────────────────────────────────
@router.patch("/{item_id}/price")
def update_price(
    item_id: int,
    payload: UpdatePriceRequest,
    db: Session = Depends(get_db),
):
    item = db.query(MenuItem).filter(MenuItem.id == item_id).first()

    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    # Validation
    if payload.price <= 0:
        raise HTTPException(status_code=400, detail="Invalid price")

    item.price = payload.price
    db.commit()
    db.refresh(item)

    # ✅ Refresh bot cache
    try:
        refresh_menu_cache()
    except Exception as e:
        print(f"⚠️ Failed to refresh bot cache: {e}")

    return {
        "message": "Price updated successfully",
        "id": item.id,
        "item": item.name,
        "new_price": item.price,
    }


# ─── Toggle Active Status (Soft Delete) ─────────────
@router.patch("/{item_id}/active")
def update_active(
    item_id: int,
    payload: UpdateActiveRequest,
    db: Session = Depends(get_db),
):
    item = db.query(MenuItem).filter(MenuItem.id == item_id).first()

    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    if payload.active not in (0, 1):
        raise HTTPException(status_code=400, detail="Active status must be 0 or 1")

    item.active = payload.active
    db.commit()
    db.refresh(item)

    # ✅ Refresh bot cache
    try:
        refresh_menu_cache()
    except Exception as e:
        print(f"⚠️ Failed to refresh bot cache: {e}")

    return {
        "message": "Status updated successfully",
        "id": item.id,
        "item": item.name,
        "active": item.active,
    }
