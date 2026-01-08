from pydantic import BaseModel

from app.models.user import UserRole


class UserOut(BaseModel):
    id: int
    email: str
    full_name: str | None
    role: UserRole

    class Config:
        from_attributes = True
