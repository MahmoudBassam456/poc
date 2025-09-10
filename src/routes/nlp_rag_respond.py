from fastapi import APIRouter, Depends,Request,status,BackgroundTasks,Request
from fastapi.responses import JSONResponse
from fastapi import Body
import logging
from helpers import get_config, Config
from assets.services.Vector_db.Faiss_controller import FaissController
from motor.motor_asyncio import AsyncIOMotorClient
from models.db_model.db_session import SessionDB
from models.ResponsesEnum.session_statusEnum import SessionStatusEnum
import asyncio


nlp_router=APIRouter(prefix="/api/v1/nlp",tags=["nlp"])


@nlp_router.post("/chat_recieve")
async def query_recieve(request: Request, background_tasks: BackgroundTasks, Query: str = Body(..., embed=True)):
   try:
       SessionDB_instance = SessionDB(db_client=request.app.mogo_client)
       new_session = await SessionDB_instance.create_session()
       session_id = str(new_session._id)
       background_tasks.add_task(rag_respond, Query, session_id, request.app.mogo_client)
       return JSONResponse(status_code=status.HTTP_200_OK, content={"session_id": session_id})
   except Exception as e:
       logging.error(f"Error in /rag_respond: {e}")
       return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={"error": "Internal Server Error"})
    

async def rag_respond(Query: str, session_id: str, db_client: AsyncIOMotorClient):
    try:
        faiss_instance = FaissController(db_path="/mnt/d/Threecuts/poc/src/routesindex/index")
        res_text = faiss_instance.llms_answer(Query)
        SessionDB_instance = SessionDB(db_client=db_client)

    # تجهيز الرد
        if isinstance(res_text, list):
          raw_text = "\n".join(doc.page_content for doc in res_text)
        else:
          raw_text = str(res_text).replace("\r\n", "\n").replace("\r", "\n").strip()



    # ✅ استخدم await بدلاً من asyncio.run()
        await SessionDB_instance.update_session_status(
        session_id=session_id,
        message=[raw_text]
    )

    except Exception as e:
        logging.error(f"Error in /rag_respond: {e}")
       
@nlp_router.get("/session/{session_id}")
async def get_session_status(request: Request, session_id: str):
    try:
        SessionDB_instance = SessionDB(db_client=request.app.mogo_client)
        session_data = await SessionDB_instance.get_session_by_id(session_id=session_id)
        if session_data.status==SessionStatusEnum.DONE.value:
            return JSONResponse(status_code=status.HTTP_200_OK, content={"session": session_data.message, "status": session_data.status})
        else:
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={"error": "Session not found"})
    except Exception as e:
        logging.error(f"Error in /session/{session_id}: {e}")
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={"error": "Internal Server Error"})