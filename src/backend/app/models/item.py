from typing import Optional

from sqlmodel import Field, SQLModel


class ItemBase(SQLModel):
    name: str = Field(title="The item name")


class Item(ItemBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)


class CreateItem(ItemBase):
    model_config = {"json_schema_extra": {"examples": [{"name": "Apple"}]}}


class ReadItem(ItemBase):
    id: int


class UpdateItem(SQLModel):
    name: Optional[str] = None

    model_config = {"json_schema_extra": {"examples": [{"name": "Orange"}]}}
