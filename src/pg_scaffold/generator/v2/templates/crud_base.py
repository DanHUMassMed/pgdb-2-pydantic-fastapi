from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union, Sequence
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy.orm import Session, Query

from app.models.base import Base

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
ReadSchemaType = TypeVar("ReadSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class CRUDBase(Generic[ModelType, CreateSchemaType, ReadSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType], 
                 CreateSchema: Type[CreateSchemaType],
                 ReadSchema: Type[ReadSchemaType],
                 UpdateSchema: Type[UpdateSchemaType],
                 db: Session):
        self.model = model
        self.CreateSchema = CreateSchema
        self.ReadSchema = ReadSchema
        self.UpdateSchema = UpdateSchema
        self.db = db

    # Hook methods — override in subclass if needed
    def _get_first_hook(self, query: Query) -> Query:
        return query

    def _get_many_hook(self, query: Query) -> Query:
        return query

    def _get_many_like_hook(self, query: Query) -> Query:
        return query

    def _create_validation_hook(self):
        return True
    
    def get_by_id(self,id: Any) -> Optional[ReadSchemaType]:
        query = self.db.query(self.model)
        query = self._get_first_hook(query)
        db_obj = query.filter(self.model.id == id).first()
        return self.ReadSchema.model_validate(db_obj)
    
    def get_many(self, *, skip: int = 0, limit: int = 100
    ) -> List[ReadSchemaType]:
        query = self.db.query(self.model)
        query = self._get_many_hook(query)
        db_objs = query.offset(skip).limit(limit).all()
        return [self.ReadSchema.model_validate(db_obj) for db_obj in db_objs]

    def _resolve_column(self, dotted_field: str):
        """Resolve 'event.name' → Event.name using SQLAlchemy relationships."""
        parts = dotted_field.split(".")
        current_model = self.model
        column = None

        for part in parts:
            if hasattr(current_model, part):
                attr = getattr(current_model, part)
                # If it's a relationship (not a column), move into its class
                if hasattr(attr, "property") and hasattr(attr.property, "mapper"):
                    current_model = attr.property.mapper.class_
                    column = attr
                else:
                    column = attr
            else:
                raise ValueError(f"Invalid field path: {dotted_field}")

        return column
    
    def get_many_where(
        self,
        where: Sequence[Sequence[Any]],
        skip: int = 0,
        limit: int = 100
    ) -> List[ReadSchemaType]:
        """
        Retrieve multiple rows matching a list of condition triplets.

        Args:
            where: A list of [field, operator, value] expressions, e.g.
                [
                    ["status", "eq", "active"],
                    ["event_id", "ne", 5],
                    ["score", "gte", 80],
                    ["name", "like", "%John%"],
                    ["id", "in", [1, 2, 3]]
                ]
            skip: Offset for pagination.
            limit: Maximum number of records to return.

        Returns:
            A list of validated ReadSchemaType instances.
        """
        query = self.db.query(self.model)

        for condition in where:
            if len(condition) != 3:
                raise ValueError(f"Invalid condition format: {condition}")

            field, op, value = condition

            column = self._resolve_column(field)
            
            match op:
                case "eq": query = query.filter(column == value)
                case "ne": query = query.filter(column != value)
                case "lt": query = query.filter(column < value)
                case "lte": query = query.filter(column <= value)
                case "gt": query = query.filter(column > value)
                case "gte": query = query.filter(column >= value)
                case "in":
                    if not isinstance(value, (list, tuple, set)):
                        raise ValueError(f"Expected list/tuple for 'in' filter on '{field}'")
                    query = query.filter(column.in_(value))
                case "like": query = query.filter(column.like(value))
                case "ilike": query = query.filter(column.ilike(value))
                case _:
                    raise ValueError(f"Unsupported operator: {op}")

        query = self._get_many_hook(query)
        db_objs = query.offset(skip).limit(limit).all()
        return [self.ReadSchema.model_validate(db_obj) for db_obj in db_objs]


    def create(self, obj_in: CreateSchemaType) -> Optional[ReadSchemaType]:
        db_obj = None
        valid_input = self._create_validation_hook()
        if valid_input:
            obj_in_data = jsonable_encoder(obj_in)
            self.db_obj = self.model(**obj_in_data)
            self.db.add(db_obj)
            self.db.commit()
            self.db.refresh(db_obj)
        return self.ReadSchema.model_validate(db_obj)


    def update(
        self, obj_in: Union[UpdateSchemaType, Dict[str, Any]]
    ) -> Optional[ReadSchemaType]:
        db_obj = self.db.query(self.model).get(obj_in.id)
        obj_data = jsonable_encoder(db_obj)
        update_data = obj_in if isinstance(obj_in, dict) else obj_in.dict(exclude_unset=True)

        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])

        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return self.ReadSchema.model_validate(db_obj)

    def remove(self, *, id: int) -> Optional[ReadSchemaType]:
        #db_obj = self.db.query(self.model).get(id)
        db_obj = self.db.get(self.model, id)
        self.db.delete(db_obj)
        self.db.commit()
        return self.ReadSchema.model_validate(db_obj)