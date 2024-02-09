from typing import Annotated

from fastapi import APIRouter, HTTPException, Path, Query, status
from sqlmodel import select

from ...database import SessionDep
from ...models.item import CreateItem, Item, ReadItem, UpdateItem

router = APIRouter()


@router.get("/", response_model=list[ReadItem])
async def read_items(
    session: SessionDep,
    offset: int = 0,
    limit: int = Query(default=10, le=10),
):
    """
    Get items.
    """
    db_items = session.exec(select(Item).offset(offset).limit(limit)).all()
    return db_items


@router.post("/", response_model=ReadItem, status_code=status.HTTP_201_CREATED)
async def create_item(session: SessionDep, item: CreateItem):
    """
    Create new item.
    """
    db_item = Item.model_validate(item)
    session.add(db_item)
    session.commit()
    session.refresh(db_item)
    return db_item


@router.get("/{item_id}", response_model=ReadItem)
async def read_item(
    session: SessionDep,
    item_id: Annotated[int, Path(title="The ID of the item to get")],
):
    """
    Get item by ID.
    """
    db_item = session.get(Item, item_id)
    if not db_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Item not found"
        )
    return db_item


@router.patch("/{item_id}", response_model=ReadItem)
async def update_item(
    session: SessionDep,
    item_id: Annotated[int, Path(title="The ID of the item to update")],
    item: UpdateItem,
):
    """
    Update an item by ID.
    """
    db_item = session.get(Item, item_id)
    if not db_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Item not found"
        )
    item_data = item.model_dump(exclude_unset=True)
    if not item_data:
        raise HTTPException(
            status_code=status.HTTP_204_NO_CONTENT, detail="Item not updated"
        )
    for key, value in item_data.items():
        setattr(db_item, key, value)
    session.add(db_item)
    session.commit()
    session.refresh(db_item)
    return db_item


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(
    session: SessionDep,
    item_id: Annotated[int, Path(title="The ID of the item to delete")],
):
    """
    Delete an item by ID.
    """
    db_item = session.get(Item, item_id)
    if not db_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Item not found"
        )
    session.delete(db_item)
    session.commit()
