from fastapi import FastAPI ,APIRouter
from dotenv import load_dotenv
import os
load_dotenv(".env")
base_router = APIRouter(
    prefix="/api/v1",
    tags=["base"],
   
)
@base_router.get("/")
def welcome():
    return {
       "message": "Welcome to the API New MA!",
       "version": os.getenv("APP_VERSION")
    }