import json
from fastapi.testclient import TestClient
from api import app, read_items, write_items, DATABASE_FILE, Item

client = TestClient(app)

def test_get_items():
    response = client.get("/items")
    assert response.status_code == 200
    assert response.json() == read_items()

def test_get_item():
    items = read_items()
    item_id = items[0]["id"]
    response = client.get(f"/items/{item_id}")
    assert response.status_code == 200
    assert response.json() == items[0]

def test_get_item_not_found():
    response = client.get("/items/999")
    assert response.status_code == 404
    assert response.json() == {"error": "Item not found"}

def test_create_item():
    item = Item(id=4, name="New Item", price=9.99)
    response = client.post("/items", json=item.dict())
    assert response.status_code == 200
    assert response.json() == item.dict()
    items = read_items()
    assert items[-1] == item.dict()

def test_update_item():
    items = read_items()
    item_id = items[0]["id"]
    updated_item = Item(id=item_id, name="Updated Item", price=19.99)
    response = client.put(f"/items/{item_id}", json=updated_item.dict())
    assert response.status_code == 200
    assert response.json() == updated_item.dict()
    items = read_items()
    assert items[0] == updated_item.dict()

def test_update_item_not_found():
    response = client.put("/items/999", json={"id": 999, "name": "Invalid Item", "price": 0.0})
    assert response.status_code == 404
    assert response.json() == {"error": "Item not found"}

def test_delete_item():
    items = read_items()
    item_id = items[0]["id"]
    response = client.delete(f"/items/{item_id}")
    assert response.status_code == 200
    assert response.json() == {"message": "Item deleted"}
    items = read_items()
    assert not any(item["id"] == item_id for item in items)

def test_delete_item_not_found():
    response = client.delete("/items/999")
    assert response.status_code == 404
    assert response.json() == {"error": "Item not found"}