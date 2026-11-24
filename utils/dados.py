from __future__ import annotations

import json
from pathlib import Path
import numpy as np
import pandas as pd
import streamlit as st

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PROCESSED = BASE_DIR / "data" / "processed"
DATA_RAW = BASE_DIR / "data" / "raw"

MESES = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]

MESES_CONFIG = [
    (1, "Jan", "MED_JAN"),
    (2, "Fev", "MED_FEV"),
    (3, "Mar", "MED_MAR"),
    (4, "Abr", "MED_ABR"),
    (5, "Mai", "MED_MAI"),
    (6, "Jun", "MED_JUN"),
    (7, "Jul", "MED_JUL"),
    (8, "Ago", "MED_AGO"),
    (9, "Set", "MED_SET"),
    (10, "Out", "MED_OUT"),
    (11, "Nov", "MED_NOV"),
    (12, "Dez", "MED_DEZ"),
]


def _classificar_regiao_hidrografica(row: pd.Series) -> str:
    lon = float(row["X"])
    lat = float(row["Y"])
    if lat > -7.5 and lon > -47.0:
        return "Parnaíba / Atlântico Nordeste"
    if lon < -51.5 and lat > -15.5:
        return "Amazônica (Tapajós / Xingu)"
    if lat > -14.5 and -51.5 <= lon <= -46.0:
        return "Tocantins-Araguaia"
    if -47.0 <= lon <= -41.5 and -20.5 <= lat <= -10.5:
        return "São Francisco"
    if lon < -52.5 and lat <= -15.5:
        return "Paraguai (Alto Paraguai)"
    return "Paraná (Paranaíba / Grande)"


@st.cache_data(show_spinner=False)
def carregar_resumo_indicadores() -> dict:
    caminho = DATA_PROCESSED / "resumo_indicadores.json"
    if caminho.exists():
        with open(caminho, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


@st.cache_data(show_spinner=False)
def carregar_tocantins_sazonalidade() -> pd.DataFrame:
    caminho = DATA_PROCESSED / "tocantins_sazonalidade.csv"
    if caminho.exists():
        return pd.read_csv(caminho)
    return pd.DataFrame(columns=["ordem", "mes", "miracema_mm", "conceicao_mm"])


@st.cache_data(show_spinner=False)
def carregar_panorama_brasil() -> pd.DataFrame:
    caminho = DATA_PROCESSED / "panorama_pluviometrico_brasil.csv"
    if caminho.exists():
        return pd.read_csv(caminho)
    return pd.DataFrame()


@st.cache_data(show_spinner=False)
def carregar_estacoes() -> pd.DataFrame:
    """Retorna o cadastro espacial das 807 estações pluviométricas reais do Cerrado."""
    caminho = DATA_PROCESSED / "climatologia_pluviometrica_cerrado.csv"
    if not caminho.exists():
        caminho = DATA_RAW / "estacoes_cerrado_807.csv"

    df = pd.read_csv(caminho)
    df["Bacia"] = df.apply(_classificar_regiao_hidrografica, axis=1)
    df["Status"] = np.where(
        df["EMOPER"].astype(str).str.lower().str.strip() == "sim",
        "Ativa",
        "Inativa",
    )
    df["Estacao"] = df["CD"].astype(str).str.strip() + " · " + df["NM"].astype(str).str.strip()
    df["Lat"] = df["Y"].astype(float)
    df["Lon"] = df["X"].astype(float)
    return df


@st.cache_data(show_spinner=False)
def carregar_dados() -> pd.DataFrame:
    """
    Retorna a base mensal climatológica real das 807 estações pluviométricas
    do Cerrado (CPRM/ANA), estruturada para os filtros, gráficos e mapa do painel.
    """
    df_est = carregar_estacoes()

    registros = []
    for mes_num, mes_nome, col_med in MESES_CONFIG:
        precip_mensal = pd.to_numeric(df_est[col_med], errors="coerce").fillna(0.0)
        precip_anual = pd.to_numeric(df_est["MED_ANUAL"], errors="coerce").fillna(0.0)
        cdd = pd.to_numeric(df_est["MED_CDD"], errors="coerce").fillna(0.0)
        rx1day = pd.to_numeric(df_est["MED_RX1DAY"], errors="coerce").fillna(0.0)

        indice_umidade_pct = np.clip((precip_mensal / 350.0) * 100.0, 0.0, 100.0)

        bloco = pd.DataFrame(
            {
                "Bacia": df_est["Bacia"],
                "Estacao": df_est["Estacao"],
                "Codigo": df_est["CD"].astype(str).str.strip(),
                "Operadora": df_est["OPERAD"].fillna("ANA/CPRM").astype(str),
                "Status": df_est["Status"],
                "Lat": df_est["Lat"],
                "Lon": df_est["Lon"],
                "Ano": pd.to_numeric(df_est["ANOFIM"], errors="coerce").fillna(2019).astype(int),
                "Ano_Inicio": pd.to_numeric(df_est["ANOINI"], errors="coerce").fillna(1980).astype(int),
                "Ano_Fim": pd.to_numeric(df_est["ANOFIM"], errors="coerce").fillna(2019).astype(int),
                "Mes_Num": mes_num,
                "Mes": mes_nome,
                "Precipitacao_mm": precip_mensal.round(2),
                "Precipitacao_Anual_mm": precip_anual.round(2),
                "Dias_Secos_Consecutivos": cdd.round(1),
                "Max_Chuva_Diaria_mm": rx1day.round(1),
                "Vazao_m3s": precip_mensal.round(2),
                "Demanda_Outorga_m3s": (precip_mensal * 0.25).round(2),
                "Disponibilidade_m3s": (precip_mensal * 0.75).round(2),
                "Disponibilidade_Pct": indice_umidade_pct.round(1),
            }
        )
        registros.append(bloco)

    return pd.concat(registros, ignore_index=True)