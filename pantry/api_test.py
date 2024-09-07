import requests

BASE_URL = "http://localhost:8000/pantry"

def test_create_item():
    url = f"{BASE_URL}/items"
    payload = {
        "name": "example item",
        "quantity": 10
    }
    response = requests.post(url, json=payload)
    print("Create Item:", response.json())

def test_get_items():
    url = f"{BASE_URL}/items"
    response = requests.get(url)
    print("Get Items:", response.json())

def test_update_item(item_id):
    url = f"{BASE_URL}/items/{item_id}"
    payload = {
        "name": "updated item",
        "quantity": 20
    }
    response = requests.put(url, json=payload)
    print("Update Item:", response.json())

def test_delete_item(item_id):
    url = f"{BASE_URL}/items/{item_id}"
    response = requests.delete(url)
    print("Delete Item:", response.json())

if __name__ == "__main__":
    # Test create item
    test_create_item()
    
    # Test get items
    test_get_items()
    
    # Assuming you have an item with ID 1 for testing update and delete
    test_update_item(1)
    test_delete_item(1)