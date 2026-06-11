# E-Commerce Inventory API 🛒

**PROG315 – Object-Oriented Programming 2 | Group D**  
Limkokwing University of Creative Technology, Sierra Leone  
Semester 4 | March – July 2026

---

## 👥 Group Members

| Name | Role |
|------|------|
| Mohamed Barry | Project Lead – Auth, Database & Core Architecture |
| Jaria Bah | Products & Categories Module |
| Abdul Hakeem Gibril Kargbo | Orders Module & Documentation |

---

## 📌 Project Overview

A **FastAPI-based RESTful API** for managing an e-commerce inventory system. This project follows industry-standard practices in API design, authentication, database integration, and open-source collaboration.

### 🌍 SDG Alignment — SDG 8: Decent Work and Economic Growth
This API empowers local Sierra Leonean businesses and traders to digitise their inventory management, process orders, and reach customers online — directly supporting economic growth at the community level.

---

## 🛠️ Tech Stack

| Technology | Purpose |
|------------|---------|
| FastAPI | Web framework |
| PostgreSQL | Relational database |
| SQLAlchemy ORM | Database integration |
| Pydantic v2 | Data validation & schemas |
| OAuth2 + JWT | Authentication & Authorization |
| Passlib (bcrypt) | Password hashing |
| Uvicorn | ASGI server |
| Python-dotenv | Environment variable management |

---

## 📁 Project Structure

```
ecommerce-inventory-api/
│
├── main.py           # App entry point, router registration
├── database.py       # PostgreSQL connection & get_db dependency
├── models.py         # SQLAlchemy ORM models
├── schemas.py        # Pydantic request/response schemas
├── auth.py           # JWT token creation, password hashing, dependencies
├── .env              # Environment variables (masked)
├── requirements.txt  # Python dependencies
├── LICENSE           # MIT License
│
└── routers/
    ├── __init__.py
    ├── users.py      # Auth (register/login) & user management
    ├── categories.py # Category CRUD
    ├── products.py   # Product CRUD with async I/O
    └── orders.py     # Order processing & status management
```

---

## ⚙️ Setup & Installation

### 1. Clone the repository
```bash
git clone https://github.com/<your-org>/ecommerce-inventory-api.git
cd ecommerce-inventory-api
```

### 2. Create a virtual environment
```bash
python -m venv venv
source venv/bin/activate        # Linux/macOS
venv\Scripts\activate           # Windows
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure environment variables
Copy `.env` and fill in your credentials:
```
DATABASE_URL=postgresql://postgres:yourpassword@localhost:5432/ecommerce_db
SECRET_KEY=your-very-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### 5. Create the PostgreSQL database
```sql
CREATE DATABASE ecommerce_db;
```

### 6. Run the application
```bash
uvicorn main:app --reload
```

---

## 📄 API Documentation

Once running, visit:
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

---

## 🔗 API Endpoints

### Auth & Users
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/api/v1/auth/register` | Register new user | Public |
| POST | `/api/v1/auth/login` | Login & get JWT token | Public |
| GET | `/api/v1/users/me` | Get current user profile | Required |
| GET | `/api/v1/users` | Get all users | Admin |
| PATCH | `/api/v1/users/{id}` | Update user | Required |
| DELETE | `/api/v1/users/{id}` | Delete user | Admin |

### Categories
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/api/v1/categories/` | Create category | Admin |
| GET | `/api/v1/categories/` | List all categories | Public |
| GET | `/api/v1/categories/{id}` | Get single category | Public |
| PATCH | `/api/v1/categories/{id}` | Update category | Admin |
| DELETE | `/api/v1/categories/{id}` | Delete category | Admin |

### Products
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/api/v1/products/` | Create product | Admin |
| GET | `/api/v1/products/` | List products (with search & filter) | Public |
| GET | `/api/v1/products/{id}` | Get single product | Public |
| PATCH | `/api/v1/products/{id}` | Update product | Admin |
| DELETE | `/api/v1/products/{id}` | Delete product | Admin |

### Orders
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/api/v1/orders/` | Place new order | Required |
| GET | `/api/v1/orders/` | List orders | Required |
| GET | `/api/v1/orders/{id}` | Get single order | Required |
| PATCH | `/api/v1/orders/{id}/status` | Update order status | Admin |
| DELETE | `/api/v1/orders/{id}` | Delete order | Admin |

---

## 🔐 Security

- Passwords hashed using **bcrypt** via Passlib
- Authentication via **OAuth2 with JWT Bearer tokens**
- Role-based access: `admin` and `customer`
- Sensitive credentials stored in `.env` (never committed to GitHub)

---

## 🤝 Collaboration

This project follows open-source collaborative development:
- All members contribute via **branches and pull requests**
- GitHub Issues used to track tasks per module
- Commits reference the feature/module being worked on

---

## 📜 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.
