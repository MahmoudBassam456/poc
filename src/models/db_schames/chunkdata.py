from pydantic import BaseModel, Field
from typing import Optional
from bson.objectid import ObjectId  # to help with mongodb object id in pydantic model python
# Fixed typo in import statement
class chunkdata(BaseModel):
    _id: Optional[ObjectId]
    file_id: str = Field(..., min_length=1)
    chunk_index: int = Field(..., ge=0)  # Ensure chunk_index is non-negative
    data: bytes  # Store chunk data as bytes

    class Config:
        arbitrary_types_allowed = True