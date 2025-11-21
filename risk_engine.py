# climate_risk_engine.py

from typing import Dict, Any
import numpy as np
import pandas as pd


def _scale(value, min_val, max_val):
    if value is None:
        return 0.0
    if value <= min_val:
        return 0.0
    if value >= max_val:
        return 1.0
    return (value - min_val) / (max_val - min_val)


def compute_climate_risk(current_weather: Dict[str, Any],
                         forecast: Dict[str, Any],
                         air_quality: Dict[str, Any]) -> Dict[str, Any]:
    """
    Calcula risco climático puro (sem camada socioeconômica).

    Racional v2:
      - Chuva acumulada em 5 dias + horas com chuva forte -> peso mais alto
      - Calor extremo (temp. máxima da previsão)
      - Vento máximo
      - Qualidade do ar (AQI da OpenWeather)
    """

    # Snapshot atual
    temp = current_weather["main"]["temp"]
    humidity = current_weather["main"]["humidity"]
    wind = current_weather["wind"]["speed"]
    rain_now = current_weather.get("rain", {}).get("1h", 0.0)

    # Previsão 5 dias / 3 em 3 horas
    fc_list = forecast.get("list", [])
    df_fc = pd.DataFrame([
        {
            "dt_txt": item["dt_txt"],
            "temp": item["main"]["temp"],
            "rain_3h": item.get("rain", {}).get("3h", 0.0),
            "wind": item["wind"]["speed"],
        }
        for item in fc_list
    ])

    if not df_fc.empty:
        temp_max_forecast = df_fc["temp"].max()
        rain_sum_forecast = df_fc["rain_3h"].sum()
        wind_max_forecast = df_fc["wind"].max()
        heavy_rain_hours = (df_fc["rain_3h"] >= 10.0).sum()  # janelas com chuva forte
    else:
        temp_max_forecast = temp
        rain_sum_forecast = rain_now
        wind_max_forecast = wind
        heavy_rain_hours = 0

    # AQI (1–5)
    try:
        aqi = air_quality["list"][0]["main"]["aqi"]
    except Exception:
        aqi = 1

    # Normalizações (heurísticas pensadas para clima BR)
    heat_risk = _scale(temp_max_forecast, 22, 38)          # calor passa a contar acima de 22°C até ~38°C
    rain_base = _scale(rain_sum_forecast, 0, 150)          # chuva acumulada 0–150 mm
    rain_heavy = _scale(heavy_rain_hours, 0, 8)            # até ~8 janelas de chuva forte
    rain_risk = 0.7 * rain_base + 0.3 * rain_heavy         # chuva + intensidade
    wind_risk = _scale(wind_max_forecast, 5, 22)           # vento forte aumenta risco
    air_risk = _scale(aqi, 1, 5)                           # AQI 1–5

    # Pesos do índice climático global
    weights = {
        "heat": 0.25,
        "rain": 0.40,
        "wind": 0.15,
        "air": 0.20,
    }

    overall = (
        heat_risk * weights["heat"] +
        rain_risk * weights["rain"] +
        wind_risk * weights["wind"] +
        air_risk * weights["air"]
    )

    score = float(np.round(overall * 100, 1))

    def categorize(s: float) -> str:
        if s < 25:
            return "Baixo"
        if s < 50:
            return "Moderado"
        if s < 75:
            return "Alto"
        return "Crítico"

    return {
        "score": score,
        "category": categorize(score),
        "dimensions": {
            "Calor": float(np.round(heat_risk * 100, 1)),
            "Chuva / Enchentes": float(np.round(rain_risk * 100, 1)),
            "Vento": float(np.round(wind_risk * 100, 1)),
            "Qualidade do Ar": float(np.round(air_risk * 100, 1)),
        },
        "snapshot": {
            "temp": temp,
            "humidity": humidity,
            "wind": wind,
            "rain_1h": rain_now,
        },
        "forecast_df": df_fc,
        "forecast_summary": {
            "temp_max_forecast": temp_max_forecast,
            "rain_sum_forecast": rain_sum_forecast,
            "wind_max_forecast": wind_max_forecast,
            "heavy_rain_hours": int(heavy_rain_hours),
        },
    }
