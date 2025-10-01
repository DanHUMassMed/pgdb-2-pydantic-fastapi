"""
Base schema classes for common Pydantic configuration and patterns.
"""
from pydantic import BaseModel, ConfigDict
from typing import Optional


class BaseSchema(BaseModel):
    """Base schema class with common Pydantic configuration.
    
    All application schemas should inherit from this class to ensure
    consistent configuration across the entire schema layer.
    """
    model_config = ConfigDict(
        from_attributes=True,  # Enable ORM model-to-schema conversion
        validate_assignment=True,  # Validate on field assignment
        use_enum_values=True,  # Use enum values instead of enum objects
        str_strip_whitespace=True,  # Strip whitespace from strings
    )


class BaseCreateSchema(BaseSchema):
    """Base schema for create operations.
    
    Excludes auto-generated fields like ID and timestamps that
    should not be provided by clients during creation.
    """
    pass


class BaseReadSchema(BaseSchema):
    """Base schema for read operations.
    
    Includes the primary key since all database records have an ID.
    """
    id: int


class BaseUpdateSchema(BaseSchema):
    """Base schema for update operations.
    
    All fields are optional since partial updates should be supported.
    ID is excluded since it's typically passed in the URL path.
    """
    pass


# OPTIONAL: Soft delete schema for entities that support soft deletion
class SoftDeleteSchema(BaseSchema):
    """Base schema for entities with soft delete functionality."""
    is_deleted: Optional[bool] = None
    deleted_at: Optional[str] = None