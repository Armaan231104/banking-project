import logging
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from app.api.routes import auth, users, accounts, transactions
from app.core.config import get_settings
from app.core.logging import configure_logging
from app.db.session import Base, engine
from app.middleware.request_id import RequestIDMiddleware

settings = get_settings()
configure_logging(settings.env)
logger = logging.getLogger(__name__)

app = FastAPI(title=settings.app_name)
app.add_middleware(RequestIDMiddleware)

app.include_router(auth.router, prefix='/api/v1')
app.include_router(users.router, prefix='/api/v1')
app.include_router(accounts.router, prefix='/api/v1')
app.include_router(transactions.router, prefix='/api/v1')


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    logger.exception('Unhandled error path=%s', request.url.path)
    return JSONResponse(status_code=500, content={'detail': 'Internal server error'})


@app.get('/health')
def health():
    return {'status': 'ok'}


Base.metadata.create_all(bind=engine)
