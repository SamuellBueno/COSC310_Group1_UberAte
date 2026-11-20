# Group 1: UberAte

COSC 310 team term project. A food-delivery backend built with FastAPI,
following a layered architecture (Route → Service → Repository → JSON).

## Requirements
- Python 3.12 or newer (developed and tested with 3.14)

## Setup

### 1. Clone the repository

git clone https://github.com/SamuellBueno/COSC310_Group1_UberAte.git

cd COSC310_Group1_UberAte


### 2. Create and activate a virtual environment
Windows (PowerShell):

py -m venv .venv

or

python -m venv .venv

then

.venv\Scripts\Activate.ps1

macOS / Linux:

python3 -m venv .venv
source .venv/bin/activate

You should see `(.venv)` at the start of your prompt.

### 3. Install dependencies

pip install -r requirements.txt

## Run the application

uvicorn app.main:app --reload




## API endpoints

### Health
| Method | Path | Description |
|---|---|---|
| GET | `/health` | Health check, returns `{"status": "ok"}` |

### Authentication
| Method | Path | Description |
|---|---|---|
| POST | `/auth/register` | Register a new customer account |
| POST | `/auth/login` | Sign in and receive a `session_id` |
| POST | `/auth/logout` | Sign out and end the session |
| GET | `/auth/me` | Get the currently signed-in user |

### Restaurants
| Method | Path | Description |
|---|---|---|
| GET | `/restaurants` | List all restaurants with optional name search, cuisine and open status filtering |
| GET | `/restaurants/{restaurant_id}` | Get a restaurant by ID |
| POST | `/restaurants` | Create a restaurant (restaurant owner or admin only) |
| PATCH | `/restaurants/{restaurant_id}` | Update a restaurant (owner of that restaurant or admin only) |
| GET | `/restaurants/{restaurant_id}/menu-items` | Get all menu items for a specific restaurant |

### Menu Items
| Method | Path | Description |
|---|---|---|
| GET | `/menu-items/{item_id}` | Get a single menu item by ID |
| POST | `/restaurants/{restaurant_id}/menu-items` | Add a menu item to a restaurant (owner or admin only) |
| PATCH | `/menu-items/{item_id}` | Update a menu item (owner of that restaurant or admin only) |
| POST | `/menu-items/{item_id}/deactivate` | Soft-delete a menu item (owner or admin only) |
| DELETE | `/menu-items/{item_id}` | Permanently delete a menu item (owner or admin only) |

### Shopping Cart
| Method | Path | Description |
|---|---|---|
| GET | `/cart` | View the current customer's shopping cart (customers only) |
| POST | `/cart/items` | Add an item to the cart (customers only) |
| PATCH | `/cart/items/{item_id}` | Update the quantity of an item in the cart (customers only) |
| DELETE | `/cart/items/{item_id}` | Remove an item from the cart (customers only) |
| DELETE | `/cart` | Clear the entire cart (customers only) |

### Checkout & Orders
| Method | Path | Description |
|---|---|---|
| POST | `/checkout` | Place an order from the current cart (customers only) |
| GET | `/orders` | List all orders placed by the current customer (customers only) |
| GET | `/orders/{order_id}` | Get the details of a specific order (customers only) |

### Customer Profile
| Method | Path | Description |
|---|---|---|
| GET | `/customers/me` | View the current customer's profile (customers only) |
| PATCH | `/customers/me` | Update the current customer's profile: name, phone, delivery address (customers only) |
| DELETE | `/customers/me` | Close/deactivate the current customer's account (customers only) |

## API documentation
Once the app is running, open **`/docs`** in your browser
(http://127.0.0.1:8000/docs) to see and try out the API.

## Frontend
The application serves a cohesive, responsive frontend under the `/ui` path prefix:

### Authentication & Account
- **Sign In**: [http://127.0.0.1:8000/ui/signin.html](http://127.0.0.1:8000/ui/signin.html) — Register as a customer or sign in with existing credentials.
- **My Account**: [http://127.0.0.1:8000/ui/account.html](http://127.0.0.1:8000/ui/account.html) — View and update your profile (name, phone, delivery address) or close your account.

### Shopping & Ordering
- **Restaurants**: [http://127.0.0.1:8000/ui/index.html](http://127.0.0.1:8000/ui/index.html) — Search and filter restaurants by name, cuisine, and open status.
- **Restaurant Details**: [http://127.0.0.1:8000/ui/restaurant.html](http://127.0.0.1:8000/ui/restaurant.html) — View a restaurant's information and open its menu.
- **Menus**: [http://127.0.0.1:8000/ui/menu.html](http://127.0.0.1:8000/ui/menu.html) — Select a restaurant to browse categorized dishes, prices, descriptions, and availability.
- **Shopping Cart**: [http://127.0.0.1:8000/ui/cart.html](http://127.0.0.1:8000/ui/cart.html) — Review and manage items in your cart, update quantities, and proceed to checkout.
- **Checkout**: [http://127.0.0.1:8000/ui/checkout.html](http://127.0.0.1:8000/ui/checkout.html) — Review order totals and place your order.
- **My Orders**: [http://127.0.0.1:8000/ui/orders.html](http://127.0.0.1:8000/ui/orders.html) — View your order history and details of past orders.

### Restaurant Management
- **Management**: [http://127.0.0.1:8000/ui/manage.html](http://127.0.0.1:8000/ui/manage.html) — Create and update restaurants and menu items (restaurant owners and admin only).

## Data
The seed data lives in `data/`:
- `data/users.json` — Customer, restaurant owner, and admin accounts
- `data/restaurants.json` — Restaurants with names, cuisines, addresses, ratings, and open status
- `data/menu_items.json` — Menu items for each restaurant with names, descriptions, prices, and availability
- `data/sessions.json` — Active user sessions
- `data/carts.json` — Customer shopping carts
- `data/orders.json` — Placed orders with items, totals, and delivery addresses

You can point the app at a different data folder by setting the
`COSC310_DATA_DIR` environment variable. If you don't set it, the app
just uses the repo's own `data/` folder by default.

## Run the tests
With the virtual environment active, from the project root, run:

pytest -v

or 

pytest -q

Tests never touch the real data file. Before each test runs, a fixture
copies the data into a temporary folder (using pytest's `tmp_path`) and
uses `monkeypatch` to point the app at that copy instead of the real one.

## Authentication

Three roles: **customer**, **restaurant_owner** and **admin**. Anyone can register, but only as a customer. Owners and the admin are demo accounts.

| Method | Path | What it does |
|---|---|---|
| POST | `/auth/register` | Creates a customer account |
| POST | `/auth/login` | Returns a `session_id` |
| POST | `/auth/logout` | Ends the session |
| GET | `/auth/me` | Returns the signed in account |

Send the session id on requests that need an account: `Authorization: Bearer <session_id>`.
In `/docs`, sign in with `/auth/login`, copy the `session_id`, and paste it into **Authorize**.

**Demo accounts** (password `Password123!`): `admin@uberate.test` (admin), `owner.sushi@uberate.test` and `owner.pizza@uberate.test` (owners), `alex@uberate.test` and `blake@uberate.test` (customers), `former@uberate.test` (deactivated).

**Where it's enforced:** passwords are hashed in `app/core/security.py`; who is calling and their role are checked in `app/api/role_checks.py`; which restaurant an owner may change is checked in the services.

## Repository structure
```
|- app/
|   |- api/
|   |   |- role_checks.py
|   |   |- routes/
|   |   |   |- authentication.py
|   |   |   |- cart.py
|   |   |   |- checkout.py
|   |   |   |- customers.py
|   |   |   |- health.py
|   |   |   |- menu_items.py
|   |   |   |- orders.py
|   |   |   |- restaurants.py
|   |- core/
|   |   |- config.py
|   |   |- errors.py
|   |   |- security.py
|   |- repositories/
|   |   |- cart_repository.py
|   |   |- json_storage.py
|   |   |- menu_item_repository.py
|   |   |- order_repository.py
|   |   |- restaurant_repository.py
|   |   |- session_repository.py
|   |   |- user_repository.py
|   |- schemas/
|   |   |- cart.py
|   |   |- menu_item.py
|   |   |- order.py
|   |   |- restaurant.py
|   |   |- user.py
|   |- services/
|   |   |- authentication_service.py
|   |   |- cart_service.py
|   |   |- checkout_service.py
|   |   |- customer_service.py
|   |   |- menu_service.py
|   |   |- order_service.py
|   |   |- pricing.py
|   |   |- restaurant_service.py
|   |- main.py
|- data/
|   |- carts.json
|   |- menu_items.json
|   |- orders.json
|   |- restaurants.json
|   |- sessions.json
|   |- users.json
|- docs/
|   |- PROVENANCE.md
|- frontend/
|   |- js/
|   |   |- account-nav.js
|   |   |- account.js
|   |   |- api.js
|   |   |- cart.js
|   |   |- checkout.js
|   |   |- format.js
|   |   |- manage-menu.js
|   |   |- manage-restaurant.js
|   |   |- menu.js
|   |   |- orders.js
|   |   |- restaurant.js
|   |   |- restaurants.js
|   |   |- signin.js
|   |- account.html
|   |- cart.html
|   |- checkout.html
|   |- index.html
|   |- manage.html
|   |- menu.html
|   |- orders.html
|   |- restaurant.html
|   |- signin.html
|   |- styles.css
|- scrum/
|   |- SPRINT-Planning.md
|   |- team-agreement.md
|- tests/
|   |- cart/
|   |   |- test_add_cart_item.py
|   |   |- test_cart_repository.py
|   |- frontend/
|   |   |- test_frontend.py
|   |- menu/
|   |   |- test_menu_add.py
|   |   |- test_menu_browsing.py
|   |   |- test_menu_item_repository.py
|   |   |- test_menu_item_schema.py
|   |   |- test_menu_update.py
|   |- orders/
|   |   |- test_checkout_integration.py
|   |   |- test_checkout_route.py
|   |   |- test_checkout_service.py
|   |   |- test_order_repository.py
|   |   |- test_order_routes.py
|   |   |- test_order_schema.py
|   |- restaurants/
|   |   |- test_restaurant_repository.py
|   |   |- test_restaurant_routes.py
|   |   |- test_restaurant_schema.py
|   |   |- test_restaurant_service.py
|   |- structure/
|   |   |- test_config.py
|   |   |- test_data_integrity.py
|   |   |- test_health.py
|   |   |- test_json_storage.py
|   |- conftest.py
|- .gitignore
|- pytest.ini
|- README.md
|- requirements.txt
```

