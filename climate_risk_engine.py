# climate_risk_engine.py

from typing import Dict, Any
import numpy as np
import pandas as pd


def _scale(value: float, min_val: float, max_val: float) -> float:
    if value is None:
        return 0.0
    if value <= min_val:
        return 0.0
    if value >= max_val:
        return 1.0
    return (value - min_val) / (max_val - min_val)


def compute_climate_risk(
    current_weather: Dict[str, Any],
    forecast: Dict[str, Any],
    air_quality: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Calcula risco climático puro (sem camada socioeconômica).

    Dimensões consideradas:
    - Calor (temperatura máxima prevista)
    - Chuva / Enchentes (chuva acumulada + número de janelas com chuva forte)
    - Vento (vento máximo previsto)
    - Qualidade do Ar (AQI)
    """

    # ---------------- SNAPSHOT ATUAL ----------------
    temp = float(current_weather["main"]["temp"])
    humidity = float(current_weather["main"]["humidity"])
    wind = float(current_weather["wind"]["speed"])
    rain_now = float(current_weather.get("rain", {}).get("1h", 0.0) or 0.0)

    # ---------------- PREVISÃO 5 DIAS ----------------
    fc_list = forecast.get("list", [])
    df_fc = pd.DataFrame(
        [
            {
                "dt_txt": item["dt_txt"],
                "temp": item["main"]["temp"],
                "rain_3h": item.get("rain", {}).get("3h", 0.0) or 0.0,
                "wind": item["wind"]["speed"],
            }
            for item in fc_list
        ]
    )

    if not df_fc.empty:
        temp_max_forecast = float(df_fc["temp"].max())
        rain_sum_forecast = float(df_fc["rain_3h"].sum())
        wind_max_forecast = float(df_fc["wind"].max())
        # número de janelas com chuva forte (>= 10 mm / 3h)
        heavy_rain_hours = int((df_fc["rain_3h"] >= 10.0).sum())
    else:
        temp_max_forecast = temp
        rain_sum_forecast = rain_now
        wind_max_forecast = wind
        heavy_rain_hours = 0

    # ---------------- QUALIDADE DO AR ----------------
    try:
        # AQI 1 (bom) a 5 (muito ruim)
        aqi = int(air_quality["list"][0]["main"]["aqi"])
    except Exception:
        aqi = 1

    # ---------------- NORMALIZAÇÕES ----------------
    # Faixas heurísticas adaptadas ao contexto brasileiro

    # Calor: risco alto quando T_max >= 30–40°C
    heat_risk = _scale(temp_max_forecast, 30.0, 40.0)

    # Chuva: combinação de volume total + número de janelas de chuva forte
    # chuva acumulada em 5 dias — 0 a 200 mm
    rain_component_amount = _scale(rain_sum_forecast, 0.0, 200.0)
    # janelas com chuva forte (>= 10 mm / 3h) — 0 a 10
    rain_component_heavy = _scale(heavy_rain_hours, 0.0, 10.0)
    rain_risk = 0.6 * rain_component_amount + 0.4 * rain_component_heavy

    # Vento: risco cresce acima de ~5 m/s, muito alto acima de 25 m/s
    wind_risk = _scale(wind_max_forecast, 5.0, 25.0)

    # AQI: 1 (bom) a 5 (muito ruim)
    air_risk = _scale(float(aqi), 1.0, 5.0)

    # ---------------- PESOS GLOBAIS ----------------
    # Damos mais peso para CHUVA/ENCHENTES para capturar melhor casos como RS
    weights = {
        "heat": 0.25,
        "rain": 0.40,
        "wind": 0.20,
        "air": 0.15,
    }

    overall = (
        heat_risk * weights["heat"]
        + rain_risk * weights["rain"]
        + wind_risk * weights["wind"]
        + air_risk * weights["air"]
    )
    score = float(np.round(overall * 100.0, 1))

    def categorize(s: float) -> str:
        if s < 25:
            return "Baixo"
        if s < 50:
            return "Moderado"
        if s < 75:
            return "Alto"
        return "Crítico"

    dimensions = {
        "Calor": float(np.round(heat_risk * 100.0, 1)),
        "Chuva / Enchentes": float(np.round(rain_risk * 100.0, 1)),
        "Vento": float(np.round(wind_risk * 100.0, 1)),
        "Qualidade do Ar": float(np.round(air_risk * 100.0, 1)),
    }

    forecast_summary = {
        "temp_max_forecast": temp_max_forecast,
        "rain_sum_forecast": rain_sum_forecast,
        "wind_max_forecast": wind_max_forecast,
        "heavy_rain_hours": heavy_rain_hours,
    }

    snapshot = {
        "temp": temp,
        "humidity": humidity,
        "wind": wind,
        "rain_1h": rain_now,
    }

    return {
        "score": score,
        "category": categorize(score),
        "dimensions": dimensions,
        "snapshot": snapshot,
        "forecast_df": df_fc,
        "forecast_summary": forecast_summary,
    }
