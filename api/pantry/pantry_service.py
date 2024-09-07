from typing import List
from fastapi import APIRouter
from storage.utils import read_pantry_items, write_pantry_items
from models.models import InventoryItem

pantry_router = APIRouter(prefix="/pantry")

@pantry_router.get("/items", response_model=List[InventoryItem])
def get_items():
    items = read_pantry_items()
    return items

@pantry_router.get("/items/{item_id}", response_model=InventoryItem)
def get_item(item_id: str):
    items = read_pantry_items()
    for item in items:
        if item["id"] == item_id:
            return item
    return {"error": "Item not found"}

@pantry_router.post("/items", response_model=InventoryItem)
def create_item(item: InventoryItem):
    print(item)
    items = read_pantry_items()
    item_dict = item.dict()
    items.append(item_dict)
    write_pantry_items(items)
    return item

@pantry_router.put("/items/{item_id}", response_model=InventoryItem)
def update_item(item_id: str, item: InventoryItem):
    items = read_pantry_items()
    for i, existing_item in enumerate(items):
        if existing_item["id"] == item_id:
            items[i] = item.dict()
            items[i]["id"] = item_id  # Ensure the ID remains the same
            write_pantry_items(items)
            return item
    return {"error": "Item not found"}

@pantry_router.delete("/items/{item_id}")
def delete_item(item_id: str):
    items = read_pantry_items()
    for i, item in enumerate(items):
        if item["id"] == item_id:
            del items[i]
            write_pantry_items(items)
            return {"message": "Item deleted"}
    return {"error": "Item not found"}