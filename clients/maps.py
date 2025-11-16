import requests
import streamlit as st


def get_coords_by_address(address: str) -> list:
    """
    Получаем координаты по адресу через OpenStreetMap
    """
    base_url = "https://nominatim.openstreetmap.org/search"

    params = {"q": address, "format": "json", "limit": 1, "accept-language": "ru"}

    headers = {"User-Agent": "StreamlitApp/1.0"}

    response = requests.get(base_url, params=params, headers=headers, timeout=10)
    response.raise_for_status()

    data = response.json()

    first_result = data[0]
    lat = float(first_result["lat"])
    lon = float(first_result["lon"])

    return f"{lat},{lon}"


def get_static_map_url(lat: float, lon: float) -> str:
    return (
        f"https://tile.thunderforest.com/static/cycle/{lon},{lat},18/2048x2048.png"
        f"?apikey={st.secrets['STATICMAPS_API_KEY']}"
    )
