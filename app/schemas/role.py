from pydantic import BaseModel, StringConstraints, ConfigDict
from typing import List, Annotated

from .base import BaseResponse

class BaseRoleRequest(BaseModel):
    name: Annotated[str, StringConstraints(min_length=1, max_length=25)]

class CreateRoleRequest(BaseRoleRequest):
    pass

class UpdateRoleRequest(BaseRoleRequest):
    pass

class DetailRole(BaseModel):
    id: int
    name: str

    model_config = ConfigDict(from_attributes=True)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name
        }

class DetailRoleResponse(BaseResponse[DetailRole]):
    pass

class ListRoleResponse(BaseResponse[List[DetailRole]]):
    pass