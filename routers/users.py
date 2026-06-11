from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta

from database import get_db
import models, schemas
from auth import (
    hash_password,
    verify_password,
    create_access_token,
    get_current_active_user,
    require_admin,
    require_seller,
    ACCESS_TOKEN_EXPIRE_MINUTES,
)
from sqlalchemy.orm import joinedload
from utils.email import send_welcome_email, send_seller_welcome_email

router = APIRouter(prefix="/api/v1", tags=["Auth & Users"])


# ─────────────────────────────────────────────
# REGISTER (Customer)
# ─────────────────────────────────────────────

@router.post("/auth/register", response_model=schemas.UserResponse, status_code=201)
def register_user(
    user: schemas.UserCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    existing = db.query(models.User).filter(models.User.email == user.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    new_user = models.User(
        full_name=user.full_name,
        email=user.email,
        hashed_password=hash_password(user.password),
        role=models.UserRole.customer,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    background_tasks.add_task(send_welcome_email, new_user.full_name, new_user.email)
    return new_user


# ─────────────────────────────────────────────
# REGISTER (Seller) — creates user + seller profile atomically
# ─────────────────────────────────────────────

@router.post("/auth/register/seller", response_model=schemas.UserResponse, status_code=201)
def register_seller(
    payload: schemas.SellerRegister,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    if db.query(models.User).filter(models.User.email == payload.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")

    new_user = models.User(
        full_name=payload.full_name,
        email=payload.email,
        hashed_password=hash_password(payload.password),
        role=models.UserRole.seller,
    )
    db.add(new_user)
    db.flush()  # get new_user.id without committing

    profile = models.SellerProfile(
        user_id=new_user.id,
        shop_name=payload.shop_name,
        bio=payload.bio,
        phone=payload.phone,
        location=payload.location,
        what_you_sell=payload.what_you_sell,
    )
    db.add(profile)
    db.commit()
    db.refresh(new_user)

    background_tasks.add_task(
        send_seller_welcome_email,
        new_user.full_name,
        new_user.email,
        payload.shop_name,
        payload.what_you_sell,
        payload.location,
    )
    return new_user


# ─────────────────────────────────────────────
# GET ALL SELLERS (Admin only)
# ─────────────────────────────────────────────

@router.get("/sellers", response_model=list[schemas.SellerProfileResponse])
def get_all_sellers(
    db: Session = Depends(get_db),
    _: models.User = Depends(require_admin),
):
    return db.query(models.SellerProfile).options(joinedload(models.SellerProfile.user)).all()


# ─────────────────────────────────────────────
# GET MY SELLER PROFILE
# ─────────────────────────────────────────────

@router.get("/sellers/me", response_model=schemas.SellerProfileResponse)
def get_my_seller_profile(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user),
):
    profile = db.query(models.SellerProfile).filter(
        models.SellerProfile.user_id == current_user.id
    ).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Seller profile not found")
    return profile


# ─────────────────────────────────────────────
# LOGIN
# ─────────────────────────────────────────────

@router.post("/auth/login", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(
        data={"sub": user.email},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    return {"access_token": access_token, "token_type": "bearer"}


# ─────────────────────────────────────────────
# GET CURRENT USER PROFILE
# ─────────────────────────────────────────────

@router.get("/users/me", response_model=schemas.UserResponse)
def get_my_profile(current_user: models.User = Depends(get_current_active_user)):
    return current_user


# ─────────────────────────────────────────────
# GET ALL USERS (Admin only)
# ─────────────────────────────────────────────

@router.get("/users", response_model=list[schemas.UserResponse])
def get_all_users(
    db: Session = Depends(get_db),
    _: models.User = Depends(require_admin),
):
    return db.query(models.User).all()


# ─────────────────────────────────────────────
# UPDATE USER
# ─────────────────────────────────────────────

@router.patch("/users/{user_id}", response_model=schemas.UserResponse)
def update_user(
    user_id: int,
    payload: schemas.UserUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user),
):
    if current_user.id != user_id and current_user.role != models.UserRole.admin:
        raise HTTPException(status_code=403, detail="Not authorized")

    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(user, field, value)

    db.commit()
    db.refresh(user)
    return user


# ─────────────────────────────────────────────
# DELETE USER (Admin only)
# ─────────────────────────────────────────────

@router.delete("/users/{user_id}", status_code=204)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    _: models.User = Depends(require_admin),
):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()
