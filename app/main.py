
from app.routes import *
from fastapi import FastAPI

app = FastAPI(
    title="Wave-1-Group-4-Hackathon",
    version="0.0.1",
    description=
    """
    Wave-1-Group-4-Hackathon
    """,
)

app.include_router(file_controller)