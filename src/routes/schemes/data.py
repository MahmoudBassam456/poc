from pydantic import BaseModel
from typing import Optional
from typing import List, Optional
class ProcessRequest(BaseModel):
    file_path: str
    chunk_size: Optional[int] = 1024 * 1024  # Default to 1MB
    overlap_size: Optional[int] =20  # Default to no overlap
    do_reset: Optional[int] = 0  # Default to no reset