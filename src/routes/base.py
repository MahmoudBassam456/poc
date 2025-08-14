from fastapi import APIRouter, Depends as depends

from helpers.config import get_config, Config

base_router = APIRouter(
    prefix="/api/v1",
    tags=["base"],
   
)
@base_router.get("/")
async def welcome(config:Config =depends(get_config)):
   # config = get_config()
    AppName = config.APP_NAME
    AppVersion = config.APP_VERSION
    return {
       "message": "Welcome to the API New MA!",
       "version": AppName,
         "app_version": AppVersion
    }