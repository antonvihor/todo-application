"""Define request and response schemas for todos."""

from typing import Self

from pydantic import BaseModel, ConfigDict, Field, StrictBool, model_validator


class TodoCreate(BaseModel):
    """Describe a new todo belonging to an existing user."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True, frozen=True)

    user_id: int = Field(gt=0)
    title: str = Field(min_length=1, max_length=120)
    description: str = Field(default="", max_length=1000)


class Todo(TodoCreate):
    """Describe a stored todo and its completion status."""

    id: int
    completed: bool = False


class TodoUpdate(BaseModel):
    """Describe a nonempty subset of mutable todo fields."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True, frozen=True)

    title: str | None = Field(default=None, min_length=1, max_length=120)
    description: str | None = Field(default=None, max_length=1000)
    completed: StrictBool | None = None

    @model_validator(mode="after")
    def validate_changes(self) -> Self:
        """Reject empty updates and explicitly supplied null values.

        Returns
        -------
        Self
            The update with at least one non-null change.

        Raises
        ------
        ValueError
            If no fields were supplied or a supplied field is null.
        """
        if not self.model_fields_set:
            raise ValueError("Provide at least one field to update.")
        if any(getattr(self, name) is None for name in self.model_fields_set):
            raise ValueError("Updated fields must not be null.")
        return self
