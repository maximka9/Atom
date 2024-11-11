import pytest
from fastapi.testclient import TestClient
from uuid import UUID
from main import app, Organization, Storage, WasteType

client = TestClient(app)

organization_data = {
    "name": "OO 1",
    "waste": {
        "пластик": 10,
        "стекло": 50,
        "биоотходы": 50
    },
    "location": "OO 1"
}

storage_data = {
    "name": "MHO 1",
    "capacity": {
        "стекло": 300,
        "пластик": 100
    },
    "current_stock": {
        "стекло": 0,
        "пластик": 0
    },
    "location": "MHO 1",
    "accepts": ["стекло", "пластик"]
}

# Тест для создания организации
def test_create_organization():
    response = client.post("/organization/", json=organization_data)
    assert response.status_code == 200
    assert "id" in response.json()  # Проверка, что организация получила ID

# Тест для создания хранилища
def test_create_storage():
    response = client.post("/storage/", json=storage_data)
    assert response.status_code == 200
    assert "id" in response.json()  # Проверка, что хранилище получило ID

# Тест для передачи отходов
def test_transfer_waste():
    # Сначала создаем организацию и хранилище
    response = client.post("/organization/", json=organization_data)
    organization_id = response.json()["id"]

    response = client.post("/storage/", json=storage_data)
    storage_id = response.json()["id"]

    # Создаем запрос на передачу отходов
    transfer_request = {
        "organization_name": "OO 1",
        "waste_type": "стекло"
    }

    response = client.post("/transfer_waste/", json=transfer_request)
    assert response.status_code == 200
    assert "message" in response.json()  # Проверка, что в ответе есть сообщение

# Тест для проверки наличия хранилища по ID
def test_get_storage_availability():
    # Создаем хранилище
    response = client.post("/storage/", json=storage_data)
    storage_id = UUID(response.json()["id"])

    # Проверяем доступность хранилища
    response = client.get(f"/storage/{storage_id}/availability/")
    assert response.status_code == 200
    assert response.json()["name"] == "MHO 1"  # Проверяем, что возвращаемое хранилище совпадает

# Тест для получения всех организаций
def test_get_organizations():
    response = client.get("/organizations/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)  # Проверка, что ответ - это список организаций

# Тест для получения всех хранилищ
def test_get_storages():
    response = client.get("/storages/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)  # Проверка, что ответ - это список хранилищ
