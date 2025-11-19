from enum import StrEnum

class State(StrEnum):
    NEW = "new"
    FOUND = "found"
    CHECKED = "checked"

# def get_coords_from_model(center_coords):
#     image_url = get_url(center_coords)
    
#     garages_coords_list = model_staff(image_url)
#     if not garages_coords_list:
#         return None
    
#     garage_coords = []
    
#     for coords in garages_coords_list:
#         map_coord = get_world_coord(coords, center_coords)
#         garage_coords.append(map_coord)
    
#     return garage_coords


def render_garage_data(state: State,  garage_coords: list, reestr_answers: list = None) -> dict:
    """Получение данных для таблицы в зависимости от состояния"""

    if state == State.FOUND:
        return {
            "Координаты": garage_coords,
            "Легальность": ["?"]*len(garage_coords),
        }
    elif state == State.CHECKED:
        return {
            "Координаты": garage_coords,
            #"Кад.номер": return_answer(garage_coords), 
            "Легальность": reestr_answers,
        }
    