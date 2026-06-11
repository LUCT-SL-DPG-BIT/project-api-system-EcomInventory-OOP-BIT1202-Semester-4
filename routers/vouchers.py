from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from database import get_db
from auth import require_admin, get_current_active_user
import models, schemas
from utils.email import send_voucher_email

router = APIRouter(prefix="/api/v1/vouchers", tags=["Vouchers"])


# ─────────────────────────────────────────────
# CREATE VOUCHER (Admin only)
# ─────────────────────────────────────────────

@router.post("/", response_model=schemas.VoucherResponse, status_code=201)
def create_voucher(
    payload: schemas.VoucherCreate,
    db: Session = Depends(get_db),
    _: models.User = Depends(require_admin),
):
    code = payload.code.upper().strip()
    if db.query(models.Voucher).filter(models.Voucher.code == code).first():
        raise HTTPException(status_code=400, detail="Voucher code already exists")

    voucher = models.Voucher(
        code=code,
        discount_type=payload.discount_type,
        discount_value=payload.discount_value,
        expiry_date=payload.expiry_date,
        usage_limit=payload.usage_limit,
        is_active=payload.is_active,
    )
    db.add(voucher)
    db.commit()
    db.refresh(voucher)
    return voucher


# ─────────────────────────────────────────────
# LIST VOUCHERS (Admin only)
# ─────────────────────────────────────────────

@router.get("/", response_model=list[schemas.VoucherResponse])
def list_vouchers(
    db: Session = Depends(get_db),
    _: models.User = Depends(require_admin),
):
    return db.query(models.Voucher).order_by(models.Voucher.created_at.desc()).all()


# ─────────────────────────────────────────────
# VALIDATE VOUCHER (Any authenticated user)
# ─────────────────────────────────────────────

@router.get("/{code}/validate")
def validate_voucher(
    code: str,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_active_user),
):
    voucher = db.query(models.Voucher).filter(
        models.Voucher.code == code.upper()
    ).first()

    if not voucher:
        raise HTTPException(status_code=404, detail="Voucher not found")
    if not voucher.is_active:
        raise HTTPException(status_code=400, detail="Voucher is inactive")
    if voucher.expiry_date and voucher.expiry_date.replace(tzinfo=None) < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Voucher has expired")
    if voucher.usage_limit is not None and voucher.times_used >= voucher.usage_limit:
        raise HTTPException(status_code=400, detail="Voucher usage limit reached")

    return {
        "code": voucher.code,
        "discount_type": voucher.discount_type,
        "discount_value": voucher.discount_value,
        "valid": True,
    }


# ─────────────────────────────────────────────
# BROADCAST VOUCHER VIA EMAIL (Admin only)
# Body: {"user_ids": [1,2,3]} or {} for all customers
# ─────────────────────────────────────────────

@router.post("/{code}/broadcast", status_code=202)
def broadcast_voucher(
    code: str,
    payload: schemas.VoucherBroadcast,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    _: models.User = Depends(require_admin),
):
    voucher = db.query(models.Voucher).filter(
        models.Voucher.code == code.upper()
    ).first()
    if not voucher:
        raise HTTPException(status_code=404, detail="Voucher not found")

    if payload.user_ids:
        users = db.query(models.User).filter(models.User.id.in_(payload.user_ids)).all()
    else:
        users = db.query(models.User).filter(
            models.User.is_active == True,
            models.User.role != models.UserRole.admin,
        ).all()

    recipients = [u.email for u in users]
    if not recipients:
        raise HTTPException(status_code=400, detail="No recipients found")

    background_tasks.add_task(
        send_voucher_email,
        voucher.code,
        voucher.discount_type.value,
        voucher.discount_value,
        recipients,
    )

    return {"message": f"Voucher email queued for {len(recipients)} recipient(s)"}


# ─────────────────────────────────────────────
# DEACTIVATE VOUCHER (Admin only)
# ─────────────────────────────────────────────

@router.delete("/{code}", status_code=204)
def deactivate_voucher(
    code: str,
    db: Session = Depends(get_db),
    _: models.User = Depends(require_admin),
):
    voucher = db.query(models.Voucher).filter(
        models.Voucher.code == code.upper()
    ).first()
    if not voucher:
        raise HTTPException(status_code=404, detail="Voucher not found")
    voucher.is_active = False
    db.commit()
