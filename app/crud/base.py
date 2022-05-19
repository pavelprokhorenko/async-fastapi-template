from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union

from databases import Database
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy import Table, delete, update

ModelTable = TypeVar("ModelTable", bound=Table)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class CRUDBase(Generic[ModelTable, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelTable]):
        """
        CRUD object with async default methods to Create, Read, Update, Delete (CRUD).

        **Parameters**

        * `model`: A SQLAlchemy model class
        * `schema`: A Pydantic model (schema) class
        """
        self.model = model

    async def get(self, db: Database, *, model_id: Any) -> Optional[Any]:
        return await db.fetch_one(
            self.model.select().where(self.model.c.id == model_id)
        )

    async def get_multi(
        self, db: Database, *, skip: int = 0, limit: int = 100
    ) -> List[Any]:
        return await db.fetch_all(self.model.select().offset(skip).limit(limit))

    async def create(self, db: Database, *, obj_in: CreateSchemaType) -> Any:
        obj_in_data = jsonable_encoder(obj_in)
        db_query = self.model.insert().values(**obj_in_data)
        obj_id = await db.execute(db_query)
        return await self.get(db=db, model_id=obj_id)

    async def update(
        self,
        db: Database,
        *,
        db_obj: Any,
        obj_in: Union[UpdateSchemaType, Dict[str, Any]]
    ) -> Any:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        obj_id = db_obj.id
        await db.execute(
            update(self.model).where(self.model.c.id == obj_id).values(**update_data)
        )
        return await self.get(db=db, model_id=obj_id)

    async def remove(self, db: Database, *, model_id: int) -> None:
        return await db.execute(delete(self.model).where(self.model.c.id == model_id))
