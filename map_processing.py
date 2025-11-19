from enum import StrEnum
from model.ml_process import model_staff
from clients.map_manager import get_world_coord
from clients.map_manager import get_url
from clients.rosreestr import return_answer


class State(StrEnum):
    NEW = "new"
    FOUND = "found"
    CHECKED = "checked"


def render_garage_data(state: State,  center_coords: list) -> dict:
    """Получение данных для таблицы в зависимости от состояния"""
    image_url = get_url(center_coords)
    
    garages_coords_list = model_staff(image_url)
    if not garages_coords_list:
        return None
    
    garage_coords = []
    
    for coords in garages_coords_list:
        map_coord = get_world_coord(coords, center_coords)
        garage_coords.append(map_coord)
    
    if state == State.FOUND:
        return {
            "Координаты": garage_coords,
            "Легальность": ["?"]*len(garage_coords),
        }
    elif state == State.CHECKED:
        return {
            "Координаты": garage_coords,
            #"Кад.номер": return_answer(garage_coords), 
            "Легальность": return_answer(garage_coords),
        }
    