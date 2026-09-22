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
_To be added: link to `/docs`, once the restaurant endpoint is merged._

## Data
_To be added: location of the data file(s) and how the data directory is
configured, once the repository layer is merged._

## Run the tests
_To be added: the pytest command and what's covered, once the test suite
is in place._

## Repository structure
_To be added: brief tree of the repo layout, once all layers are merged._
