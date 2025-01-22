from pydantic import BaseModel
from typing import Optional

class FileBase(BaseModel):
    id: int
    file_path: str

    class Config:
        from_attributes = True

class FileCreate(BaseModel):
    file_path: str

class FileUpdate(BaseModel):
    file_path: Optional[str] = None