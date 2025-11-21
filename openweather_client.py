# openweather_client.py

import os
import requests
from dotenv import load_dotenv

load_dotenv()

OPENWEATHER_KEY = os.getenv("OPENWEATHER_KEY")

if not OPENWEATHER_KEY:
    raise RuntimeError("OPENWEATHER_KEY não encontrado. Defina no .env ou nas variáveis de ambiente.")

BASE_WEATHER_URL = "https://api.openweathermap.org/data/2.5"
BASE_GEO_URL = "http://api.openweathermap.org/geo/1.0"


# -----------------------------------------------------------
# 1) Mapa de Estados -> Capitais (caso queira evitar Geocoding)
# -----------------------------------------------------------
BRAZIL_STATE_CAPITALS = {
    "AC": "Rio Branco",
    "AL": "Maceió",
    "AP": "Macapá",
    "AM": "Manaus",
    "BA": "Salvador",
    "CE": "Fortaleza",
    "DF": "Brasília",
    "ES": "Vitória",
    "GO": "Goiânia",
    "MA": "São Luís",
    "MT": "Cuiabá",
    "MS": "Campo Grande",
    "MG": "Belo Horizonte",
    "PA": "Belém",
    "PB": "João Pessoa",
    "PR": "Curitiba",
    "PE": "Recife",
    "PI": "Teresina",
    "RJ": "Rio de Janeiro",
    "RN": "Natal",
    "RS": "Porto Alegre",
    "RO": "Porto Velho",
    "RR": "Boa Vista",
    "SC": "Florianópolis",
    "SP": "São Paulo",
    "SE": "Aracaju",
    "TO": "Palmas",
}


def get_capital_for_state(uf: str) -> str:
    uf = uf.upper()
    if uf not in BRAZIL_STATE_CAPITALS:
        raise ValueError(f"UF inválida: {uf}")
    return BRAZIL_STATE_CAPITALS[uf]


# -----------------------------------------------------------
# 2) Geocoding – usando a API da OpenWeather (opcional, robusto)
# -----------------------------------------------------------
def geocode_city(city_name: str, country_code: str = "BR"):
    """
    Retorna (lat, lon) da cidade usando a Geocoding API da OpenWeather.
    """
    params = {
        "q": f"{city_name},{country_code}",
        "limit": 1,
        "appid": OPENWEATHER_KEY,
    }
    resp = requests.get(f"{BASE_GEO_URL}/direct", params=params, timeout=10)
    resp.raise_for_status()
    data = resp.json()

    if not data:
        raise ValueError(f"Não foi possível geocodificar {city_name}, {country_code}")

    item = data[0]
    return item["lat"], item["lon"]


# -----------------------------------------------------------
# 3) Current Weather
# -----------------------------------------------------------
def get_current_weather(lat: float, lon: float, units: str = "metric"):
    params = {
        "lat": lat,
        "lon": lon,
        "appid": OPENWEATHER_KEY,
        "units": units,
        "lang": "pt_br",
    }
    resp = requests.get(f"{BASE_WEATHER_URL}/weather", params=params, timeout=10)
    resp.raise_for_status()
    return resp.json()


# -----------------------------------------------------------
# 4) 5-day / 3-hour Forecast
# -----------------------------------------------------------
def get_forecast(lat: float, lon: float, units: str = "metric"):
    params = {
        "lat": lat,
        "lon": lon,
        "appid": OPENWEATHER_KEY,
        "units": units,
        "lang": "pt_br",
    }
    resp = requests.get(f"{BASE_WEATHER_URL}/forecast", params=params, timeout=10)
    resp.raise_for_status()
    return resp.json()


# -----------------------------------------------------------
# 5) Air Pollution
# -----------------------------------------------------------
def get_air_quality(lat: float, lon: float):
    params = {
        "lat": lat,
        "lon": lon,
        "appid": OPENWEATHER_KEY,
    }
    resp = requests.get(f"{BASE_WEATHER_URL}/air_pollution", params=params, timeout=10)
    resp.raise_for_status()
    return resp.json()
