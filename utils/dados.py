import numpy as np
import pandas as pd
import streamlit as st

MESES = [
    "Jan", "Fev", "Mar", "Abr", "Mai", "Jun",
    "Jul", "Ago", "Set", "Out", "Nov", "Dez",
]

_BACIAS = {
    "Bacia do Rio Meia Ponte": (-16.68, -49.25, 1.00, 1.00),
    "Bacia do Rio Corumbá": (-17.73, -48.62, 1.35, 1.08),
    "Bacia do Rio Vermelho": (-15.93, -50.14, 0.85, 0.94),
    "Bacia do Rio Paranã": (-14.55, -47.45, 1.50, 0.88),
}

_FATORES_SAZONAIS = [
    1.45, 1.50, 1.35, 1.05, 0.75, 0.55,
    0.45, 0.40, 0.48, 0.75, 1.10, 1.35,
]


@st.cache_data
def carregar_dados() -> pd.DataFrame:
    """Gera uma série sintética por estação, bacia, ano e mês."""
    rng = np.random.default_rng(42)
    registros = []

    for bacia, (lat_base, lon_base, fator_vazao, fator_chuva) in _BACIAS.items():
        for numero_estacao in range(1, 6):
            nome_estacao = f"Estação {numero_estacao:02d} · {bacia.replace('Bacia do Rio ', '')}"
            status = (
                "Ativa" if numero_estacao <= 3
                else "Intermitente" if numero_estacao == 4
                else "Inativa"
            )
            lat_estacao = lat_base + rng.uniform(-0.2, 0.2)
            lon_estacao = lon_base + rng.uniform(-0.2, 0.2)
            fator_estacao = rng.uniform(0.82, 1.18)

            for ano in range(2000, 2025):
                tendencia = 1 - (ano - 2000) * 0.008
                for indice_mes, mes in enumerate(MESES):
                    sazonalidade = _FATORES_SAZONAIS[indice_mes]
                    fator = fator_vazao * fator_estacao * sazonalidade * tendencia
                    vazao = max(8.0, rng.normal(140 * fator, 12))
                    precipitacao = max(
                        0.0,
                        rng.normal(135 * sazonalidade * fator_chuva, 20),
                    )
                    demanda = vazao * rng.uniform(0.22, 0.35)
                    disponibilidade_pct = np.clip(
                        82 * tendencia + rng.normal(0, 4),
                        35,
                        98,
                    )

                    registros.append(
                        {
                            "Bacia": bacia,
                            "Estacao": nome_estacao,
                            "Status": status,
                            "Ano": ano,
                            "Mes_Num": indice_mes + 1,
                            "Mes": mes,
                            "Vazao_m3s": round(vazao, 1),
                            "Precipitacao_mm": round(precipitacao, 1),
                            "Demanda_Outorga_m3s": round(demanda, 1),
                            "Disponibilidade_Pct": round(float(disponibilidade_pct), 1),
                            "Disponibilidade_m3s": round(
                                vazao * disponibilidade_pct / 100,
                                1,
                            ),
                            "Lat": round(lat_estacao, 5),
                            "Lon": round(lon_estacao, 5),
                        }
                    )

    return pd.DataFrame(registros)


@st.cache_data
def carregar_estacoes() -> pd.DataFrame:
    """Retorna o catálogo único de estações do conjunto compartilhado."""
    dados = carregar_dados()
    return dados[
        ["Bacia", "Estacao", "Status", "Lat", "Lon"]
    ].drop_duplicates("Estacao").reset_index(drop=True)
