"""Define request and response schemas for users."""

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserCreate(BaseModel):
    """Describe the name and email required to create a user."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True, frozen=True)

    name: str = Field(min_length=1, max_length=80)
    email: EmailStr


class User(UserCreate):
    """Describe a stored user with a server-assigned identifier."""

    id: int
