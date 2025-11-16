from enum import StrEnum


class State(StrEnum):
    NEW = "new"
    FOUND = "found"
    CHECKED = "checked"


def render_garage_data(state: State, coords: str) -> dict:
    """Получение данных для таблицы в зависимости от состояния"""
    if state == State.FOUND:
        return {
            "Координаты": [coords, coords],
            "Легальность": ["?", "?"],
        }
    elif state == State.CHECKED:
        return {
            "Координаты": [coords, coords],
            "Легальность": ["Легален", "Нелегален"],
        }
    return None
