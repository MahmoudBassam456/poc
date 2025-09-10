from pydantic import BaseModel, Field,validator
from typing import Optional
from bson.objectid import ObjectId  # to help with mongodb object id in pydantic model python

class project(BaseModel):
    _id:Optional[ObjectId]
    project_id:str=Field(...,min_length=1)
    file_name:Optional[str]=Field(...,min_length=0)
    file_path:Optional[str]=Field(...,min_length=0)
    file_extension:Optional[str]=Field(...,min_length=0)
  
    class Config:
        arbitrary_types_allowed = True
       

