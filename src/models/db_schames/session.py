from pydantic import BaseModel, Field
from typing import Optional, List
from bson.objectid import ObjectId  #
class session(BaseModel):
    _id:Optional[ObjectId]
    status:Optional[str]=Field(...,min_length=0)
    message:Optional[List[str]]=Field(...,min_length=0)
  
    class Config:
        arbitrary_types_allowed = True