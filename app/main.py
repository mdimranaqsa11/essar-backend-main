import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from sqlalchemy import text

from app.api.v1.router import api_router
from app.db.session import engine
from app.utils.response import error

logger = logging.getLogger("uvicorn")


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.connect() as conn:
        await conn.execute(text("SELECT 1"))
    logger.info("Database connection successful.")

    yield

    await engine.dispose()
    logger.info("Database connection closed.")


app = FastAPI(title="Essar Backend", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---- Global error handlers: make EVERY error use the same envelope ----
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(status_code=exc.status_code, content=error(message=exc.detail))


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    # first validation error message, plus the full list in `response` for debugging
    first = exc.errors()[0]
    field = " -> ".join(str(p) for p in first.get("loc", []))
    message = f"Validation error: {field} - {first.get('msg', '')}"
    return JSONResponse(
        status_code=422, content=error(message=message, response=jsonable_encoder(exc.errors()))
    )


@app.get("/health")
async def health():
    return {"status": "ok"}


app.include_router(api_router, prefix="/api")
