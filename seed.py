"""
seed.py — Run this ONCE to set up your database and create default accounts.

Usage:
  python seed.py

What it does:
  1. Creates all database tables (safe to run multiple times).
  2. Adds any missing columns to existing tables (discount_amount, voucher_code).
  3. Creates a default Admin account.
  4. Creates a default Customer account.

Default accounts created:
  Admin    — admin@example.com       / admin1234
  Customer — customer@example.com   / customer1234
"""
import sys
from sqlalchemy import text
from dotenv import load_dotenv

load_dotenv()

from database import engine, Base, SessionLocal
import models
from auth import hash_password


def run_migrations():
    """Add missing columns to existing tables without dropping data."""
    with engine.connect() as conn:
        migrations = [
            "ALTER TABLE orders ADD COLUMN IF NOT EXISTS discount_amount FLOAT DEFAULT 0",
            "ALTER TABLE orders ADD COLUMN IF NOT EXISTS voucher_code VARCHAR(50)",
        ]
        success = 0
        for sql in migrations:
            try:
                conn.execute(text(sql))
                conn.commit()
                success += 1
            except Exception:
                conn.rollback()
        if success:
            print(f"  DB migration: applied {success} column addition(s) to orders table")


def create_tables():
    """Create all tables. Skips tables that already exist."""
    Base.metadata.create_all(bind=engine)
    print("  All DB tables are ready")


def seed_users():
    db = SessionLocal()
    try:
        accounts = [
            {
                "full_name": "System Admin",
                "email": "admin@example.com",
                "password": "admin1234",
                "role": models.UserRole.admin,
            },
            {
                "full_name": "Demo Customer",
                "email": "customer@example.com",
                "password": "customer1234",
                "role": models.UserRole.customer,
            },
        ]

        for acc in accounts:
            existing = db.query(models.User).filter(models.User.email == acc["email"]).first()
            if not existing:
                db.add(models.User(
                    full_name=acc["full_name"],
                    email=acc["email"],
                    hashed_password=hash_password(acc["password"]),
                    role=acc["role"],
                    is_active=True,
                ))
                label = "Admin   " if acc["role"] == models.UserRole.admin else "Customer"
                print(f"  Created {label}: {acc['email']}  /  {acc['password']}")
            else:
                label = "Admin   " if acc["role"] == models.UserRole.admin else "Customer"
                print(f"  Already exists ({label}): {acc['email']}")

        db.commit()
    except Exception as e:
        db.rollback()
        print(f"  ERROR creating users: {e}")
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    print()
    print("=" * 50)
    print("  EcomInventory Pro — Database Seeder")
    print("=" * 50)
    print()

    run_migrations()
    create_tables()
    seed_users()

    print()
    print("  Done! Start the server:")
    print("    uvicorn main:app --reload")
    print()
    print("  Then open:")
    print("    http://localhost:8000         Dashboard")
    print("    http://localhost:8000/docs    Swagger UI")
    print()
