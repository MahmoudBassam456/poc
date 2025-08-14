from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes import data_router
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ← السماح لجميع origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(data_router)
