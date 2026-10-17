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
| Method | Path | Description |
|---|---|---|
| GET | `/health`     | Health check, returns `{"status": "ok"}`|
| GET | `/restaurants`  | Returns the list of restaurants with optional name search, as well as cuisine and open status filtering|
| GET | `/restaurants/{restaurant_id}`  | Returns a restaurant by ID|
| POST | `/restaurants` | Creates a restaurant|
| PATCH | `/restaurants/{restaurant_id}` | Updates a restaurant with only the fields sent|
| GET | `/restaurants/{restaurant_id}/menu-items` | Returns all menu items for a specific restaurant |
| POST | `/restaurants/{restaurant_id}/menu-items` | Adds a menu item to a restaurant|
| PATCH | `/menu-items/{item_id}` | Updates a menu item with only the fields sent|
| DELETE | `/menu-items/{item_id}` | Deletes a menu item by ID|

## API documentation
Once the app is running, open **`/docs`** in your browser
(http://127.0.0.1:8000/docs) to see and try out the API.

## Frontend
The application serves a cohesive, responsive frontend under the `/ui` path prefix:
- **Restaurants**: [http://127.0.0.1:8000/ui/index.html](http://127.0.0.1:8000/ui/index.html) — Search and filter restaurants, then view restaurant details.
- **Restaurant Details**: [http://127.0.0.1:8000/ui/restaurant.html](http://127.0.0.1:8000/ui/restaurant.html) — View a restaurant's information and open its menu.
- **Menus**: [http://127.0.0.1:8000/ui/menu.html](http://127.0.0.1:8000/ui/menu.html) — Select a restaurant to browse categorized dishes, prices, descriptions, and availability.
- **Management**: [http://127.0.0.1:8000/ui/manage.html](http://127.0.0.1:8000/ui/manage.html) — Create and update restaurants and menu items.

## Data
The seed data lives in:
- `data/restaurants.json`
- `data/menu_items.json`


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

## Repository structure
```
|- app/
|   |- api/
|   |   |- routes/
|   |   |   |- health.py
|   |   |   |- menu_items.py
|   |   |   |- restaurants.py
|   |- core/
|   |   |- config.py
|   |- repositories/
|   |   |- json_storage.py
|   |   |- menu_item_repository.py
|   |   |- restaurant_repository.py
|   |- schemas/
|   |   |- menu_item.py
|   |   |- restaurant.py
|   |- services/
|   |   |- menu_service.py
|   |   |- restaurant_service.py
|   |- main.py
|- data/
|   |- menu_items.json
|   |- restaurants.json
|- docs/
|   |- PROVENANCE.md
|- frontend/
|   |- js/
|   |   |- api.js
|   |   |- manage-restaurant.js
|   |   |- menu.js
|   |- manage.html
|   |- menu.html
|- scrum/
|   |- team-agreement.md
|- tests/
|   |- menu/
|   |   |- test_menu_add.py
|   |   |- test_menu_browsing.py
|   |   |- test_menu_item_repository.py
|   |   |- test_menu_item_schema.py
|   |   |- test_menu_update.py
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