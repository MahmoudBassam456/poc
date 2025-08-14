from fastapi import APIRouter, Depends, UploadFile, File, status
from fastapi.responses import JSONResponse
import os
import aiofiles

from helpers import get_config, Config
from controllers import DataController, ProjectController

data_router = APIRouter(prefix="/api/v1/upload", tags=["upload"])

@data_router.post("/data/{file_id}")
async def upload_file(
    file_id: str,
    file: UploadFile = File(...),
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
    project = ProjectController()
    file_target_base = project.get_project_path(file_id=file_id)

    # Ensure directory exists
    os.makedirs(file_target_base, exist_ok=True)

    # Full path to save file
    file_target_fullpath = os.path.join(file_target_base, file.filename)

    # Read entire file into memory (no chunks)
    content = await file.read()  # ← Entire file read at once

    # Write entire content in one async write
    try:
        async with aiofiles.open(file_target_fullpath, "wb") as f:
            await f.write(content)  # ← Written all at once
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message": f"Failed to save file: {str(e)}"}
        )

    # Optional: Close the uploaded file (good practice)
    await file.close()

    return {
        "is_valid": is_valid,
        "state": state,
        "filename": file.filename,
        "saved_to": file_target_fullpath,
        "file_size": len(content),
    }