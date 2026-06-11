from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from database import get_db
import models

router = APIRouter(prefix="/api/v1", tags=["Dashboard Stats"])


@router.get("/stats")
def get_dashboard_stats(db: Session = Depends(get_db)):
    total_users = db.query(func.count(models.User.id)).scalar() or 0
    total_products = db.query(func.count(models.Product.id)).scalar() or 0
    total_categories = db.query(func.count(models.Category.id)).scalar() or 0
    total_orders = db.query(func.count(models.Order.id)).scalar() or 0
    total_revenue = db.query(func.sum(models.Order.total_amount)).scalar() or 0.0
    available_products = (
        db.query(func.count(models.Product.id))
        .filter(models.Product.is_available == True)
        .scalar() or 0
    )
    pending_orders = (
        db.query(func.count(models.Order.id))
        .filter(models.Order.status == models.OrderStatus.pending)
        .scalar() or 0
    )

    orders_by_status = {
        s.value: (
            db.query(func.count(models.Order.id))
            .filter(models.Order.status == s)
            .scalar() or 0
        )
        for s in models.OrderStatus
    }

    recent_orders = (
        db.query(models.Order)
        .order_by(models.Order.created_at.desc())
        .limit(5)
        .all()
    )

    return {
        "total_users": total_users,
        "total_products": total_products,
        "total_categories": total_categories,
        "total_orders": total_orders,
        "total_revenue": float(total_revenue),
        "available_products": available_products,
        "pending_orders": pending_orders,
        "orders_by_status": orders_by_status,
        "recent_orders": [
            {
                "id": o.id,
                "status": o.status.value,
                "total_amount": float(o.total_amount),
                "shipping_address": o.shipping_address,
                "created_at": o.created_at.isoformat() if o.created_at else None,
            }
            for o in recent_orders
        ],
    }
