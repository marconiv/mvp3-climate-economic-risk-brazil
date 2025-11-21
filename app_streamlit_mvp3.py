# app_streamlit_mvp3.py

import streamlit as st
import pandas as pd
import altair as alt

from openweather_client import (
    get_capital_for_state,
    geocode_city,
    get_current_weather,
    get_forecast,
    get_air_quality,
)
from climate_risk_engine import compute_climate_risk
from socioecon_risk_engine import compute_socioecon_risk
from combined_risk_engine import combine_risks
from weather_maps import get_basic_weather_maps
from theme import inject_custom_css


# ---------------- CONFIG INICIAL ----------------
st.set_page_config(
    page_title="MVP3 – Plataforma Climatoeconômica InfoChoice",
    layout="wide",
)

inject_custom_css()

# ---------------- DICIONÁRIO DE IDIOMAS ----------------
TEXTS = {
    "pt": {
        "app_title": "MVP3 – Plataforma Climatoeconômica InfoChoice",
        "sidebar_title": "Configurações",
        "select_state": "Selecione o Estado (UF)",
        "sidebar_hint": "A **capital da UF** será usada como ponto de referência para consulta às APIs da **OpenWeather**.",
        "analyze_button": "Analisar Estado",
        "pre_run_info": "Selecione uma UF na barra lateral e clique em **Analisar Estado**.",
        "spinner_msg": "Consultando OpenWeather e calculando índices de risco...",
        "header_subtitle": (
            "Integração de <b>clima em tempo real</b>, <b>previsão</b> e "
            "<b>indicadores socioeconômicos</b> para estimar o risco "
            "<b>climatoeconômico</b> dos estados brasileiros."
        ),
        "climate_now_title": "Clima Atual",
        "current_temp_label": "Temperatura atual",
        "current_humidity": "Umidade",
        "current_wind": "Vento",
        "current_rain": "Chuva (últ. 1h)",
        "forecast_title": "Previsão – 5 dias (janela de 3 em 3 horas)",
        "forecast_summary_title": "Resumo da Previsão (agregada)",
        "fc_temp_max": "Temperatura máxima prevista (5 dias)",
        "fc_rain_sum": "Chuva acumulada (5 dias)",
        "fc_heavy_hours": "Janelas com chuva forte (≥ 10 mm/3h)",
        "fc_wind_max": "Vento máximo previsto (5 dias)",
        "forecast_no_data": "Não há dados de previsão disponíveis para este local.",
        "weather_maps_title": "Weather Maps – Camadas da OpenWeather",
        "weather_maps_sub": (
            "Visualização aproximada das camadas de <b>precipitação</b>, <b>temperatura</b> "
            "e <b>nuvens</b> centradas na capital selecionada, usando a API "
            "<i>Weather Maps</i> da OpenWeather."
        ),
        "weather_map_not_available": "Mapa não disponível para esta camada.",
        "climate_risk_title": "Índice de Risco Climático",
        "climate_score_label": "SCORE CLIMÁTICO (0–100)",
        "socio_risk_title": "Risco Socioeconômico (UF)",
        "socio_score_label": "SCORE SOCIOECONÔMICO (0–100)",
        "indicators_title": "Indicadores Socioeconômicos (último ano disponível)",
        "combined_risk_title": "Índice Climatoeconômico Integrado",
        "combined_score_label": "SCORE INTEGRADO (0–100)",
        "sector_risk_title": "Risco por Setor Econômico",
        "sector_subtitle": (
            "Distribuição aproximada da vulnerabilidade socioeconômica entre os principais "
            "setores da economia estadual."
        ),
        "dims_axis_y": "RISCO (%)",
        "dims_axis_x": "DIMENSÃO",
        "sector_axis_y": "RISCO (%)",
        "sector_axis_x": "SETOR",
        "model_rationale_title": "Model Rationale (v0 – Heuristic with AI)",
        "method_note_title": "Nota Metodológica",
    },
    "en": {
        "app_title": "MVP3 – Climate-Economic Risk Dashboard (Brazil)",
        "sidebar_title": "Settings",
        "select_state": "Select State (UF)",
        "sidebar_hint": "The state's **capital city** is used as reference point for OpenWeather API calls.",
        "analyze_button": "Analyze State",
        "pre_run_info": "Select a state on the sidebar and click **Analyze State**.",
        "spinner_msg": "Querying OpenWeather and computing risk indices...",
        "header_subtitle": (
            "Integration of <b>real-time weather</b>, <b>forecast</b> and "
            "<b>socioeconomic indicators</b> to estimate the "
            "<b>climate-economic risk</b> of Brazilian states."
        ),
        "climate_now_title": "Current Weather",
        "current_temp_label": "Current temperature",
        "current_humidity": "Humidity",
        "current_wind": "Wind",
        "current_rain": "Rain (last 1h)",
        "forecast_title": "Forecast – 5 days (3-hour steps)",
        "forecast_summary_title": "Forecast Summary (aggregated)",
        "fc_temp_max": "Maximum forecast temperature (5 days)",
        "fc_rain_sum": "Total rainfall (5 days)",
        "fc_heavy_hours": "Strong rain windows (≥ 10 mm/3h)",
        "fc_wind_max": "Maximum forecast wind (5 days)",
        "forecast_no_data": "No forecast data available for this location.",
        "weather_maps_title": "Weather Maps – OpenWeather Layers",
        "weather_maps_sub": (
            "Approximate visualization of <b>precipitation</b>, <b>temperature</b> and "
            "<b>cloud</b> layers centered on the selected capital, using OpenWeather "
            "<i>Weather Maps</i> API."
        ),
        "weather_map_not_available": "Map not available for this layer.",
        "climate_risk_title": "Climate Risk Index",
        "climate_score_label": "CLIMATE SCORE (0–100)",
        "socio_risk_title": "Socioeconomic Risk (State)",
        "socio_score_label": "SOCIOECONOMIC SCORE (0–100)",
        "indicators_title": "Socioeconomic Indicators (latest available year)",
        "combined_risk_title": "Integrated Climate-Economic Index",
        "combined_score_label": "INTEGRATED SCORE (0–100)",
        "sector_risk_title": "Risk by Economic Sector",
        "sector_subtitle": (
            "Approximate distribution of socioeconomic vulnerability across the main "
            "economic sectors of the state."
        ),
        "dims_axis_y": "RISK (%)",
        "dims_axis_x": "DIMENSION",
        "sector_axis_y": "RISK (%)",
        "sector_axis_x": "SECTOR",
        "model_rationale_title": "Model Rationale (v0 – Heuristic with AI)",
        "method_note_title": "Methodological Note",
    },
}

if "lang" not in st.session_state:
    st.session_state["lang"] = "pt"

lang = st.session_state["lang"]


def T(key: str) -> str:
    return TEXTS.get(lang, TEXTS["pt"]).get(key, TEXTS["pt"].get(key, key))


# ---------------- SIDEBAR ----------------
lang_col1, lang_col2 = st.sidebar.columns(2)
if lang_col1.button("🇧🇷 PT"):
    st.session_state["lang"] = "pt"
    lang = "pt"
if lang_col2.button("🇺🇸 EN"):
    st.session_state["lang"] = "en"
    lang = "en"

st.sidebar.title(T("sidebar_title"))

UF_OPTIONS = [
    "AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO",
    "MA", "MT", "MS", "MG", "PA", "PB", "PR", "PE", "PI",
    "RJ", "RN", "RS", "RO", "RR", "SC", "SP", "SE", "TO",
]

uf = st.sidebar.selectbox(T("select_state"), UF_OPTIONS, index=UF_OPTIONS.index("MG"))
st.sidebar.markdown(T("sidebar_hint"))

run_analysis = st.sidebar.button(T("analyze_button"), type="primary")

# ---------------- HEADER ----------------
st.markdown(
    f"""
    <div class="card">
      <div class="card-header">
        🌍 {T("app_title")}
      </div>
      <div class="card-subtitle">
        {T("header_subtitle")}
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

if not run_analysis:
    st.info(T("pre_run_info"))
    st.stop()

# ---------------- PIPELINE PRINCIPAL ----------------
with st.spinner(T("spinner_msg")):
    try:
        capital = get_capital_for_state(uf)
        lat, lon = geocode_city(capital, "BR")

        current = get_current_weather(lat, lon)
        forecast = get_forecast(lat, lon)
        air = get_air_quality(lat, lon)

        climate_risk = compute_climate_risk(current, forecast, air)
        socio_risk = compute_socioecon_risk(uf)
        combined_risk = combine_risks(climate_risk, socio_risk)

        weather_maps = get_basic_weather_maps(lat, lon)

    except Exception as e:
        st.error(f"Erro ao obter dados ou calcular risco: {e}")
        st.stop()

# ---------------- PAINEL 1 – CLIMA ATUAL ----------------
snapshot = climate_risk["snapshot"]

st.markdown(
    f"""
    <div class="card">
      <div class="card-header">
        ☁️ {T("climate_now_title")} – {capital} / {uf}
      </div>
      <div style="display:flex; gap:40px; flex-wrap:wrap;">
        <div>
          <div class="big-metric">{snapshot['temp']:.1f}°C</div>
          <div class="big-metric-label">{T("current_temp_label")}</div>
        </div>
        <div>
          <div><b>{T("current_humidity")}:</b> {snapshot['humidity']:.0f}%</div>
          <div><b>{T("current_wind")}:</b> {snapshot['wind']:.1f} m/s</div>
          <div><b>{T("current_rain")}:</b> {snapshot['rain_1h']:.1f} mm</div>
        </div>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ---------------- PAINEL 2 – PREVISÃO ----------------
st.markdown(
    f"""
    <div class="card">
      <div class="card-header">
        📅 {T("forecast_title")}
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

df_fc = climate_risk["forecast_df"]
if not df_fc.empty:
    # ---- TABELA DE PREVISÃO ----
    table_cols = {
        "dt_txt": "Data/Hora" if lang == "pt" else "Date/Time",
        "temp": "Temperatura (°C)" if lang == "pt" else "Temperature (°C)",
        "rain_3h": "Chuva 3h (mm)" if lang == "pt" else "Rain 3h (mm)",
        "wind": "Vento (m/s)" if lang == "pt" else "Wind (m/s)",
    }
    df_fc_viz = df_fc.rename(columns=table_cols)
    st.dataframe(df_fc_viz.head(16), use_container_width=True)

    # ---- GRÁFICO ALTair – TEMPERATURA + CHUVA ----
    df_fc_alt = df_fc.copy()
    df_fc_alt["dt"] = pd.to_datetime(df_fc_alt["dt_txt"])

    x_title = "DATA/HORA" if lang == "pt" else "DATE/TIME"
    y_temp_title = "TEMPERATURA (°C)" if lang == "pt" else "TEMPERATURE (°C)"
    y_rain_title = "CHUVA 3H (mm)" if lang == "pt" else "RAIN 3H (mm)"

    base_chart = alt.Chart(df_fc_alt)

    temp_line = (
        base_chart
        .mark_line()
        .encode(
            x=alt.X(
                "dt:T",
                title=x_title,
            ),
            y=alt.Y(
                "temp:Q",
                axis=alt.Axis(title=y_temp_title),
            ),
            tooltip=[
                alt.Tooltip("dt:T", title=x_title),
                alt.Tooltip("temp:Q", title=y_temp_title, format=".1f"),
                alt.Tooltip("rain_3h:Q", title=y_rain_title, format=".1f"),
            ],
        )
    )

    rain_line = (
        base_chart
        .mark_line(strokeDash=[4, 2])
        .encode(
            x=alt.X(
                "dt:T",
                title=x_title,
            ),
            y=alt.Y(
                "rain_3h:Q",
                axis=alt.Axis(title=y_rain_title),
            ),
            color=alt.value("#ff7f0e"),
            tooltip=[
                alt.Tooltip("dt:T", title=x_title),
                alt.Tooltip("rain_3h:Q", title=y_rain_title, format=".1f"),
            ],
        )
    )

    chart_fc = (
        alt.layer(temp_line, rain_line)
        .resolve_scale(y="independent")
        .properties(
            height=260,
            background="#000000",
        )
        .configure_axis(
            labelColor="#FFFFFF",
            titleColor="#FFFFFF",
            labelFontSize=11,
            titleFontSize=12,
            labelFontWeight="bold",
            titleFontWeight="bold",
            gridColor="#333333",
        )
        .configure_view(
            stroke="#1A1A1A",
            strokeWidth=1,
        )
    )

    st.altair_chart(chart_fc, use_container_width=True)

    fc_summary = climate_risk["forecast_summary"]
    st.markdown(
        f"""
        <div class="card">
          <div class="card-header">📌 {T("forecast_summary_title")}</div>
          <ul>
            <li><b>{T("fc_temp_max")}:</b> {fc_summary['temp_max_forecast']:.1f} °C</li>
            <li><b>{T("fc_rain_sum")}:</b> {fc_summary['rain_sum_forecast']:.1f} mm</li>
            <li><b>{T("fc_heavy_hours")}:</b> {fc_summary['heavy_rain_hours']}</li>
            <li><b>{T("fc_wind_max")}:</b> {fc_summary['wind_max_forecast']:.1f} m/s</li>
          </ul>
        </div>
        """,
        unsafe_allow_html=True,
    )
else:
    st.info(T("forecast_no_data"))

# ---------------- PAINEL 2b – WEATHER MAPS ----------------
st.markdown(
    f"""
    <div class="card">
      <div class="card-header">
        🗺️ {T("weather_maps_title")}
      </div>
      <div class="card-subtitle">
        {T("weather_maps_sub")}
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

cols_maps = st.columns(3)
map_labels = list(weather_maps.keys())
for col, label in zip(cols_maps, map_labels):
    lbl = label
    if lang == "en":
        if label.lower().startswith("precip"):
            lbl = "Precipitation"
        elif label.lower().startswith("temper"):
            lbl = "Temperature"
        elif label.lower().startswith("nuv"):
            lbl = "Clouds"
    else:
        if label.lower().startswith("precip"):
            lbl = "Precipitação"
        elif label.lower().startswith("temper"):
            lbl = "Temperatura"
        elif label.lower().startswith("cloud"):
            lbl = "Nuvens"

    img = weather_maps[label]
    with col:
        st.markdown(f"**{lbl}**")
        if img is not None:
            st.image(img, use_container_width=True)
        else:
            st.info(T("weather_map_not_available"))


# ---------------- FUNÇÃO AUXILIAR – badge de risco ----------------
def risk_badge_html(category: str, label: str = "Nível"):
    cls = "risk-med"
    cat_lower = category.lower()
    if cat_lower.startswith("baixo") or "low" in cat_lower:
        cls = "risk-low"
    elif cat_lower.startswith("moderado") or "moderat" in cat_lower:
        cls = "risk-med"
    elif cat_lower.startswith("alto") or "high" in cat_lower:
        cls = "risk-high"
    elif cat_lower.startswith("crít") or "very high" in cat_lower:
        cls = "risk-critical"
    return f'<span class="risk-badge {cls}">{label}: {category}</span>'


# ---------------- PAINEL 3 – RISCO CLIMÁTICO ----------------
climate_score = climate_risk["score"]
climate_cat = climate_risk["category"]

st.markdown(
    f"""
    <div class="card">
      <div class="card-header">
        🔥 {T("climate_risk_title")}
        {risk_badge_html(climate_cat, "Clima" if lang == "pt" else "Climate")}
      </div>
      <div class="big-metric">{climate_score:.1f}</div>
      <div class="big-metric-label">{T("climate_score_label")}</div>
    </div>
    """,
    unsafe_allow_html=True,
)
st.progress(min(climate_score / 100.0, 1.0))

dims = climate_risk["dimensions"]
if lang == "pt":
    dim_names = {
        "Calor": "CALOR",
        "Chuva / Enchentes": "CHUVA / ENCHENTES",
        "Vento": "VENTO",
        "Qualidade do Ar": "QUALIDADE DO AR",
    }
else:
    dim_names = {
        "Calor": "HEAT",
        "Chuva / Enchentes": "RAIN / FLOODS",
        "Vento": "WIND",
        "Qualidade do Ar": "AIR QUALITY",
    }

dim_df = pd.DataFrame(
    {
        "Dimensão": [dim_names.get(k, k) for k in dims.keys()],
        "Risco (%)": list(dims.values()),
    }
)

dim_colors = {
    ("CALOR", "HEAT"): "#ff6b6b",
    ("CHUVA / ENCHENTES", "RAIN / FLOODS"): "#4dabf7",
    ("VENTO", "WIND"): "#74c0fc",
    ("QUALIDADE DO AR", "AIR QUALITY"): "#ffd43b",
}


def resolve_dim_color(dim_label: str) -> str:
    for (pt_label, en_label), color in dim_colors.items():
        if dim_label == pt_label or dim_label == en_label:
            return color
    return "#339af0"


dim_df["Cor"] = dim_df["Dimensão"].apply(resolve_dim_color)

chart_dims = (
    alt.Chart(dim_df)
    .mark_bar()
    .encode(
        x=alt.X(
            "Dimensão:N",
            sort=None,
            title=T("dims_axis_x"),
            axis=alt.Axis(
                labelAngle=0,
                labelFontWeight="bold",
                titleFontWeight="bold",
                labelColor="#FFFFFF",
                titleColor="#FFFFFF",
                labelFontSize=11,
                titleFontSize=12,
            ),
        ),
        y=alt.Y(
            "Risco (%):Q",
            scale=alt.Scale(domain=[0, 100]),
            title=T("dims_axis_y"),
            axis=alt.Axis(
                labelColor="#FFFFFF",
                titleColor="#FFFFFF",
                labelFontWeight="bold",
                titleFontSize=12,
                labelFontSize=11,
                titleFontWeight="bold",
            ),
        ),
        color=alt.Color("Cor:N", scale=None, legend=None),
        tooltip=["Dimensão", "Risco (%):Q"],
    )
    .properties(
        background="#000000",
    )
    .configure_view(
        stroke="#1A1A1A",
        strokeWidth=1,
    )
    .configure_axis(
        gridColor="#333333",
    )
)

st.altair_chart(chart_dims, use_container_width=True)

# ---------------- PAINEL 4 – RISCO SOCIOECONÔMICO ----------------
socio_score = socio_risk["score"]
socio_cat = socio_risk["category"]

st.markdown(
    f"""
    <div class="card">
      <div class="card-header">
        🏙️ {T("socio_risk_title")}
        {risk_badge_html(socio_cat, "Socioeconômico" if lang == "pt" else "Socioeconomic")}
      </div>
      <div class="big-metric">{socio_score:.1f}</div>
      <div class="big-metric-label">{T("socio_score_label")}</div>
    </div>
    """,
    unsafe_allow_html=True,
)
st.progress(min(socio_score / 100.0, 1.0))

# ----- CARD SIMPLES DE INDICADORES SOCIOECONÔMICOS -----
ind = socio_risk["indicators"]

label_gdp_pc = "PIB per capita (R$)" if lang == "pt" else "GDP per capita (R$)"
label_pop = "População" if lang == "pt" else "Population"
label_gdp_tot = "PIB total (mil R$)" if lang == "pt" else "Total GDP (thou. R$)"
label_density = "Densidade (hab/km²)" if lang == "pt" else "Density (inhab/km²)"

st.markdown(
    f"""
    <div class="card">
      <div class="card-header">
        📊 {T("indicators_title")}
      </div>
      <div class="mini-metric-grid">
        <div class="mini-metric">
          <div class="mini-metric-label">{label_gdp_pc}</div>
          <div class="mini-metric-value">{ind['PIB_per_capita']:,.0f}</div>
        </div>
        <div class="mini-metric">
          <div class="mini-metric-label">{label_pop}</div>
          <div class="mini-metric-value">{ind['Populacao']:,.0f}</div>
        </div>
        <div class="mini-metric">
          <div class="mini-metric-label">{label_gdp_tot}</div>
          <div class="mini-metric-value">{ind['PIB_mil_reais']:,.0f}</div>
        </div>
        <div class="mini-metric">
          <div class="mini-metric-label">{label_density}</div>
          <div class="mini-metric-value">{ind['Densidade_hab_km2']:.1f}</div>
        </div>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ---------------- PAINEL 5 – RISCO CLIMATOECONÔMICO COMBINADO ----------------
comb_score = combined_risk["score"]
comb_cat = combined_risk["category"]

if lang == "pt":
    comb_text = (
        f"O índice combina o risco climático (peso {combined_risk['weights']['climate']:.1f}) "
        f"com o risco socioeconômico (peso {combined_risk['weights']['socioecon']:.1f}), "
        "seguindo a visão metodológica do MVP3."
)

else:
    comb_text = (
        f"The index combines climate risk (weight {combined_risk['weights']['climate']:.1f}) "
        f"with socioeconomic risk (weight {combined_risk['weights']['socioecon']:.1f}), "
        "according to the MVP3 methodological design."
)


st.markdown(
    f"""
    <div class="card">
      <div class="card-header">
        🌐 {T("combined_risk_title")}
        {risk_badge_html(comb_cat, "Global")}
      </div>
      <div class="big-metric">{comb_score:.1f}</div>
      <div class="big-metric-label">{T("combined_score_label")}</div>
      <p style="margin-top:10px; font-size:0.9rem; opacity:0.85;">
        {comb_text}
      </p>
    </div>
    """,
    unsafe_allow_html=True,
)
st.progress(min(comb_score / 100.0, 1.0))

# ---------------- PAINEL 6 – RISCO POR SETOR ----------------
sector_risk = socio_risk["sector_risk"]

st.markdown(
    f"""
    <div class="card">
      <div class="card-header">
        🧩 {T("sector_risk_title")}
      </div>
      <div class="card-subtitle">
        {T("sector_subtitle")}
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

sector_df = pd.DataFrame(
    {
        "Setor": list(sector_risk.keys()),
        "Risco (%)": list(sector_risk.values()),
    }
)

sector_colors = {
    ("Agropecuária", "Agriculture"): "#69db7c",
    ("Indústria", "Industry"): "#4dabf7",
    ("Comércio", "Commerce"): "#ffd43b",
    ("Serviços", "Services"): "#ffa94d",
}


def resolve_sector_color(label: str) -> str:
    for (pt_label, en_label), color in sector_colors.items():
        if label == pt_label or label == en_label:
            return color
    return "#4dabf7"


sector_df["Cor"] = sector_df["Setor"].apply(resolve_sector_color)

chart_sector = (
    alt.Chart(sector_df)
    .mark_bar()
    .encode(
        x=alt.X(
            "Setor:N",
            sort=None,
            title=T("sector_axis_x"),
            axis=alt.Axis(
                labelAngle=0,
                labelFontWeight="bold",
                titleFontWeight="bold",
                labelColor="#FFFFFF",
                titleColor="#FFFFFF",
                labelFontSize=11,
                titleFontSize=12,
            ),
        ),
        y=alt.Y(
            "Risco (%):Q",
            scale=alt.Scale(domain=[0, 100]),
            title=T("sector_axis_y"),
            axis=alt.Axis(
                labelColor="#FFFFFF",
                titleColor="#FFFFFF",
                labelFontWeight="bold",
                titleFontWeight="bold",
                labelFontSize=11,
                titleFontSize=12,
            ),
        ),
        color=alt.Color("Cor:N", scale=None, legend=None),
        tooltip=["Setor", "Risco (%):Q"],
    )
    .properties(
        background="#000000",
    )
    .configure_view(
        stroke="#1A1A1A",
        strokeWidth=1,
    )
    .configure_axis(
        gridColor="#333333",
    )
)

st.altair_chart(chart_sector, use_container_width=True)

# ---------------- FUNÇÃO AUXILIAR – TEXTO DINÂMICO DO RACIONAL ----------------
def build_model_rationale_html(lang, uf, capital, climate_risk, socio_risk, combined_risk):
    """
    Gera um texto estruturado (parágrafos + lista) explicando:
      - Risco climático
      - Risco socioeconômico (ML)
      - Índice combinado
      - Principais interpretações
    com base nos valores reais daquele estado.
    """

    # --- Clima ---
    climate_score = climate_risk.get("score", 0.0)
    climate_cat = climate_risk.get("category", "")
    dims = climate_risk.get("dimensions", {})

    # dimensão climática dominante
    main_dim = None
    main_dim_value = None
    if dims:
        main_dim = max(dims, key=dims.get)
        main_dim_value = dims[main_dim]

    # tradução da dimensão dominante
    if lang == "pt":
        dim_names = {
            "Calor": "calor extremo",
            "Chuva / Enchentes": "chuva intensa e enchentes",
            "Vento": "ventos fortes",
            "Qualidade do Ar": "qualidade do ar deteriorada",
        }
    else:
        dim_names = {
            "Calor": "extreme heat",
            "Chuva / Enchentes": "intense rain and floods",
            "Vento": "strong winds",
            "Qualidade do Ar": "deteriorated air quality",
        }

    main_dim_desc = None
    if main_dim is not None:
        main_dim_desc = dim_names.get(main_dim, main_dim)

    # --- Socioeconômico (ML) ---
    socio_score = socio_risk.get("score", 0.0)
    socio_cat = socio_risk.get("category", "")
    ind = socio_risk.get("indicators", {})

    pib_pc = float(ind.get("PIB_per_capita", 0.0))
    pib_tot = float(ind.get("PIB_mil_reais", 0.0))
    pop = float(ind.get("Populacao", 0.0))
    dens = float(ind.get("Densidade_hab_km2", 0.0))

    # --- Setores ---
    sector_risk = socio_risk.get("sector_risk", {})
    # ordena por risco desc
    ranked_sectors = sorted(sector_risk.items(), key=lambda x: x[1], reverse=True)
    top_sectors = [name for name, _ in ranked_sectors[:2]]  # até 2 setores mais expostos

    # tradução simples de setores
    sector_map_en = {
        "Agropecuária": "Agriculture",
        "Indústria": "Industry",
        "Comércio": "Commerce",
        "Serviços": "Services",
    }

    if lang == "en":
        top_sectors_display = [sector_map_en.get(s, s) for s in top_sectors]
    else:
        top_sectors_display = top_sectors

    # --- Índice combinado ---
    comb_score = combined_risk.get("score", 0.0)
    comb_cat = combined_risk.get("category", "")
    w_dict = combined_risk.get("weights", {})
    w_climate = float(w_dict.get("climate", 0.6))
    # tenta nomes diferentes para o peso socioeconômico
    w_socio = float(
        w_dict.get("socioecon", w_dict.get("socioeconomico_ml", 0.4))
    )

    # normaliza só por segurança
    total_w = w_climate + w_socio
    if total_w > 0:
        w_climate_norm = w_climate / total_w
        w_socio_norm = w_socio / total_w
    else:
        w_climate_norm, w_socio_norm = 0.6, 0.4

    # formata pesos em porcentagem
    w_climate_pct = round(w_climate_norm * 100)
    w_socio_pct = round(w_socio_norm * 100)

    # --------- TEXTOS EM PORTUGUÊS ---------
    if lang == "pt":
        # 1) Risco climático
        if main_dim_desc and main_dim_value is not None:
            p1 = (
                f"O risco climático em <b>{capital} / {uf}</b> apresenta um score de "
                f"<b>{climate_score:.1f}</b> (categoria <b>{climate_cat}</b>). "
                f"Nesta janela de 5 dias, a dimensão predominante é "
                f"<b>{main_dim_desc}</b>, que responde por aproximadamente "
                f"{main_dim_value:.0f}% do risco climático estimado."
            )
        else:
            p1 = (
                f"O risco climático em <b>{capital} / {uf}</b> apresenta um score de "
                f"<b>{climate_score:.1f}</b> (categoria <b>{climate_cat}</b>), "
                f"com contribuição combinada de calor, chuva, vento e qualidade do ar."
            )

        # 2) Risco socioeconômico (ML)
        p2 = (
            f"O componente <b>socioeconômico</b>, estimado por um modelo de Machine Learning, "
            f"resulta em um score de <b>{socio_score:.1f}</b> (categoria <b>{socio_cat}</b>). "
            f"Os indicadores mais relevantes para esta UF incluem o <b>PIB per capita</b "
            f"de aproximadamente <b>R$ {pib_pc:,.0f}</b>, uma população em torno de "
            f"<b>{pop:,.0f}</b> habitantes, densidade populacional de <b>{dens:,.1f} hab/km²</b> "
            f"e PIB total da ordem de <b>R$ {pib_tot:,.0f} mil</b>."
        )

        # 3) Índice combinado
        p3 = (
            f"O <b>índice climatoeconômico integrado</b> combina o risco climático (peso "
            f"aproximado de <b>{w_climate_pct}%</b>) e o risco socioeconômico (peso "
            f"aproximado de <b>{w_socio_pct}%</b>), resultando em um score global de "
            f"<b>{comb_score:.1f}</b> (categoria <b>{comb_cat}</b>)."
        )

        # 4) Principais interpretações / lista
        bullets = []

        if main_dim_desc:
            bullets.append(
                f"A dimensão climática mais sensível para este estado, no horizonte de 5 dias, "
                f"é <b>{main_dim_desc}</b>, exigindo atenção especial em planos de contingência."
            )

        if top_sectors_display:
            bullets.append(
                "Os setores econômicos mais expostos, segundo o perfil da UF, são: "
                + ", ".join(f"<b>{s}</b>" for s in top_sectors_display)
                + "."
            )

        bullets.append(
            "O modelo socioeconômico baseado em ML utiliza múltiplas variáveis financeiras "
            "e demográficas, permitindo capturar padrões de vulnerabilidade que vão além "
            "de uma análise puramente descritiva."
        )

        bullets.append(
            "O índice integrado pode ser usado como um sinal de priorização para análises "
            "mais detalhadas, investimentos em resiliência e definição de políticas públicas."
        )

    # --------- TEXTOS EM INGLÊS ---------
    else:
        # 1) Climate risk
        if main_dim_desc and main_dim_value is not None:
            p1 = (
                f"The climate risk in <b>{capital} / {uf}</b> shows a score of "
                f"<b>{climate_score:.1f}</b> (category <b>{climate_cat}</b>). "
                f"In this 5-day window, the dominant dimension is "
                f"<b>{main_dim_desc}</b>, accounting for approximately "
                f"{main_dim_value:.0f}% of the estimated climate risk."
            )
        else:
            p1 = (
                f"The climate risk in <b>{capital} / {uf}</b> shows a score of "
                f"<b>{climate_score:.1f}</b> (category <b>{climate_cat}</b>), "
                f"with a combined contribution of heat, rainfall, wind and air quality."
            )

        # 2) Socioeconomic risk (ML)
        p2 = (
            f"The <b>socioeconomic</b> component, estimated by a Machine Learning model, "
            f"results in a score of <b>{socio_score:.1f}</b> (category <b>{socio_cat}</b>). "
            f"Key indicators for this state include a <b>GDP per capita</b> of approximately "
            f"<b>R$ {pib_pc:,.0f}</b>, total population close to <b>{pop:,.0f}</b> inhabitants, "
            f"population density of <b>{dens:,.1f} inhab/km²</b>, and a total GDP around "
            f"<b>R$ {pib_tot:,.0f} thousand</b>."
        )

        # 3) Combined index
        p3 = (
            f"The <b>integrated climate-economic index</b> combines climate risk "
            f"(weight around <b>{w_climate_pct}%</b>) and socioeconomic risk "
            f"(weight around <b>{w_socio_pct}%</b>), yielding a global score of "
            f"<b>{comb_score:.1f}</b> (category <b>{comb_cat}</b>)."
        )

        # 4) Bullets
        bullets = []

        if main_dim_desc:
            bullets.append(
                "The most sensitive climate dimension for this state, within the 5-day window, "
                f"is <b>{main_dim_desc}</b>, which should be carefully monitored in contingency plans."
            )

        if top_sectors_display:
            bullets.append(
                "The most exposed economic sectors, according to the state's profile, are: "
                + ", ".join(f"<b>{s}</b>" for s in top_sectors_display)
                + "."
            )

        bullets.append(
            "The ML-based socioeconomic model leverages multiple financial and demographic variables, "
            "capturing vulnerability patterns that go beyond purely descriptive analysis."
        )

        bullets.append(
            "The integrated index can be used as a prioritization signal for deeper analyses, "
            "resilience investments and public policy design."
        )

    # monta HTML final
    bullets_html = "".join(f"<li>{b}</li>" for b in bullets)

    html = f"""
    <div class="card-body-text">
      <p>{p1}</p>
      <p>{p2}</p>
      <p>{p3}</p>
      <ul>
        {bullets_html}
      </ul>
    </div>
    """
    return html

# ---------------- PAINEL 7 – RACIONAL DO MODELO (HTML ESTILIZADO) ----------------
# Título ligeiramente ajustado para refletir o uso de ML
if lang == "pt":
    TEXTS["pt"]["model_rationale_title"] = "Model Rationale (v1 – Clima + ML Socioeconômico)"
else:
    TEXTS["en"]["model_rationale_title"] = "Model Rationale (v1 – Climate + Socioeconomic ML)"

rationale_html = build_model_rationale_html(
    lang=lang,
    uf=uf,
    capital=capital,
    climate_risk=climate_risk,
    socio_risk=socio_risk,
    combined_risk=combined_risk,
)

st.markdown(
    f"""
    <div class="card">
      <div class="card-header">
        🧠 {T("model_rationale_title")}
      </div>
      {rationale_html}
    </div>
    """,
    unsafe_allow_html=True,
)

# ---------------- PAINEL 8 – NOTA METODOLÓGICA ----------------
if lang == "pt":
    TEXTS["pt"]["method_note_title"] = "Nota Metodológica (versão 1.0)"

    method_html = """
    <div class="card-body-text">
      Esta é a versão <b>v1.0</b> do MVP3 em Streamlit, integrando dados da OpenWeather
      (<i>Current Weather</i>, <i>5-day / 3-hour Forecast</i>, <i>Air Pollution</i> e
      <i>Weather Maps</i>) com a base socioeconômica consolidada do projeto (arquivo
      <code>mvp3_dataset.csv</code>).
      <br/><br/>
      O componente de risco climático é calculado a partir de índices de calor, chuva,
      vento e qualidade do ar, normalizados em uma escala de 0 a 100. O componente
      socioeconômico é estimado por um modelo de <b>Machine Learning</b>, treinado com variáveis
      de PIB, população, densidade demográfica e outras dimensões econômicas.
      <br/><br/>
      A combinação dos dois componentes gera um <b>índice climatoeconômico integrado</b>, com
      pesos atualmente fixados em aproximadamente 60% para clima e 40% para o componente
      socioeconômico, permitindo priorizar estados mais vulneráveis para análises adicionais,
      estudos de impacto e ações de mitigação.
    </div>
    """
else:
    TEXTS["en"]["method_note_title"] = "Methodological Note (version 1.0)"

    method_html = """
    <div class="card-body-text">
      This is the <b>v1.0</b> version of MVP3 in Streamlit, integrating OpenWeather data
      (<i>Current Weather</i>, <i>5-day / 3-hour Forecast</i>, <i>Air Pollution</i> and
      <i>Weather Maps</i>) with the project's consolidated socioeconomic database
      (<code>mvp3_dataset.csv</code>).
      <br/><br/>
      The climate risk component is derived from heat, rainfall, wind and air quality
      indices, normalized on a 0–100 scale. The socioeconomic component is estimated
      by a <b>Machine Learning</b> model trained with GDP, population, demographic density
      and other economic features.
      <br/><br/>
      Both components are combined into an <b>integrated climate-economic index</b>, with
      current weights of approximately 60% for climate and 40% for the socioeconomic
      component, enabling the prioritization of more vulnerable states for further
      analysis, impact studies and mitigation planning.
    </div>
    """

st.markdown(
    f"""
    <div class="card">
      <div class="card-header">
        📜 {T("method_note_title")}
      </div>
      {method_html}
    </div>
    """,
    unsafe_allow_html=True,
)
