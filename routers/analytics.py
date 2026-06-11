from fastapi import APIRouter, Depends
from sqlalchemy import func, desc
from sqlalchemy.orm import Session

from database import get_db
from auth import require_admin
import models, schemas

router = APIRouter(prefix="/api/v1/analytics", tags=["Analytics"])


@router.get("/summary", response_model=schemas.AnalyticsSummary)
def get_analytics_summary(
    db: Session = Depends(get_db),
    _: models.User = Depends(require_admin),
):
    """
    Admin-only endpoint that aggregates live business intelligence data.
    Runs four read-only queries — no data is written or modified.
    """

    # ── 1. Total revenue from delivered orders only ──────────────────────────
    delivered_revenue = (
        db.query(func.sum(models.Order.total_amount))
        .filter(models.Order.status == models.OrderStatus.delivered)
        .scalar()
        or 0.0
    )

    # ── 2. Order count grouped by each status value ──────────────────────────
    orders_by_status = {s.value: 0 for s in models.OrderStatus}
    status_rows = (
        db.query(
            models.Order.status,
            func.count(models.Order.id).label("count"),
        )
        .group_by(models.Order.status)
        .all()
    )
    for row in status_rows:
        orders_by_status[row.status.value] = row.count

    # ── 3. Top 5 products by total units sold ────────────────────────────────
    top_product_rows = (
        db.query(
            models.Product.id.label("product_id"),
            models.Product.name.label("product_name"),
            func.sum(models.OrderItem.quantity).label("total_sold"),
        )
        .join(models.OrderItem, models.OrderItem.product_id == models.Product.id)
        .group_by(models.Product.id, models.Product.name)
        .order_by(desc(func.sum(models.OrderItem.quantity)))
        .limit(5)
        .all()
    )
    top_5_products = [
        schemas.TopProduct(
            product_id=row.product_id,
            product_name=row.product_name,
            total_sold=row.total_sold,
        )
        for row in top_product_rows
    ]

    # ── 4. Revenue by category (quantity × unit_price per order item) ────────
    cat_revenue_rows = (
        db.query(
            models.Category.name.label("category_name"),
            func.sum(
                models.OrderItem.quantity * models.OrderItem.unit_price
            ).label("revenue"),
        )
        .join(models.Product, models.Product.category_id == models.Category.id)
        .join(models.OrderItem, models.OrderItem.product_id == models.Product.id)
        .join(models.Order, models.Order.id == models.OrderItem.order_id)
        .group_by(models.Category.name)
        .order_by(desc(func.sum(models.OrderItem.quantity * models.OrderItem.unit_price)))
        .all()
    )
    revenue_by_category = [
        schemas.CategoryRevenue(
            category_name=row.category_name,
            revenue=float(row.revenue),
        )
        for row in cat_revenue_rows
    ]

    return schemas.AnalyticsSummary(
        delivered_revenue=float(delivered_revenue),
        orders_by_status=orders_by_status,
        top_5_products=top_5_products,
        revenue_by_category=revenue_by_category,
    )
