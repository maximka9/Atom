import requests
import uuid

BASE_URL = "http://localhost:8000"

organizations_data = [
    {
        "name": "OO 1",
        "waste": {
            "пластик": 10,
            "стекло": 50,
            "биоотходы": 50
        },
        "location": "OO 1"
    },
    {
        "name": "OO 2",
        "waste": {
            "пластик": 60,
            "стекло": 20,
            "биоотходы": 50
        },
        "location": "OO 2"
    }
]

storages_data = [
    {
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
    },
    {
        "name": "MHO 2",
        "capacity": {
            "пластик": 50,
            "биоотходы": 150
        },
        "current_stock": {
            "пластик": 0,
            "биоотходы": 0
        },
        "location": "MHO 2",
        "accepts": ["пластик", "биоотходы"]
    },
    {
        "name": "MHO 3",
        "capacity": {
            "пластик": 10,
            "биоотходы": 250
        },
        "current_stock": {
            "пластик": 0,
            "биоотходы": 0
        },
        "location": "MHO 3",
        "accepts": ["пластик", "биоотходы"]
    },
    {
        "name": "MHO 6",
        "capacity": {
            "стекло": 100,
            "биоотходы": 150
        },
        "current_stock": {
            "стекло": 0,
            "биоотходы": 0
        },
        "location": "MHO 6",
        "accepts": ["стекло", "биоотходы"]
    },
    {
        "name": "MHO 8",
        "capacity": {
            "стекло": 35,
            "пластик": 25,
            "биоотходы": 52
        },
        "current_stock": {
            "стекло": 0,
            "пластик": 0,
            "биоотходы": 0
        },
        "location": "MHO 8",
        "accepts": ["стекло", "пластик", "биоотходы"]
    },
    {
        "name": "MHO 5",
        "capacity": {
            "стекло": 220,
            "биоотходы": 25
        },
        "current_stock": {
            "стекло": 0,
            "биоотходы": 0
        },
        "location": "MHO 5",
        "accepts": ["стекло", "биоотходы"]
    },
    {
        "name": "MHO 7",
        "capacity": {
            "пластик": 100,
            "биоотходы": 250
        },
        "current_stock": {
            "пластик": 0,
            "биоотходы": 0
        },
        "location": "MHO 7",
        "accepts": ["пластик", "биоотходы"]
    },
    {
        "name": "MHO 9",
        "capacity": {
            "пластик": 250,
            "биоотходы": 20
        },
        "current_stock": {
            "пластик": 0,
            "биоотходы": 0
        },
        "location": "MHO 9",
        "accepts": ["пластик", "биоотходы"]
    }
]

# Функция для отправки POST-запросов
def create_organization(data):
    response = requests.post(f"{BASE_URL}/organization/", json=data)
    if response.status_code == 200:
        print(f"Организация {data['name']} успешно добавлена.")
    else:
        print(f"Ошибка при добавлении организации {data['name']}: {response.json()}")

def create_storage(data):
    response = requests.post(f"{BASE_URL}/storage/", json=data)
    if response.status_code == 200:
        print(f"Хранилище {data['name']} успешно добавлено.")
    else:
        print(f"Ошибка при добавлении хранилища {data['name']}: {response.json()}")

def transfer_waste_to_storage(organization_name, waste_type):
    transfer_data = {
        "organization_name": organization_name,
        "waste_type": waste_type
    }
    response = requests.post(f"{BASE_URL}/transfer_waste/", json=transfer_data)
    if response.status_code == 200:
        print(f"Отходы типа '{waste_type}' успешно переданы организацией '{organization_name}'.")
    else:
        print(f"Ошибка при передаче отходов типа '{waste_type}' организацией '{organization_name}': {response.json()}")

# Создаем организации
for org_data in organizations_data:
    create_organization(org_data)

# Создаем хранилища
for storage_data in storages_data:
    create_storage(storage_data)

# Передаем отходы
for org_data in organizations_data:
    for waste_type in org_data["waste"]:
        transfer_waste_to_storage(org_data["name"], waste_type)
