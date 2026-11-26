import pandas as pd
import streamlit as st

from utils.dados import carregar_dados
from utils.tema import exibir_rodape

DICIONARIO = pd.DataFrame(
    [
        ("Bacia", "Nome da bacia hidrográfica associada à observação."),
        ("Estacao", "Identificador descritivo da estação de monitoramento simulada."),
        ("Status", "Situação da estação: ativa, intermitente ou inativa."),
        ("Ano / Mes_Num / Mes", "Ano e mês de referência da observação."),
        ("Vazao_m3s", "Vazão média mensal em metros cúbicos por segundo."),
        ("Precipitacao_mm", "Precipitação mensal estimada em milímetros."),
        ("Demanda_Outorga_m3s", "Demanda outorgada simulada em metros cúbicos por segundo."),
        ("Disponibilidade_Pct", "Índice sintético de disponibilidade hídrica, em percentual."),
        ("Disponibilidade_m3s", "Parcela da vazão correspondente ao índice de disponibilidade."),
        ("Lat / Lon", "Coordenadas aproximadas da estação para visualização no mapa."),
    ],
    columns=["Variável", "Descrição"],
)


def renderizar_base() -> None:
    dados = carregar_dados()
    st.title("Base de dados & metodologia", icon=":material/database:")
    st.caption(
        "Fontes, definições e exploração do conjunto de dados compartilhado pelo DASHIDRO."
    )

    st.warning(
        "Esta versão utiliza dados simulados para demonstração. "
        "Os valores não são medições oficiais e não devem embasar decisões operacionais."
    )

    with st.container(border=True):
        st.subheader("Fontes de referência")
        fontes = st.columns(3, gap="medium")
        with fontes[0]:
            st.markdown("**ANA · Agência Nacional de Águas e Saneamento Básico**")
            st.write(
                "Referência para séries de estações fluviométricas, "
                "pluviométricas e informações de outorgas."
            )
        with fontes[1]:
            st.markdown("**INMET · Instituto Nacional de Meteorologia**")
            st.write(
                "Referência para dados meteorológicos e de precipitação "
                "observados por estações."
            )
        with fontes[2]:
            st.markdown("**MapBiomas**")
            st.write(
                "Referência para cobertura e uso da terra, como contexto "
                "territorial da análise hidrológica."
            )

    with st.container(border=True):
        st.subheader("Metodologia da demonstração")
        st.write(
            "A base reproduz uma série mensal de 2000 a 2024 para as bacias dos rios "
            "Meia Ponte, Corumbá, Vermelho e Paranã. Os valores sintéticos incorporam "
            "variação sazonal de chuva e vazão, diferenças entre bacias e uma tendência "
            "histórica moderada. O carregamento é centralizado em `utils/dados.py`."
        )

    with st.container(border=True):
        st.subheader("Dicionário de variáveis")
        st.dataframe(
            DICIONARIO,
            hide_index=True,
            alt="Dicionário de campos e unidades da base DASHIDRO",
        )

    st.subheader("Explorar a base completa")
    busca = st.text_input(
        "Buscar na base",
        placeholder="Ex.: Meia Ponte, Ativa, 2020...",
        key="busca_base",
    )
    dados_exibidos = dados
    if busca.strip():
        mascara = dados.astype("string").apply(
            lambda coluna: coluna.str.contains(
                busca.strip(),
                case=False,
                regex=False,
                na=False,
            )
        )
        dados_exibidos = dados.loc[mascara.any(axis=1)]

    st.caption(
        f"{len(dados_exibidos):,} de {len(dados):,} registros encontrados".replace(
            ",", "."
        )
    )
    st.dataframe(
        dados_exibidos,
        hide_index=True,
        alt="Registros completos da base hidrológica sintética",
    )
    st.download_button(
        "Baixar conjunto completo em CSV",
        data=dados.to_csv(index=False).encode("utf-8-sig"),
        file_name="dashidro_base_completa.csv",
        mime="text/csv",
        icon=":material/download:",
    )

    exibir_rodape()
