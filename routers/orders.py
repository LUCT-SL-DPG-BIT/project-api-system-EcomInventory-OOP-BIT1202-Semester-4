from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session, joinedload
import os
from datetime import datetime

from database import get_db
import models, schemas
from auth import get_current_active_user, require_admin, require_admin_or_seller
from utils.email import send_email, send_order_confirmation_email, send_seller_order_notification


# ─────────────────────────────────────────────
# BACKGROUND TASK: LOW STOCK EMAIL ALERT
# ─────────────────────────────────────────────

def _send_low_stock_alert(low_stock_items: list[dict]) -> None:
    """
    Runs after the HTTP response is sent (via FastAPI BackgroundTasks).
    Emails the admin about products below the stock threshold.
    """
    admin_email = os.getenv("ADMIN_EMAIL", "")
    threshold   = os.getenv("LOW_STOCK_THRESHOLD", "5")
    if not admin_email or not low_stock_items:
        return

    rows = "".join(
        f"<tr>"
        f"<td style='padding:10px;border:1px solid #ddd'>{item['name']}</td>"
        f"<td style='padding:10px;border:1px solid #ddd;color:#e74c3c'>"
        f"<strong>{item['stock']} units remaining</strong></td>"
        f"</tr>"
        for item in low_stock_items
    )
    subject = f"⚠️ Low Stock Alert — {len(low_stock_items)} product(s) below {threshold} units"
    body = f"""
    <div style="font-family:Inter,sans-serif;max-width:600px;margin:auto">
      <h2 style="color:#e74c3c">⚠️ Low Stock Alert</h2>
      <p>The following products dropped below <strong>{threshold} units</strong>
         after a recent customer order:</p>
      <table style="border-collapse:collapse;width:100%">
        <thead>
          <tr>
            <th style="padding:10px;border:1px solid #ddd;background:#f5f5f5;text-align:left">Product</th>
            <th style="padding:10px;border:1px solid #ddd;background:#f5f5f5;text-align:left">Stock</th>
          </tr>
        </thead>
        <tbody>{rows}</tbody>
      </table>
      <p style="color:#666;margin-top:16px">
        Please restock these items to avoid stockouts.
      </p>
    </div>
    """
    send_email(subject, body, admin_email)

router = APIRouter(prefix="/api/v1/orders", tags=["Orders"])


# ─────────────────────────────────────────────
# CREATE ORDER (Authenticated users)
# ─────────────────────────────────────────────

@router.post("/", response_model=schemas.OrderResponse, status_code=201)
def create_order(
    payload: schemas.OrderCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user),
):
    if not payload.items:
        raise HTTPException(status_code=400, detail="Order must have at least one item")

    total = 0.0
    order_items = []
    products_purchased = []   # collected for low-stock check

    for item in payload.items:
        product = db.query(models.Product).options(
            joinedload(models.Product.seller).joinedload(models.SellerProfile.user)
        ).filter(models.Product.id == item.product_id).first()
        if not product:
            raise HTTPException(status_code=404, detail=f"Product {item.product_id} not found")
        if not product.is_available:
            raise HTTPException(status_code=400, detail=f"Product '{product.name}' is not available")
        if product.stock_quantity < item.quantity:
            raise HTTPException(
                status_code=400,
                detail=f"Insufficient stock for '{product.name}'. Available: {product.stock_quantity}"
            )

        subtotal = product.price * item.quantity
        total += subtotal

        order_items.append(models.OrderItem(
            product_id=product.id,
            quantity=item.quantity,
            unit_price=product.price,
        ))

        # Deduct stock
        product.stock_quantity -= item.quantity
        products_purchased.append(product)

    # ── Voucher validation & discount ────────────────────────────────────────
    discount_amount = 0.0
    applied_voucher_code = None

    if payload.voucher_code:
        code = payload.voucher_code.upper().strip()
        voucher = db.query(models.Voucher).filter(models.Voucher.code == code).first()

        if not voucher:
            raise HTTPException(status_code=404, detail="Voucher code not found")
        if not voucher.is_active:
            raise HTTPException(status_code=400, detail="Voucher is no longer active")
        if voucher.expiry_date and voucher.expiry_date.replace(tzinfo=None) < datetime.utcnow():
            raise HTTPException(status_code=400, detail="Voucher has expired")
        if voucher.usage_limit is not None and voucher.times_used >= voucher.usage_limit:
            raise HTTPException(status_code=400, detail="Voucher usage limit reached")

        if voucher.discount_type == models.DiscountType.percentage:
            discount_amount = total * (voucher.discount_value / 100)
        else:  # flat discount
            discount_amount = min(voucher.discount_value, total)

        total = max(0.0, total - discount_amount)
        voucher.times_used += 1          # atomic within same transaction
        applied_voucher_code = voucher.code

    # ── Save order ────────────────────────────────────────────────────────────
    order = models.Order(
        customer_id=current_user.id,
        shipping_address=payload.shipping_address,
        total_amount=total,
        discount_amount=discount_amount,
        voucher_code=applied_voucher_code,
        items=order_items,
    )

    db.add(order)
    db.commit()
    db.refresh(order)

    # ── Low-stock email ────────────────────────────────────────────────────────
    threshold = int(os.getenv("LOW_STOCK_THRESHOLD", "5"))
    low_stock = [
        {"name": p.name, "stock": p.stock_quantity}
        for p in products_purchased
        if p.stock_quantity < threshold
    ]
    if low_stock:
        background_tasks.add_task(_send_low_stock_alert, low_stock)

    # ── Order confirmation email to customer ──────────────────────────────────
    customer_items = []
    for oi in order_items:
        prod = next((p for p in products_purchased if p.id == oi.product_id), None)
        shop = prod.seller.shop_name if prod and prod.seller else "EcomInventory Pro"
        customer_items.append({
            "name":       prod.name if prod else f"Product #{oi.product_id}",
            "qty":        oi.quantity,
            "unit_price": float(oi.unit_price),
            "shop_name":  shop,
        })
    background_tasks.add_task(
        send_order_confirmation_email,
        current_user.full_name,
        current_user.email,
        order.id,
        customer_items,
        float(order.total_amount),
        float(order.discount_amount or 0),
        applied_voucher_code,
    )

    # ── Seller notification emails (one per unique seller) ────────────────────
    seller_items_map: dict = {}   # seller_profile.id -> {seller, items_list}
    for oi in order_items:
        prod = next((p for p in products_purchased if p.id == oi.product_id), None)
        if prod and prod.seller and prod.seller.user:
            sid = prod.seller.id
            if sid not in seller_items_map:
                seller_items_map[sid] = {"profile": prod.seller, "items": []}
            seller_items_map[sid]["items"].append({
                "name":       prod.name,
                "qty":        oi.quantity,
                "unit_price": float(oi.unit_price),
            })
    for entry in seller_items_map.values():
        profile = entry["profile"]
        background_tasks.add_task(
            send_seller_order_notification,
            profile.user.email,
            profile.shop_name,
            current_user.full_name,
            entry["items"],
            order.id,
        )

    return order


# ─────────────────────────────────────────────
# HELPER: attach customer_name + product_name to an order list
# ─────────────────────────────────────────────

def _enrich_orders(orders: list, db: Session) -> list:
    for o in orders:
        o.customer_name = o.customer.full_name if o.customer else None
        for item in o.items:
            item.product_name = item.product.name if item.product else None
    return orders


# ─────────────────────────────────────────────
# GET ALL ORDERS (Admin all, Seller theirs, Customer own)
# ─────────────────────────────────────────────

@router.get("/", response_model=list[schemas.OrderResponse])
def get_orders(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user),
):
    if current_user.role == models.UserRole.admin:
        orders = db.query(models.Order).options(
            joinedload(models.Order.customer),
            joinedload(models.Order.items).joinedload(models.OrderItem.product),
        ).order_by(models.Order.created_at.desc()).all()
        return _enrich_orders(orders, db)

    if current_user.role == models.UserRole.seller:
        profile = db.query(models.SellerProfile).filter(
            models.SellerProfile.user_id == current_user.id
        ).first()
        if not profile:
            return []
        orders = (
            db.query(models.Order)
            .options(
                joinedload(models.Order.customer),
                joinedload(models.Order.items).joinedload(models.OrderItem.product),
            )
            .join(models.OrderItem, models.Order.id == models.OrderItem.order_id)
            .join(models.Product,   models.OrderItem.product_id == models.Product.id)
            .filter(models.Product.seller_id == profile.id)
            .distinct()
            .order_by(models.Order.created_at.desc())
            .all()
        )
        return _enrich_orders(orders, db)

    # Customer — own orders only
    orders = db.query(models.Order).options(
        joinedload(models.Order.customer),
        joinedload(models.Order.items).joinedload(models.OrderItem.product),
    ).filter(models.Order.customer_id == current_user.id).order_by(models.Order.created_at.desc()).all()
    return _enrich_orders(orders, db)


# ─────────────────────────────────────────────
# GET SINGLE ORDER
# ─────────────────────────────────────────────

@router.get("/{order_id}", response_model=schemas.OrderResponse)
def get_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user),
):
    order = db.query(models.Order).options(
        joinedload(models.Order.customer),
        joinedload(models.Order.items).joinedload(models.OrderItem.product),
    ).filter(models.Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    if current_user.role == models.UserRole.admin:
        return _enrich_orders([order], db)[0]

    if current_user.role == models.UserRole.seller:
        profile = db.query(models.SellerProfile).filter(models.SellerProfile.user_id == current_user.id).first()
        seller_product_ids = {p.id for p in db.query(models.Product).filter(models.Product.seller_id == profile.id).all()} if profile else set()
        order_product_ids  = {i.product_id for i in order.items}
        if not seller_product_ids.intersection(order_product_ids):
            raise HTTPException(status_code=403, detail="Not authorized to view this order")
        return _enrich_orders([order], db)[0]

    if order.customer_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to view this order")
    return _enrich_orders([order], db)[0]


# ─────────────────────────────────────────────
# UPDATE ORDER STATUS (Admin or owning Seller)
# ─────────────────────────────────────────────

@router.patch("/{order_id}/status", response_model=schemas.OrderResponse)
def update_order_status(
    order_id: int,
    payload: schemas.OrderStatusUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_admin_or_seller),
):
    order = db.query(models.Order).options(
        joinedload(models.Order.customer),
        joinedload(models.Order.items).joinedload(models.OrderItem.product),
    ).filter(models.Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    if current_user.role == models.UserRole.seller:
        profile = db.query(models.SellerProfile).filter(models.SellerProfile.user_id == current_user.id).first()
        seller_product_ids = {p.id for p in db.query(models.Product).filter(models.Product.seller_id == profile.id).all()} if profile else set()
        order_product_ids  = {i.product_id for i in order.items}
        if not seller_product_ids.intersection(order_product_ids):
            raise HTTPException(status_code=403, detail="This order does not contain your products")

    order.status = payload.status
    db.commit()
    db.refresh(order)
    return _enrich_orders([order], db)[0]


# ─────────────────────────────────────────────
# DELETE / CANCEL ORDER (Admin only)
# ─────────────────────────────────────────────

@router.delete("/{order_id}", status_code=204)
def delete_order(
    order_id: int,
    db: Session = Depends(get_db),
    _: models.User = Depends(require_admin),
):
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    db.delete(order)
    db.commit()
