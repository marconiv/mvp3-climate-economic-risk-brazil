# ============================================================
# train_socioecon_model.py
# ============================================================
# Treina o modelo de vulnerabilidade socioeconômica
# usando o dataset mvp3_dataset.csv.
#
# Gera artefatos para o MVP3:
#  - model.joblib
#  - shap_summary.png
#  - shap_summary.html
#
# ============================================================

import os
import pandas as pd
import numpy as np
from joblib import dump
import matplotlib.pyplot as plt
import shap

from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_absolute_error

# ------------------------------------------------------------
# Configuração de diretórios
# ------------------------------------------------------------
BASE_DATASET = "/mnt/data/mvp3_dataset.csv"

OUT_DIR = "models_ml"
os.makedirs(OUT_DIR, exist_ok=True)


# ------------------------------------------------------------
# 1) Carregar dataset socioeconômico
# ------------------------------------------------------------
print("🔍 Lendo dataset socioeconômico...")
df = pd.read_csv(BASE_DATASET)

required_cols = [
    "UF", "Ano", "PIB_mil_reais", "Populacao",
    "Area_km2", "Densidade_hab_km2", "PIB_per_capita"
]

if not set(required_cols).issubset(df.columns):
    raise RuntimeError(f"Dataset inválido. Colunas necessárias: {required_cols}")

print(f"✔ Dataset carregado com {len(df)} linhas.")


# ------------------------------------------------------------
# 2) Criar target Y (Vulnerabilidade socioeconômica)
# ------------------------------------------------------------
# Aqui replicamos 100% o racional da heurística oficial do MVP3:
#   vulnerabilidade = combinação de PIB_pc (invertido), densidade e população.

print("⚙ Criando variável-alvo (Y) baseada na heurística do MVP3...")

# Min-max globais por média da UF
df_avg = df.groupby("UF").agg(
    pib_pc=("PIB_per_capita", "mean"),
    dens=("Densidade_hab_km2", "mean"),
    pop=("Populacao", "mean")
).reset_index()

pib_min, pib_max = df_avg["pib_pc"].min(), df_avg["pib_pc"].max()
dens_min, dens_max = df_avg["dens"].min(), df_avg["dens"].max()
pop_min, pop_max = df_avg["pop"].min(), df_avg["pop"].max()

def mm(x, a, b):
    return (x - a) / (b - a) if b > a else 0.0

Y_list = []

for _, row in df.iterrows():
    pib = row["PIB_per_capita"]
    dens = row["Densidade_hab_km2"]
    pop = row["Populacao"]

    # Normalizações
    pib_norm_inv = 1 - mm(pib, pib_min, pib_max)
    dens_norm = mm(dens, dens_min, dens_max)
    pop_norm = mm(pop, pop_min, pop_max)

    # Vulnerabilidade final da heurística
    vuln = (
        0.5 * pib_norm_inv +
        0.3 * dens_norm +
        0.2 * pop_norm
    ) * 100

    Y_list.append(vuln)

df["Vulnerabilidade"] = Y_list

print("✔ Variável-alvo criada.")


# ------------------------------------------------------------
# 3) Criar features X
# ------------------------------------------------------------
print("📊 Construindo matriz de features (X)...")

X = df[[
    "PIB_per_capita",
    "Densidade_hab_km2",
    "Populacao",
    "PIB_mil_reais",
]]

Y = df["Vulnerabilidade"]

print("✔ Features prontas.")


# ------------------------------------------------------------
# 4) Split train/test
# ------------------------------------------------------------
print("✂ Dividindo conjunto em treino e teste...")
X_train, X_test, y_train, y_test = train_test_split(
    X, Y,
    test_size=0.25,
    random_state=42
)

print("✔ Split concluído.")


# ------------------------------------------------------------
# 5) Treinar modelo ML (RandomForest)
# ------------------------------------------------------------
print("🌲 Treinando RandomForestRegressor...")

model = RandomForestRegressor(
    n_estimators=400,
    max_depth=8,
    random_state=42
)

model.fit(X_train, y_train)

print("✔ Modelo treinado.")


# ------------------------------------------------------------
# 6) Avaliação
# ------------------------------------------------------------
y_pred = model.predict(X_test)

r2 = r2_score(y_test, y_pred)
mae = mean_absolute_error(y_test, y_pred)

print("\n📈 Desempenho do modelo:")
print(f"   R²  = {r2:.4f}")
print(f"   MAE = {mae:.4f}\n")

# ------------------------------------------------------------
# 7) Salvar modelo
# ------------------------------------------------------------
model_path = os.path.join(OUT_DIR, "model.joblib")
dump(model, model_path)

print(f"💾 Modelo salvo em: {model_path}")


# ------------------------------------------------------------
# 8) SHAP Explainability
# ------------------------------------------------------------
print("🧠 Gerando explicabilidade SHAP...")

explainer = shap.TreeExplainer(model)
shap_values = explainer.shap_values(X)

# PNG estático
plt.figure(figsize=(10, 6))
shap.summary_plot(shap_values, X, show=False)
png_path = os.path.join(OUT_DIR, "shap_summary.png")
plt.savefig(png_path, dpi=180, bbox_inches="tight")
plt.close()

print(f"📸 SHAP Summary (PNG) salvo em: {png_path}")

# HTML interativo
html_path = os.path.join(OUT_DIR, "shap_summary.html")
shap.save_html(html_path, shap.summary_plot(shap_values, X))

print(f"🌐 SHAP Summary (HTML) salvo em: {html_path}")

print("\n🎉 Treinamento concluído com sucesso!")
print("Agora o MVP3 pode carregar o modelo e exibir o gráfico SHAP.")
