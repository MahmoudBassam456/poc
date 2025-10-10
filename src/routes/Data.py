from fastapi import APIRouter, Depends, UploadFile, File, status, Body, BackgroundTasks, Request
from fastapi.responses import JSONResponse
from typing import List
import aiofiles
import os
import logging

from helpers import get_config, Config
from controllers import DataController, ProjectController, ProcessController
from models.db_model import ProjectDB
from models.ResponsesEnum.ResposeSiginalsFile import ResponseSignalsFile
from .schemes.data import ProcessRequest
from assets.services.Vector_db.Faiss_controller import FaissController


logger = logging.getLogger("uvicorn.error")
data_router = APIRouter(prefix="/api/v1/upload", tags=["upload"])

@data_router.post("/data/{file_id}")
async def upload_file(
   request: Request,
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
    # Save file record to DB
        data_base_rec=ProjectDB(db_client=request.app.mogo_client)
    
        file_id_db=await data_base_rec.create_project(project_id=file_id,file_name=file.filename,file_path=file_target_fullpath,file_extension=ProcessController(file_path=file_target_fullpath).get_file_extension())
           
    except Exception as e:
        logger.error(f"Failed to save file {file.filename}: {str(e)}")
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message": ResponseSignalsFile.Upload_Failure.value}
        )

    # Optional: Close the uploaded file (good practice)
    await file.close()
    exten_sion = ProcessController(file_path=file_target_fullpath).get_file_extension()
    return {
        "is_valid": is_valid,
        "state": state,
        "filename": file.filename,
        "saved_to": file_target_fullpath,
        "file_id in db": str(file_id_db._id),
        "file_extension": exten_sion
    }

@data_router.post("/process/{project_id}")
async def process_endpoint(
    project_id: str,
    request: Request,
    file_path: ProcessRequest = Body(...)
):
    asa =await ProjectDB(request.app.mogo_client).get_project_or_create_newone(project_id=project_id)
    file_query = asa.file_path
    test=request.app.mogo_client
    # التحقق من وجود الملف
    if not os.path.exists(file_query):
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"message": "File not found"}
        )
    ea= ProjectDB(db_client=test)
   # q=await ea.create_project(project_data=project_id)
   # test_id=await ea.get_project_or_create_newone(project_id=project_id)
    # جلب محتوى الملف
    content = ProcessController(file_path=file_query).get_file_content()
    chunked_content = ProcessController(file_path=file_query).get_chunked_content(file_content=content)

    # استدعاء Faiss
    result = FaissController(db_path=os.path.join(os.getcwd(), "routesindex", "index"))
    # يمكن إضافة محتوى مقسم إلى Faiss إذا أردت
    result.add_documents(chunked_content)

    # الحصول على الإجابة من LLM
    #BackgroundTasks(result.llms_answer(" ايه هو cypcut"))
 

    # الحصول على الإجابة من LLM
    #BackgroundTasks(result.llms_answer(" ايه هو cypcut"))

    
    # تحويل النص العربي الطويل إلى قائمة فقرات
  
    # إذا نص عادي
    
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            
            "path": file_query
          #  "test_id":str(test_id.project_id)
        },
        media_type="application/json; charset=utf-8"
    )

@data_router.post("/batch_upload/{project_id}", status_code=status.HTTP_202_ACCEPTED)
async def upload_batch_files(
    project_id: str,
    files: List[UploadFile],
    background_tasks: BackgroundTasks,
    request: Request,
    config: Config = Depends(get_config)
):
    """
    Accepts multiple files, saves them, and queues them for background processing.
    """
    project_path = ProjectController().get_project_path(file_id=project_id)
    os.makedirs(project_path, exist_ok=True)

    saved_files_paths = []
    results = {"saved": [], "failed": []}

    for file in files:
        is_valid, state = DataController().validate_config(file=file)
        if not is_valid:
            results["failed"].append({"filename": file.filename, "reason": state})
            continue

        file_target_fullpath = DataController().clean_filename_build(files_path=project_path, file=file)
        
        try:
            async with aiofiles.open(file_target_fullpath, "wb") as f:
                while chunk := await file.read(config.FILE_SIZE_CHUNK):
                    await f.write(chunk)
            
            saved_files_paths.append(file_target_fullpath)
            results["saved"].append({"filename": file.filename, "path": file_target_fullpath})
        except Exception as e:
            logging.error(f"Failed to save file {file.filename}: {e}")
            results["failed"].append({"filename": file.filename, "reason": "Failed to save file."})

    if saved_files_paths:
        # Add the processing task to the background
        background_tasks.add_task(
            ProcessController.process_and_vectorize_files,
            file_paths=saved_files_paths,
            project_id=project_id
        )
        message = f"Accepted {len(saved_files_paths)} files for processing."
    else:
        message = "No valid files were accepted for processing."

    return {"message": message, "details": results}