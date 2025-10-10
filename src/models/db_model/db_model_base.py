from motor.motor_asyncio import AsyncIOMotorClient

class db_model_base:
    def __init__(self, db_client: AsyncIOMotorClient):
        self.db_client = db_client