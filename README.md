# E-Commerce Backend (Django REST Framework)

REST API for a small online store: product catalog, cart, orders, JWT auth, and
race-safe inventory tracking. Runs on SQLite by default; set `DB_ENGINE=mysql` for MySQL.

## Run it
```bash
python -m venv venv && source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt                       # remove mysqlclient if you only use SQLite
python manage.py migrate
python manage.py createsuperuser                      # staff user = can manage products
python manage.py runserver
python manage.py test                                 # 11 tests
```
For MySQL: create the database, copy `.env.example` values into your environment, then run `migrate`.

## Endpoints
| Method | URL | Auth | Purpose |
|---|---|---|---|
| POST | /api/auth/register/ | none | create account |
| POST | /api/auth/token/ | none | get access + refresh JWT |
| POST | /api/auth/token/refresh/ | none | new access token |
| GET | /api/products/?search=&category= | none | browse products |
| POST/PUT/DELETE | /api/products/, /api/categories/ | staff | manage catalog |
| GET/DELETE | /api/cart/ | user | view / empty cart |
| POST | /api/cart/items/ | user | add `{product_id, quantity}` |
| PATCH/DELETE | /api/cart/items/<id>/ | user | change quantity / remove |
| POST | /api/orders/ | user | checkout: needs shipping fields (see below) |
| GET | /api/orders/, /api/orders/<id>/ | user | order history |
| POST | /api/orders/<id>/cancel/ | user | cancel (only while placed/paid) and restore stock |
| PATCH | /api/orders/<id>/status/ | staff | move order: paid -> shipped -> delivered (or cancelled) |
| GET | /api/health/ | none | health check (also tests the DB connection) |
| GET | /api/docs/ | none | interactive Swagger UI (raw schema at /api/schema/) |

**Checkout body:** `ship_name, ship_phone` (10-digit Indian mobile), `ship_address, ship_city, ship_state, ship_pincode` (6 digits).

**Order lifecycle:** `placed -> paid -> shipped -> delivered`. Customers can cancel only from `placed` or `paid`.
Illegal jumps (e.g. placed -> delivered) are rejected by `Order.TRANSITIONS`.

Send the token as `Authorization: Bearer <access_token>`.

## Design notes (know these for your interview)
- **Stateless JWT (SimpleJWT):** no server-side sessions; any server instance can verify a token.
  Access token = 30 min, refresh = 7 days.
- **Inventory consistency:** checkout runs in `transaction.atomic()` and locks product rows with
  `select_for_update()` (ordered by id to avoid deadlocks). Two buyers of the last unit are
  serialized, so overselling is impossible. See `orders/services.py`.
- **Price snapshot:** `OrderItem.unit_price` stores the price at purchase time, so later price
  changes don't rewrite history.
- **Modular apps:** `users`, `catalog`, `cart`, `orders`, each with its own models/serializers/views/urls.
  This is a modular monolith. It is separable into services later, but it is not deployed as microservices.
- **Object-level security:** carts and orders are always filtered by `request.user`, so users get 404 for other people's data.

## Production-style features
- **Order lifecycle + shipping address** copied onto each order at checkout (an address change later doesn't rewrite old orders).
- **Swagger docs** (drf-spectacular) at `/api/docs/`.
- **Rate limiting:** 100/min anonymous, 300/min logged in, and a stricter 30/min on login/register.
- **Logging** of order placed / cancelled / status changes (`LOG_LEVEL` env var).
- **Config via environment variables** (secret key, debug, allowed hosts, database), nothing secret in the code.
- **Docker:** `docker compose up --build` starts MySQL + the API on gunicorn at http://localhost:8000 (WhiteNoise serves static files).
- **CI:** GitHub Actions runs the tests on every push (`.github/workflows/ci.yml`).
- **Health endpoint** for deployment checks.

## Deploying (AWS EC2)
Launch an Ubuntu EC2 instance, install Docker, clone the repo, set real values for `SECRET_KEY`, `ALLOWED_HOSTS`
and the DB password in `docker-compose.yml`, then run `docker compose up -d --build`. Open port 8000 (or put Nginx in front).

## Not built yet (be honest about this in interviews)
Real payment gateway (e.g. Razorpay), product images, email notifications, refunds, reviews, and a caching layer.
