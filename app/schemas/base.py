from typing import Optional, TypeVar, Generic, List
from pydantic import BaseModel

T = TypeVar('T')

class BaseResponse(BaseModel, Generic[T]):
    status: str
    message: str
    errors: Optional[List[dict]] = None
    data: Optional[T] = None