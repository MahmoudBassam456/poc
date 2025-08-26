from fastapi import APIRouter, Depends, UploadFile, File, status, Body
from fastapi.responses import JSONResponse
import os
import aiofiles
import logging
from helpers import get_config, Config
from controllers import DataController, ProjectController, ProcessController
from models import ResponseSignalsFile
from .schemes.data import ProcessRequest
from assets.services.Vector_db.Faiss_controller import FaissController

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
    exten_sion = ProcessController(file_path=file_target_fullpath).get_file_extension()
    return {
        "is_valid": is_valid,
        "state": state,
        "filename": file.filename,
        "saved_to": file_target_fullpath,
        "file_id": file_id,
        "file_extension": exten_sion
    }
@data_router.post("/process/{file_id}")
async def process_endpoint(
    file_id: str,
    file_path: ProcessRequest = Body(...)
):
    file_query = file_path.file_path

    # التحقق من وجود الملف
    if not os.path.exists(file_query):
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"message": "File not found"}
        )

    # جلب محتوى الملف
    content = ProcessController(file_path=file_query).get_file_content()
    chunked_content = ProcessController(file_path=file_query).get_chunked_content(file_content=content)

    # استدعاء Faiss
    result = FaissController(db_path="/mnt/d/Threecuts/poc/src/routesindex/index")
    # يمكن إضافة محتوى مقسم إلى Faiss إذا أردت
    # result.add_documents(chunked_content)

    # الحصول على الإجابة من LLM
    res_text = result.llms_answer(" ايه هو cypcut")

    # تحويل النص العربي الطويل إلى قائمة فقرات
    res_paragraphs = res_text.split("\n")  # كل سطر عنصر في القائمة
    if isinstance(res_text, list):
    # تحويل كل Document إلى نص
     res_paragraphs = [doc.page_content for doc in res_text]
    else:
    # إذا نص عادي
     res_paragraphs = str(res_text).split("\n")
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "Result": res_paragraphs
        },
        media_type="application/json; charset=utf-8"
    )