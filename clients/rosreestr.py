import math
import requests


def lonlat_to_mercator(lon, lat):
    """
    Преобразуем:
    – всемирно распространённый WGS84 (lon, lat)
    – в формат Web Mercator (x, y)
    """
    x = lon * 20037508.34 / 180
    y = math.log(math.tan((90 + lat) * math.pi / 360)) / (math.pi / 180)
    y = y * 20037508.34 / 180
    return x, y


def get_property_by_coords(lat: float, lon: float) -> dict | None:
    """
    Получаем данные об объекте недвижимости по координатам через map.ru
    """
    x, y = lonlat_to_mercator(lon, lat) 

    url = "https://map.ru/api/wms"
    params = {
        "x": x,
        "y": y,
        "layers": "36048",
    }
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Referer": "https://map.ru/pkk",
        "Accept": "application/json",
    }

    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        if response.status_code == 200:
            data = response.json()
            if data.get("features"):
                feat = data["features"][0]
                props = feat["properties"]
                opts = props.get("options", {})

                return {
                    "cadastral_number": opts.get("cad_num") or props.get("externalKey"),
                    "address": opts.get("readable_address"),
                    "status": opts.get("status"),
                    "registered": bool(opts.get("cad_num")),
                }

    except Exception as e:
        print(f"Ошибка запроса к map.ru: {e}")

    return None

def return_answer(coords: str):
    results = []
    for coord in coords:
        lat, lon = [round(float(x), 6) for x in coord.split(', ')]
        print(lat, lon)
        res = get_property_by_coords(lat, lon)
        if not res:
            results.append('No data')
        else:
            results.append(res['cadastral_number'])
        
    print(results)
    return results