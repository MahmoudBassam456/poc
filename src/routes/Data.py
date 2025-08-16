from fastapi import APIRouter, Depends, UploadFile, File, status
from fastapi.responses import JSONResponse
import os
import aiofiles
import logging
from helpers import get_config, Config
from controllers import DataController, ProjectController
from models import ResponseSignalsFile

logger = logging.getLogger("uvicorn.error")
data_router = APIRouter(prefix="/api/v1/upload", tags=["upload"])

@data_router.post("/data/{file_id}")
async def upload_file(
    file_id: str,
    file: UploadFile ,
    config: Config = Depends(get_config)
):
    # Validate file
    is_valid, state = DataController().validate_config(file=file)
    if not is_valid:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message": state}
        )
          
        

    # Get project controller and paths
    
    file_target_base = ProjectController().get_project_path(file_id=file_id)

    # Ensure directory exists
    if not os.path.exists(file_target_base):
     os.makedirs(file_target_base)

    # Full path to save file
    file_target_fullpath = DataController().clean_filename_build(files_path=file_target_base, file=file)

    # Read entire file into memory (no chunks)
    #content = await file.read()  # ← Entire file read at once

    # Write entire content in one async write
    try:
        async with aiofiles.open(file_target_fullpath, "wb") as f:
            while chunk := await file.read(config.FILE_SIZE_CHUNK):
                await f.write(chunk)
           
    except Exception as e:
        logger.error(f"Failed to save file {file.filename}: {str(e)}")
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message": ResponseSignalsFile.Upload_Failure.value}
        )

    # Optional: Close the uploaded file (good practice)
    await file.close()

    return {
        "is_valid": is_valid,
        "state": state,
        "filename": file.filename,
        "saved_to": file_target_fullpath,
        "file_id": file_id
    }