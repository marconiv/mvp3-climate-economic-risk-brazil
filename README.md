# 🌎 MVP3 — Climate–Economic Risk Platform (Brazil)
### Integrating Climate Data + Machine Learning Socioeconomic Models for State-Level Vulnerability Assessment  
**OpenWeather Challenge Edition**

---

## 🔍 Overview

The **MVP3 – Climate-Economic Risk Platform** is an interactive application that integrates **real-time climate data from OpenWeather** with a **Machine Learning–based socioeconomic vulnerability model** to generate a combined **climate-economic risk index** for each Brazilian state (UF).

This project was developed as part of the **OpenWeather Challenge**, focusing on originality, impact, and technical transparency.

Access the live application here:  
👉 **https://mvp3-climate-economic-risk-brazil.streamlit.app/**

---

## 📌 Key Features

- **Forecast-based climate risk** (heat, rain & floods, wind, and air quality)  
- **Socioeconomic ML model** trained on:
  - GDP per capita  
  - Total GDP  
  - Population  
  - Density  
  - Additional derived indicators  
- **Integrated risk index (60% climate + 40% socioeconomic)**  
- **Explainability with SHAP** (global + local importance)  
- **Interactive dashboards**  
- **Dual-language interface (PT/EN)**  
- **OpenWeather API integration**  
- **Deployed on Streamlit Cloud**

---

## 📂 Project Structure

mvp3-climate-economic-risk-brazil/
│
├── data/
│ └── mvp3_dataset.csv # ML dataset
│
├── models_ml/
│ ├── socio_model.pkl # Trained ML model
│ └── socio_shap_values.pkl # SHAP explainability
│
├── app_streamlit_mvp3.py # Main application
├── climate_risk_engine.py # Climate risk computation
├── socioecon_risk_engine.py # ML preprocessing
├── combined_risk_engine.py # Climate + socioeconomic combination
├── risk_engine.py # High-level orchestration
├── openweather_client.py # API consumption
├── weather_maps.py # Weather Maps integration (OpenWeather)
├── theme.py # UI theme configuration
├── requirements.txt # Dependencies
└── README.md

---

## ⚠️ Important — API Key Requirement

To run this project locally, **you must create a `.env` file** in the root directory containing:


👉 You can obtain a free API key at  
https://home.openweathermap.org/api_keys

> The `.env` file is intentionally excluded from the repository  
> (via `.gitignore`) to protect private credentials.

---

## 🛠️ Installation

### 1. Clone the repository

```bash
git clone https://github.com/marconiv/mvp3-climate-economic-risk-brazil.git
cd mvp3-climate-economic-risk-brazil

### 2. Create your .env
OPENWEATHER_KEY=YOUR_PERSONAL_KEY

3. Install dependencies
pip install -r requirements.txt

4. Run the app
streamlit run app_streamlit_mvp3.py

🧠 Machine Learning Model (Socioeconomic Component)

Model type: Random Forest Regressor

Task: Predict socioeconomic vulnerability (0–100)

Input variables:

GDP per capita

Total GDP

Population

Density

Output:

Vulnerability score

Category label (Baixo / Moderado / Alto / Crítico)

Explainability:

SHAP summary plot

State-level local SHAP values

☁️ OpenWeather Integrations

Current Weather

5-day / 3-hour Forecast

Air Pollution API

Weather Maps (Tile layers)
All climate indices are normalized between 0 and 100.

🎯 Purpose & Impact

This platform provides a first-of-its-kind integrated view of climate and socioeconomic vulnerability for Brazil, enabling:

Public sector decision-making

Contingency planning

Investment prioritization

Early risk identification

Socio-climatic resilience insights

🌐 Live Demo

💻 Streamlit Cloud:
👉 https://mvp3-climate-economic-risk-brazil.streamlit.app/

📝 License

This project is released under the MIT License.

🙌 Acknowledgments

OpenWeather — APIs and Challenge platform

Scikit-learn — Machine learning

SHAP — AI explainability

Streamlit — Application framework

✨ About the Author

Marconi Fábio Vieira
InfoChoice Tecnologia Ltda
40+ years of experience in IT, AI, Data Science & Project Management
Brazil 🌎

Post about the app: https://infochoice.com.br/site/index.php/2025/11/21/mvp3-climate-economic-risk-platform-a-new-integrated-view-of-state-level-vulnerability-in-brazil/
