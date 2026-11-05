from fastapi import FastAPI
from app.api.routes import health, restaurants, menu_items, authentication
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.core.errors import *

app = FastAPI(title = "UberAte")
app.include_router(health.router)
app.include_router(restaurants.router)
app.include_router(menu_items.router)
app.include_router(authentication.router)

app.mount("/ui", StaticFiles(directory="frontend", html=True), name="ui")

STATUS_FOR_ERROR = {
    NotFoundError: 404,
    ConflictError: 409,
    BusinessRuleError: 400,
    AuthenticationError: 401,
    PermissionDeniedError: 403,
}


@app.exception_handler(DomainError)
async def domain_error_handler(request, exc: DomainError):
    """Convert a domain error into an appropriate standardized error response."""
    return JSONResponse(
        status_code=STATUS_FOR_ERROR.get(type(exc), 400),
        content={"detail": str(exc)},
    )

@app.exception_handler(DataStoreError)
async def data_store_error_handler(request, exc: DataStoreError):
    """Return a safe server error when data storage fails."""
    return JSONResponse(status_code=500, content={"detail": "Data storage error"})