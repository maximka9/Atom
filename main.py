from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List, Dict
from enum import Enum
from uuid import UUID, uuid4
import logging

# Настроим базовую конфигурацию для логирования
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()


# Модели данных
class WasteType(Enum):
    BIO = "биоотходы"
    GLASS = "стекло"
    PLASTIC = "пластик"

class Organization(BaseModel):
    id: UUID = None 
    name: str
    waste: Dict[WasteType, int]  
    location: str 

class Storage(BaseModel):
    id: UUID = None  
    name: str
    capacity: Dict[WasteType, int]  
    current_stock: Dict[WasteType, int]  
    location: str  
    accepts: List[WasteType]  

class TransferWasteRequest(BaseModel):
    organization_name: str  
    waste_type: WasteType
        

app = FastAPI()


organizations = []
storages = []


@app.get("/storages/")
def get_storages():
    if not storages:
        raise HTTPException(status_code=404, detail="Хранилища не найдены")
    return storages

@app.post("/storage/")
def create_storage(storage: Storage):
    storage.id = uuid4()  
    storages.append(storage)
    return {"message": "Хранилище добавлено", "id": str(storage.id)}

@app.get("/storage/{storage_id}/availability/")
def get_storage_availability(storage_id: UUID):  
    storage = next((s for s in storages if s.id == storage_id), None)
    if not storage:
        raise HTTPException(status_code=404, detail="Хранилище не найдено")
    return storage

# Организации
@app.post("/organization/")
def create_organization(organization: Organization):
    organization.id = uuid4()  
    organizations.append(organization)
    return {"message": "Организация добавлена", "id": str(organization.id)}

@app.get("/organizations/")
def get_organizations():
    if not organizations:
        raise HTTPException(status_code=404, detail="Организации не найдены")
    return organizations
distances = {
        ("OO 1", "MHO 1"): 100,
        ("OO 1", "MHO 2"): 50,
        ("OO 1", "MHO 3"): 600,
        ("OO 2", "MHO 3"): 50,
        ("MHO 1", "MHO 8"): 500,
        ("MHO 2", "MHO 5"): 50,
        ("MHO 3", "MHO 7"): 50,
        ("MHO 3", "MHO 6"): 600,
        ("MHO 8", "MHO 9"): 10,
    }
def get_distance(location1: str, location2: str) -> float:
    
    distance = distances.get((location1, location2), float('inf'))
    return distance
def get_route_exists(location1: str, location2: str, get_distance: callable) -> bool:
    """Проверка, существует ли маршрут между двумя локациями."""
    visited = set()
    
    def dfs(current):
        if current == location2:
            return True
        visited.add(current)
       
        for loc1, loc2 in distances:
            if loc1 == current and loc2 not in visited:
                if dfs(loc2):
                    return True
        return False
    
    return dfs(location1)

@app.post("/transfer_waste/")
def transfer_waste(request: TransferWasteRequest):
    logger.debug(f"Запрос на передачу отходов: {request.organization_name}, {request.waste_type}")

    # Поиск организации по имени
    organization = next((org for org in organizations if org.name == request.organization_name), None)
    if not organization:
        logger.error(f"Организация с именем '{request.organization_name}' не найдена.")
        raise HTTPException(status_code=404, detail="Организация не найдена")

    # Получаем количество отходов, которые организация хочет передать
    waste_to_transfer = organization.waste.get(request.waste_type, 0)
    if waste_to_transfer == 0:
        logger.warning(f"Организация '{organization.name}' не имеет отходов для передачи типа '{request.waste_type}'.")
        raise HTTPException(status_code=400, detail="У организации нет отходов для передачи")

    logger.info(f"Количество отходов для передачи: {waste_to_transfer}")

    # Фильтрация хранилищ, которые могут принимать этот тип отходов
    available_storages = [s for s in storages if request.waste_type in s.accepts]
    logger.debug(f"Доступные хранилища для типа отходов '{request.waste_type}': {len(available_storages)}")

    if not available_storages:
        logger.warning(f"Нет доступных хранилищ для типа отходов '{request.waste_type}'.")
        raise HTTPException(status_code=404, detail="Нет доступных хранилищ для этого типа отходов")

    # Сортировка хранилищ по расстоянию от организации
    available_storages.sort(key=lambda s: get_distance(organization.location, s.location))

    transferred_waste = 0  # Количество переданных отходов

    for storage in available_storages:
        # Проверяем, есть ли путь от организации до хранилища
        if not get_route_exists(organization.location, storage.location, get_distance):
            logger.debug(f"Нет пути от организации '{organization.name}' до хранилища '{storage.name}'. Пропускаем это хранилище.")
            continue

        # Проверяем, есть ли место в хранилище для данного типа отходов
        available_space = storage.capacity[request.waste_type] - storage.current_stock[request.waste_type]
        logger.debug(f"Хранилище '{storage.name}' имеет {available_space} доступных мест для типа отходов '{request.waste_type}'.")

        if available_space > 0:  # Если есть место в хранилище для этого типа отходов
            # Передаем отходы в это хранилище
            transfer_amount = min(waste_to_transfer, available_space)
            storage.current_stock[request.waste_type] += transfer_amount
            organization.waste[request.waste_type] -= transfer_amount
            transferred_waste += transfer_amount

            logger.info(f"Передаем {transfer_amount} единиц отходов в хранилище '{storage.name}'.")
            logger.info(f"После передачи, хранилище '{storage.name}' содержит {storage.current_stock[request.waste_type]} единиц отходов типа '{request.waste_type}'.")
            logger.info(f"Организация '{organization.name}' теперь имеет {organization.waste[request.waste_type]} единиц отходов типа '{request.waste_type}'.")
            
            # Обновляем оставшееся количество отходов для передачи
            waste_to_transfer -= transfer_amount

            if waste_to_transfer == 0:
                # Если отходы переданы полностью, выходим
                break

    # Если остались отходы для передачи, выводим предупреждение
    if waste_to_transfer > 0:
        logger.warning(f"Не удалось передать все отходы. Осталось {waste_to_transfer} единиц.")
        raise HTTPException(status_code=400, detail=f"Не удалось передать все отходы. Осталось {waste_to_transfer} единиц.")

    return {"message": f"{transferred_waste} единиц отходов передано в хранилища."}