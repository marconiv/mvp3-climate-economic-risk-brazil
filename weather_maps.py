# weather_maps.py

import math
import io
from typing import Optional, Dict
import requests
from PIL import Image

from openweather_client import OPENWEATHER_KEY


def _latlon_to_tile(lat: float, lon: float, zoom: int):
    """
    Converte latitude/longitude para coordenadas de tile (x, y) em um dado zoom.
    Fórmula padrão de web mercator / slippy maps.
    """
    lat_rad = math.radians(lat)
    n = 2.0 ** zoom
    xtile = int((lon + 180.0) / 360.0 * n)
    ytile = int((1.0 - math.log(math.tan(lat_rad) + 1 / math.cos(lat_rad)) / math.pi) / 2.0 * n)
    return xtile, ytile


def get_weather_map_tile(lat: float, lon: float, layer: str, zoom: int = 5) -> Optional[Image.Image]:
    """
    Retorna um tile de mapa da OpenWeather (como PIL.Image) para a camada especificada.

    Camadas comuns:
      - "clouds_new"
      - "precipitation_new"
      - "temp_new"
      - "pressure_new"
      - "wind_new"
    """
    x, y = _latlon_to_tile(lat, lon, zoom)
    url = f"https://tile.openweathermap.org/map/{layer}/{zoom}/{x}/{y}.png?appid={OPENWEATHER_KEY}"

    resp = requests.get(url, timeout=10)
    resp.raise_for_status()

    img = Image.open(io.BytesIO(resp.content))
    return img


def get_basic_weather_maps(lat: float, lon: float) -> Dict[str, Image.Image]:
    """
    Retorna um pequeno conjunto de mapas básicos para o MVP:
    - Precipitação
    - Temperatura
    - Nuvens
    """
    layers = {
        "Precipitação": "precipitation_new",
        "Temperatura": "temp_new",
        "Nuvens": "clouds_new",
    }

    images = {}
    for label, layer in layers.items():
        try:
            images[label] = get_weather_map_tile(lat, lon, layer)
        except Exception:
            images[label] = None

    return images
