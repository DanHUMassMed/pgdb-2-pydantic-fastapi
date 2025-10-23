from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union
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

    def get_many_like(
        self,
        filters: Dict[str, str],
        skip: int = 0,
        limit: int = 100,
    ) -> List[ReadSchemaType]:
        query = self.db.query(self.model)
        query = self._get_many_like_hook(query)

        for field, value in filters.items():
            column = getattr(self.model, field, None)
            if column is None:
                raise ValueError(f"Invalid field name '{field}' for model {self.model.__name__}")
            query = query.filter(column.ilike(f"%{value}%"))

        db_objs = query.offset(skip).limit(limit).all()
        return [self.ReadSchema.model_validate(db_obj) for db_obj in db_objs]

    def create(self, obj_in: CreateSchemaType) -> Optional[ReadSchemaType]:
        db_obj = None
        valid_input = self._create_validation_hook()
        if valid_input:
            obj_in_data = jsonable_encoder(obj_in)
            db_obj = self.model(**obj_in_data)
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