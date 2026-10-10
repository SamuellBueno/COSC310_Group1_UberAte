from fastapi import FastAPI
from app.api.routes import health, restaurants, menu_items

from fastapi.staticfiles import StaticFiles

app = FastAPI(title = "UberAte")
app.include_router(health.router)
app.include_router(restaurants.router)
app.include_router(menu_items.router)

app.mount("/ui", StaticFiles(directory="frontend", html=True), name="ui")