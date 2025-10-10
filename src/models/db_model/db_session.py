from ..db_schames.session import session
from .db_model_base import db_model_base
from ..ResponsesEnum.session_statusEnum import SessionStatusEnum
from bson.objectid import ObjectId
class SessionDB(db_model_base):
    def __init__(self, db_client):
        super().__init__(db_client=db_client)
        self.collection = self.db_client["sessions"]
    async def create_session(self, status: str = SessionStatusEnum.PENDING.value, message: str = [""]):

        session_data = session(status=status, message=message)
        result = await self.collection.insert_one(session_data.dict())
        session_data._id = result.inserted_id
        return session_data
    async def update_session_status(self, session_id:str , message: str =[""]):
        if len(message)>0:

         update_data = {"status": SessionStatusEnum.DONE.value, "message": message}
         result = await self.collection.update_one({"_id": ObjectId(session_id)}, {"$set": update_data})
         if result.modified_count > 0:# True if update was successful, False otherwise
             return result
         else:
             return None
        else:
            return False
    async def get_session_by_id(self, session_id):
        existing = await self.collection.find_one({"_id": ObjectId(session_id)})
        if existing:
            return session(**existing)
        return None
    async def delete_session(self, session_id):
        result = await self.collection.delete_one({"_id": ObjectId(session_id)})
        if result.deleted_count > 0:
            return True
        else:
            return False
        