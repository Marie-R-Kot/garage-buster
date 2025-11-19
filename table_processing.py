from enum import StrEnum

class State(StrEnum):
    NEW = "new"
    FOUND = "found"
    CHECKED = "checked"


def render_garage_data(state: State,  garage_coords: list, reestr_answers: list = None) -> dict:
    """Получение данных для таблицы в зависимости от состояния"""

    if state == State.FOUND:
        return {
            "Координаты": garage_coords,
            "Лег-ность": ["?"]*len(garage_coords),
        }
    
    elif state == State.CHECKED:
        property_states = []
        for answer in reestr_answers:
            if answer == 'Нет данных':
                property_states.append('✗')
            else:
                property_states.append('✓')
    
        return {
                "Координаты": garage_coords,
                "Кад.номер": reestr_answers, 
                "Лег-ность": property_states
            }
    