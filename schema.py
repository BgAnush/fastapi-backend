from pydantic import BaseModel

class UserCreate(BaseModel):
    id: int
    email: str
    name: str
    password: str
    role: str
