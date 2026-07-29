from pydantic import BaseModel
import uuid

class CategorySchema(BaseModel):
    id: uuid.UUID
    name: str
    type: str
    icon: str