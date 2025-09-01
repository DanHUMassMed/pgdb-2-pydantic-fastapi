from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy.orm import Session, Query
from app.models.base import Base

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType]):
        self.model = model

    def _create_validation_hook(self):
        return True
    
    # Hook methods — override in subclass if needed
    def _apply_get_hook(self, query: Query) -> Query:
        return query

    def _apply_filter_hook(self, query: Query) -> Query:
        return query

    def _apply_multi_hook(self, query: Query) -> Query:
        return query

    def get(self, db: Session, id: Any) -> Optional[ModelType]:
        query = db.query(self.model)
        query = self._apply_get_hook(query)
        return query.filter(self.model.id == id).first()

    def filter_multi_like(
        self,
        db: Session,
        filters: Dict[str, str],
        skip: int = 0,
        limit: int = 100,
    ) -> List[ModelType]:
        query = db.query(self.model)
        query = self._apply_filter_hook(query)

        for field, value in filters.items():
            column = getattr(self.model, field, None)
            if column is None:
                raise ValueError(f"Invalid field name '{field}' for model {self.model.__name__}")
            query = query.filter(column.ilike(f"%{value}%"))

        return query.offset(skip).limit(limit).all()

    def get_multi(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[ModelType]:
        query = db.query(self.model)
        query = self._apply_multi_hook(query)
        return query.offset(skip).limit(limit).all()

    def create(self, db: Session, *, obj_in: CreateSchemaType) -> Optional[ModelType]:
        db_obj = None
        valid_input = self._create_validation_hook()
        if valid_input:
            obj_in_data = jsonable_encoder(obj_in)
            db_obj = self.model(**obj_in_data)
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
        return db_obj

    def update(
        self, db: Session, *, db_obj: ModelType, obj_in: Union[UpdateSchemaType, Dict[str, Any]]
    ) -> ModelType:
        obj_data = jsonable_encoder(db_obj)
        update_data = obj_in if isinstance(obj_in, dict) else obj_in.dict(exclude_unset=True)

        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def remove(self, db: Session, *, id: int) -> ModelType:
        obj = db.query(self.model).get(id)
        db.delete(obj)
        db.commit()
        return obj