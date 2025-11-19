import requests
import math


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

def get_url(coords: list) -> str:
    lat, lon = coords[0], coords[1]
    return f"https://static.maps.2gis.com/1.0?s=1280x1280@2x&z=17&c={lat},{lon}"

def lat_lon_to_pixel(lat, lon, zoom):
    """
    Преобразует lat/lon в глобальные пиксельные координаты Web Mercator.
    Возвращает (x, y) в пикселях на уровне zoom.
    """
    n = 2.0 ** zoom
    tile_size = 256  # стандартный размер тайла, но у вас 2048 = 256 * 8 → zoom_offset = 3
    scale = tile_size * n  # общее число пикселей по оси на данном zoom

    x = (lon + 180.0) / 360.0 * scale
    lat_rad = math.radians(lat)
    y = (1.0 - math.log(math.tan(lat_rad) + 1.0 / math.cos(lat_rad)) / math.pi) / 2.0 * scale
    return x, y

def pixel_to_lat_lon(x, y, zoom):
    """
    Обратное преобразование: пиксели → lat/lon
    """
    n = 2.0 ** zoom
    tile_size = 256
    scale = tile_size * n

    lon = x / scale * 360.0 - 180.0
    lat_rad = math.atan(math.sinh(math.pi * (1 - 2 * y / scale)))
    lat = math.degrees(lat_rad)
    return lat, lon

def get_world_coord(rel_coord: list, world_center_coord: list, zoom=17, tile_size=2048):
    """
    Переводит относительные координаты внутри тайла (0..1) в lat/lon.
    rel_coord: [rel_x, rel_y], где (0,0) — верхний левый угол тайла.
    world_center_coord: [lat, lon] центра тайла.
    """
    # Глобальные пиксели центра тайла
    center_x, center_y = lat_lon_to_pixel(world_center_coord[0], world_center_coord[1], zoom)

    # Смещение от центра (в пикселях)
    dx = (rel_coord[0] - 0.5) * tile_size
    dy = (rel_coord[1] - 0.5) * tile_size

    # Абсолютные пиксели точки
    target_x = center_x + dx
    target_y = center_y + dy

    # Обратно в lat/lon
    lat, lon = pixel_to_lat_lon(target_x, target_y, zoom)
    return f"{round(lat, 6)}, {round(lon, 6)}"
