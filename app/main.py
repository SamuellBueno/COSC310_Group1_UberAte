from fastapi import FastAPI
from app.api.routes import health, restaurants

app = FastAPI(title = "UberAte")
app.include_router(health.router)
app.include_router(restaurants.router)