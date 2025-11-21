# socioecon_risk_engine.py

from functools import lru_cache
from typing import Dict, Tuple
import pandas as pd
import numpy as np
import os

# =========================================================
# 1) MAPEAMENTO DE SIGLA PARA NOME COMPLETO DO ESTADO
# =========================================================

UF_TO_NAME = {
    "AC": "Acre",
    "AL": "Alagoas",
    "AP": "Amapá",
    "AM": "Amazonas",
    "BA": "Bahia",
    "CE": "Ceará",
    "DF": "Distrito Federal",
    "ES": "Espírito Santo",
    "GO": "Goiás",
    "MA": "Maranhão",
    "MT": "Mato Grosso",
    "MS": "Mato Grosso do Sul",
    "MG": "Minas Gerais",
    "PA": "Pará",
    "PB": "Paraíba",
    "PR": "Paraná",
    "PE": "Pernambuco",
    "PI": "Piauí",
    "RJ": "Rio de Janeiro",
    "RN": "Rio Grande do Norte",
    "RS": "Rio Grande do Sul",
    "RO": "Rondônia",
    "RR": "Roraima",
    "SC": "Santa Catarina",
    "SP": "São Paulo",
    "SE": "Sergipe",
    "TO": "Tocantins",
}

DATA_PATH = os.path.join("data", "mvp3_dataset.csv")


# =========================================================
# 2) LEITURA DO DATASET + ESTATÍSTICAS POR UF
# =========================================================

@lru_cache(maxsize=1)
def load_dataset() -> Tuple[pd.DataFrame, pd.DataFrame]:
    if not os.path.exists(DATA_PATH):
        raise FileNotFoundError(f"Dataset não encontrado em: {DATA_PATH}")

    df = pd.read_csv(DATA_PATH)

    required_cols = {
        "UF", "Ano", "PIB_mil_reais", "Populacao",
        "Area_km2", "Densidade_hab_km2", "PIB_per_capita"
    }
    if not required_cols.issubset(df.columns):
        raise RuntimeError(
            f"Dataset socioeconômico incompleto. Deve conter: {sorted(required_cols)}"
        )

    # Aqui a coluna UF está com o NOME do estado (ex.: "Acre", "São Paulo")
    # Calculamos médias por estado para normalização mais estável
    uf_stats = df.groupby("UF").agg(
        pib_pc_mean=("PIB_per_capita", "mean"),
        dens_mean=("Densidade_hab_km2", "mean"),
        pop_mean=("Populacao", "mean"),
        pib_total_mean=("PIB_mil_reais", "mean"),
    ).reset_index()

    return df, uf_stats


def _minmax(val: float, vmin: float, vmax: float) -> float:
    if vmax == vmin:
        return 0.0
    x = (val - vmin) / (vmax - vmin)
    return float(np.clip(x, 0.0, 1.0))


def _categorize_vuln(score: float) -> str:
    """
    Categorização do score de vulnerabilidade socioeconômica (0–100).
    """
    if score < 25:
        return "Baixa vulnerabilidade"
    if score < 50:
        return "Moderada"
    if score < 75:
        return "Alta"
    return "Crítica"


def _sector_profile(uf: str, base_score: float) -> Dict[str, float]:
    """
    Define pesos setoriais de forma heurística com base no perfil do estado.
    base_score está em 0–100 e serve como patamar para todos os setores.
    """
    uf = uf.upper()

    # Estados com perfil agro forte (maior peso em Agropecuária)
    agro_heavy = {"MT", "MS", "GO", "RS", "PR", "MG", "BA", "TO", "RO", "PA"}

    # Estados mais industriais/urbanos (maior peso em Indústria/Serviços)
    industry_heavy = {"SP", "RJ", "MG", "PR", "SC", "RS"}

    # Base neutra: todos os setores com o mesmo peso
    weights = {
        "Agropecuária": 1.0,
        "Indústria": 1.0,
        "Comércio": 1.0,
        "Serviços": 1.0,
    }

    if uf in agro_heavy:
        weights["Agropecuária"] += 0.5
        weights["Comércio"] += 0.2
    if uf in industry_heavy:
        weights["Indústria"] += 0.5
        weights["Serviços"] += 0.2

    total_w = sum(weights.values())
    for k in weights:
        weights[k] /= total_w

    sector_risk = {k: float(np.round(base_score * w, 1)) for k, w in weights.items()}
    return sector_risk


# =========================================================
# 3) FUNÇÃO PRINCIPAL
# =========================================================

def compute_socioecon_risk(uf: str, ano_ref: int = None) -> Dict:
    df, uf_stats = load_dataset()

    uf = uf.upper()
    if uf not in UF_TO_NAME:
        raise ValueError(f"UF '{uf}' inválida.")

    estado_nome = UF_TO_NAME[uf]

    # No CSV, a coluna "UF" contém o nome por extenso
    df_uf = df[df["UF"].str.lower() == estado_nome.lower()]
    if df_uf.empty:
        raise ValueError(f"Estado '{estado_nome}' não encontrado no dataset socioeconômico.")

    # Seleciona o ano de referência (ou o mais recente)
    if ano_ref is None:
        ano_ref = int(df_uf["Ano"].max())

    df_atual = df_uf[df_uf["Ano"] == ano_ref]
    if df_atual.empty:
        df_atual = df_uf[df_uf["Ano"] == df_uf["Ano"].max()]

    row = df_atual.iloc[0]

    pib_pc = float(row["PIB_per_capita"])
    dens = float(row["Densidade_hab_km2"])
    pop = float(row["Populacao"])
    pib_total = float(row["PIB_mil_reais"])

    # médias por UF (para ranking relativo)
    stats_row = uf_stats[uf_stats["UF"] == estado_nome]
    if stats_row.empty:
        # fallback – usa os valores do ano atual
        pib_pc_avg = pib_pc
        dens_avg = dens
        pop_avg = pop
    else:
        stats_row = stats_row.iloc[0]
        pib_pc_avg = float(stats_row["pib_pc_mean"])
        dens_avg = float(stats_row["dens_mean"])
        pop_avg = float(stats_row["pop_mean"])

    # Min–max globais com base nas MÉDIAS por UF (mais robusto)
    pib_min = float(uf_stats["pib_pc_mean"].min())
    pib_max = float(uf_stats["pib_pc_mean"].max())
    dens_min = float(uf_stats["dens_mean"].min())
    dens_max = float(uf_stats["dens_mean"].max())
    pop_min = float(uf_stats["pop_mean"].min())
    pop_max = float(uf_stats["pop_mean"].max())

    # Normalizações (0–1)
    # Quanto menor o PIB per capita médio, maior a vulnerabilidade → invertido
    pib_pc_norm_inv = 1.0 - _minmax(pib_pc_avg, pib_min, pib_max)
    # Quanto maior a densidade média, maior a vulnerabilidade
    dens_norm = _minmax(dens_avg, dens_min, dens_max)
    # Quanto maior a população média, maior a exposição
    pop_norm = _minmax(pop_avg, pop_min, pop_max)

    # Pesos internos – foco em vulnerabilidade estrutural:
    # 50% PIB per capita (capacidade econômica),
    # 30% densidade (pressão urbana),
    # 20% população (exposição).
    w_pib = 0.5
    w_dens = 0.3
    w_pop = 0.2

    risk_01 = w_pib * pib_pc_norm_inv + w_dens * dens_norm + w_pop * pop_norm
    score = float(np.round(risk_01 * 100, 1))
    category = _categorize_vuln(score)

    indicators = {
        "UF_nome": estado_nome,
        "Ano_ref": int(ano_ref),
        "PIB_per_capita": pib_pc,
        "Densidade_hab_km2": dens,
        "Populacao": pop,
        "PIB_mil_reais": pib_total,
    }

    sector_risk = _sector_profile(uf, score)

    return {
        "score": score,
        "category": category,
        "indicators": indicators,
        "sector_risk": sector_risk,
        "components": {
            "PIB_pc_norm_inv": float(np.round(pib_pc_norm_inv * 100, 1)),
            "Densidade_norm": float(np.round(dens_norm * 100, 1)),
            "Pop_norm": float(np.round(pop_norm * 100, 1)),
        },
    }
