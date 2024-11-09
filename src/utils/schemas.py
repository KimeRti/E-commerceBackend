import typing
from pydantic import BaseModel, GetJsonSchemaHandler, Extra, field_validator
from typing import Any, Annotated, Callable, List, Union
from datetime import datetime

from bson import ObjectId
from pydantic_core import core_schema

from pydantic.json_schema import JsonSchemaValue

from uuid import UUID

T = typing.TypeVar("T")


class GeneralResponse(BaseModel, typing.Generic[T]):
    message: str
    status: typing.Optional[int] = 200
    code: typing.Optional[str] = "EMPTY_CODE"
    details: typing.Optional[T] = None

    class Config:
        arbitrary_types_allowed = True

    def change_language(self, lang):
        print(self)
        print(self.details)
        print(lang)
        return self


class UUIDView:  # use with BaseModel subclassed
    id: typing.Union[UUID, str]

    @field_validator('id')
    def str_id(cls, v):
        return str(v)


class AtView:
    created_at: Union[int, datetime]
    updated_at: Union[int, datetime]

    @field_validator('created_at', 'updated_at')
    def int_date(cls, v):
        if isinstance(v, datetime):
            return int(v.timestamp()) * 1000
        return v


class PaginationInfo(BaseModel):
    currentPage: int
    currentPageSize: int
    hasNext: bool
    hasPrevious: bool
    pageCount: int
    pageSize: int
    remainingPages: int
    totalItems: int


class ListView(BaseModel, typing.Generic[T], extra=Extra.allow):
    info: typing.Optional[PaginationInfo] = None
    items: typing.List[T]


class PaginationGet(BaseModel):
    page: typing.Optional[int] = 1
    pageSize: typing.Optional[int] = 10
    paginate: typing.Optional[bool] = True
    search: typing.Optional[str] = None
    order: typing.Optional[bool] = None

    @field_validator('page')
    def page_validator(cls, v):
        if v < 1:
            raise ValueError("Sayfa 0'dan büyük olmalı.")
        return v


class ObjectIdPydanticAnnotation:
    @classmethod
    def __get_pydantic_core_schema__(
            cls,
            _source_type: Any,
            _handler: Callable[[Any], core_schema.CoreSchema],
    ) -> core_schema.CoreSchema:
        def validate_from_str(id_: str) -> ObjectId:
            return ObjectId(id_)

        from_str_schema = core_schema.chain_schema(
            [
                core_schema.str_schema(),
                core_schema.no_info_plain_validator_function(validate_from_str),
            ]
        )

        return core_schema.json_or_python_schema(
            json_schema=from_str_schema,
            python_schema=core_schema.union_schema(
                [
                    # check if it's an instance first before doing any further work
                    core_schema.is_instance_schema(ObjectId),
                    from_str_schema,
                ]
            ),
            serialization=core_schema.plain_serializer_function_ser_schema(
                lambda instance: str(instance)
            ),
        )

    @classmethod
    def __get_pydantic_json_schema__(
            cls, _core_schema: core_schema.CoreSchema, handler: GetJsonSchemaHandler
    ) -> JsonSchemaValue:
        # Use the same schema that would be used for `str`
        return handler(core_schema.str_schema())


StrObjectId = Annotated[ObjectId, ObjectIdPydanticAnnotation]


class Id(BaseModel):
    id: UUID

    class Config:
        from_attributes = True


def check_exist(v):
    id_set = set()
    for i in v:
        if i.id in id_set:
            raise ValueError("Duplicate permission ID found.")
        id_set.add(i.id)
    return v


def transform_list(replaces: List[Union[UUID, Id]]) -> List[UUID]:
    transformed_list = []
    for i in replaces:
        if isinstance(i, Id):
            transformed_list.append(i.id)
        else:
            transformed_list.append(i)
    return transformed_list
