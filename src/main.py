from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from routes import data_router
from helpers import get_config

from routes.nlp_rag_respond import nlp_router

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ← السماح لجميع origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
@app.on_event("startup") 
async def start_db():
    settings=get_config()
    app.mongo_con=AsyncIOMotorClient(settings.MONGODB_URI)
    app.mogo_client=app.mongo_con[settings.MONGODB_NAME]
@app.on_event("shutdown")
async def end_db():
    app.mongo_con.close()
app.include_router(data_router)
app.include_router(nlp_router)

