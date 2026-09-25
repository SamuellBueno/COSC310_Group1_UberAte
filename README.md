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
| GET | `/health` | Health check, returns `{"status": "ok"}` |

## API documentation
Once the app is running, open **`/docs`** in your browser
(http://127.0.0.1:8000/docs) to see and try out the API.

## Data
The restaurant data lives in `data/restaurants.json`.

You can point the app at a different data folder by setting the
`COSC310_DATA_DIR` environment variable. If you don't set it, the app
just uses the repo's own `data/` folder by default.

## Run the tests
With the virtual environment active, from the project root, run:

pytest -q

Tests never touch the real data file. Before each test runs, a fixture
copies the data into a temporary folder (using pytest's `tmp_path`) and
uses `monkeypatch` to point the app at that copy instead of the real one.

## Repository structure
|- app/
|   |- api/
|   |   |- routes/
|   |   |   |- health.py
|   |   |   |- restaurants.py
|   |- core/
|   |   |- config.py
|   |- repositories/
|   |   |- restaurant_repository.py
|   |- schemas/
|   |   |- restaurant.py
|   |- services/
|   |   |- restaurant_service.py
|   |- main.py
|- data/
|   |- restaurants.json
|- docs/
|   |- PROVENANCE.md
|- scrum/
|   |- team-agreement.md
|- tests/
|   |- test_config.py
|   |- test_health.py
|   |- test_restaurant_repository.py
|   |- test_restaurant_routes.py
|   |- test_restaurant_schema.py
|   |- test_restaurant_service.py
|- .gitignore
|- pytest.ini
|- README.md
|- requirements.txt