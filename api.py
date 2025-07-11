from fastapi import FastAPI

from .db.engine import create_db_and_tables

logicore = FastAPI(
    docs_url="/api/openapi" if DEBUG else None,
    openapi_url="/api/openapi.json" if DEBUG else None
)

origins = [
    'http://localhost:8080',
]

logicore.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)