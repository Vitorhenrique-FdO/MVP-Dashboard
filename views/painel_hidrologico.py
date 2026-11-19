import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from utils.dados import MESES, carregar_dados, carregar_estacoes
from utils.tema import PALETA, exibir_rodape

VARIAVEIS = {
    "Vazão média (m³/s)": "Vazao_m3s",
    "Precipitação (mm)": "Precipitacao_mm",
    "Disponibilidade hídrica (%)": "Disponibilidade_Pct",
    "Demanda por outorgas (m³/s)": "Demanda_Outorga_m3s",
}


def _formatar_delta(atual: float, anterior: float) -> str:
    if anterior == 0:
        return "—"
    return f"{(atual - anterior) / abs(anterior) * 100:+.1f}%".replace(".", ",")


def _percentual_comprometimento(dados: pd.DataFrame) -> float:
    disponibilidade = dados["Disponibilidade_m3s"].mean()
    if pd.isna(disponibilidade) or disponibilidade <= 0:
        return 0.0
    return float(dados["Demanda_Outorga_m3s"].mean() / disponibilidade * 100)


def _finalizar_figura(figura: go.Figure, altura: int = 330) -> go.Figure:
    figura.update_layout(
        height=altura,
        margin=dict(l=12, r=12, t=25, b=12),
        paper_bgcolor="white",
        plot_bgcolor="white",
        font=dict(color=PALETA["texto"]),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    return figura


def _exibir_perguntas() -> None:
    perguntas = [
        (
            "01 · TENDÊNCIA HISTÓRICA",
            "Como as águas estão mudando?",
            "Acompanhe vazões, chuvas e disponibilidade ao longo das últimas décadas.",
            PALETA["azul"],
        ),
        (
            "02 · SAZONALIDADE & ESTIAGEM",
            "Quando a água aperta?",
            "Compare o período chuvoso com a estiagem típica do Cerrado goiano.",
            PALETA["ambar"],
        ),
        (
            "03 · PRESSÃO DE USO & OUTORGAS",
            "Quanto da água está comprometido?",
            "Observe a relação entre disponibilidade hídrica e demanda outorgada.",
            PALETA["azul_claro"],
        ),
    ]
    colunas = st.columns(3, gap="medium")
    for coluna, (numero, titulo, texto, cor) in zip(colunas, perguntas):
        with coluna:
            st.html(
                f"""
                <article class="question-card" style="border-top-color: {cor}">
                    <span class="question-number">{numero}</span>
                    <h3>{titulo}</h3>
                    <p>{texto}</p>
                </article>
                """
            )


def _exibir_kpis(dados: pd.DataFrame, estacoes: pd.DataFrame) -> None:
    anos = sorted(dados["Ano"].unique())
    recente = dados[dados["Ano"].isin(anos[-3:])]
    anterior = dados[dados["Ano"].isin(anos[-6:-3])]
    if anterior.empty:
        anterior = dados

    media_vazao = float(dados["Vazao_m3s"].mean())
    media_chuva = float(dados["Precipitacao_mm"].mean())
    media_disponibilidade = float(dados["Disponibilidade_Pct"].mean())
    comprometimento = _percentual_comprometimento(dados)
    vazao_recente = float(recente["Vazao_m3s"].mean())
    vazao_anterior = float(anterior["Vazao_m3s"].mean())
    chuva_recente = float(recente["Precipitacao_mm"].mean())
    chuva_anterior = float(anterior["Precipitacao_mm"].mean())
    disponibilidade_recente = float(recente["Disponibilidade_Pct"].mean())
    disponibilidade_anterior = float(anterior["Disponibilidade_Pct"].mean())
    uso_recente = _percentual_comprometimento(recente)
    uso_anterior = _percentual_comprometimento(anterior)

    metricas = [
        (
            "Vazão (m³/s)",
            f"{media_vazao:.0f}",
            _formatar_delta(vazao_recente, vazao_anterior),
        ),
        (
            "Chuva (mm/mês)",
            f"{media_chuva:.0f}",
            _formatar_delta(chuva_recente, chuva_anterior),
        ),
        (
            "Disp. hídrica",
            f"{media_disponibilidade:.1f}%".replace(".", ","),
            _formatar_delta(disponibilidade_recente, disponibilidade_anterior),
        ),
        (
            "Outorgas (%)",
            f"{comprometimento:.1f}%".replace(".", ","),
            _formatar_delta(uso_recente, uso_anterior),
        ),
        (
            "Estações",
            f"{int(estacoes['Status'].eq('Ativa').sum())}/{len(estacoes)}",
            None,
        ),
    ]

    colunas = st.columns(5, gap="small")
    for coluna, (rotulo, valor, delta) in zip(colunas, metricas):
        with coluna:
            st.metric(rotulo, valor, delta, delta_color="off", border=True)
    st.caption(
        "Variações comparam os três anos mais recentes com o triênio anterior."
    )


def _exibir_mapa(dados: pd.DataFrame, estacoes: pd.DataFrame) -> None:
    st.subheader("Explorador geográfico")
    coluna_filtros, coluna_mapa = st.columns([1, 2.3], gap="large")
    bacias = ["Todas as bacias"] + sorted(dados["Bacia"].unique().tolist())
    status_opcoes = ["Todos"] + sorted(estacoes["Status"].unique().tolist())

    with coluna_filtros:
        with st.container(border=True):
            st.markdown("**Filtros do mapa**")
            bacia_mapa = st.selectbox(
                "Bacia hidrográfica",
                bacias,
                key="mapa_bacia",
            )
            status_mapa = st.selectbox(
                "Status da estação",
                status_opcoes,
                key="mapa_status",
            )
            anos_mapa = st.slider(
                "Período",
                min_value=int(dados["Ano"].min()),
                max_value=int(dados["Ano"].max()),
                value=(2015, int(dados["Ano"].max())),
                key="mapa_anos",
            )
            st.caption(
                "Os filtros deste mapa são independentes dos filtros da análise."
            )

    mapa_dados = dados[dados["Ano"].between(anos_mapa[0], anos_mapa[1])]
    if bacia_mapa != "Todas as bacias":
        mapa_dados = mapa_dados[mapa_dados["Bacia"] == bacia_mapa]
    if status_mapa != "Todos":
        mapa_dados = mapa_dados[mapa_dados["Status"] == status_mapa]

    if mapa_dados.empty:
        with coluna_mapa:
            st.warning("Nenhuma estação corresponde aos filtros selecionados.")
        return

    resumo_estacoes = (
        mapa_dados.groupby(
            ["Bacia", "Estacao", "Status", "Lat", "Lon"],
            as_index=False,
        )
        .agg(
            Vazao_m3s=("Vazao_m3s", "mean"),
            Precipitacao_mm=("Precipitacao_mm", "mean"),
            Disponibilidade_Pct=("Disponibilidade_Pct", "mean"),
            Disponibilidade_m3s=("Disponibilidade_m3s", "mean"),
            Demanda_Outorga_m3s=("Demanda_Outorga_m3s", "mean"),
        )
    )
    resumo_estacoes["Criticidade_pct"] = (
        resumo_estacoes["Demanda_Outorga_m3s"]
        / resumo_estacoes["Disponibilidade_m3s"].clip(lower=0.1)
        * 100
    )

    with coluna_mapa:
        camada = st.segmented_control(
            "Camada visual",
            options=["Estações", "Disponibilidade", "Criticidade"],
            default="Estações",
            key="mapa_camada",
        )
        if camada == "Estações":
            figura = px.scatter_map(
                resumo_estacoes,
                lat="Lat",
                lon="Lon",
                size="Vazao_m3s",
                color="Status",
                hover_name="Estacao",
                hover_data={
                    "Bacia": True,
                    "Vazao_m3s": ":.1f",
                    "Precipitacao_mm": ":.1f",
                    "Lat": False,
                    "Lon": False,
                },
                color_discrete_map={
                    "Ativa": PALETA["azul"],
                    "Intermitente": PALETA["ambar"],
                    "Inativa": "#94A3B8",
                },
                size_max=16,
                zoom=5.1,
                map_style="carto-positron",
            )
        else:
            coluna_cor = (
                "Disponibilidade_Pct"
                if camada == "Disponibilidade"
                else "Criticidade_pct"
            )
            rotulo_cor = (
                "Disponibilidade (%)"
                if camada == "Disponibilidade"
                else "Comprometimento (%)"
            )
            figura = px.scatter_map(
                resumo_estacoes,
                lat="Lat",
                lon="Lon",
                size="Vazao_m3s",
                color=coluna_cor,
                hover_name="Estacao",
                hover_data={
                    "Bacia": True,
                    "Status": True,
                    "Vazao_m3s": ":.1f",
                    "Lat": False,
                    "Lon": False,
                },
                color_continuous_scale=[
                    PALETA["ambar"],
                    PALETA["azul_claro"],
                    PALETA["marinho"],
                ],
                labels={coluna_cor: rotulo_cor},
                size_max=16,
                zoom=5.1,
                map_style="carto-positron",
            )
        figura.update_layout(
            height=440,
            margin=dict(l=0, r=0, t=0, b=0),
            paper_bgcolor="white",
        )
        st.plotly_chart(
            figura,
            width="stretch",
            alt="Estações hidrológicas e indicadores selecionados no Cerrado goiano",
        )

        if bacia_mapa == "Todas as bacias":
            dados_resumo = mapa_dados
            nome_resumo = "Bacias selecionadas"
        else:
            dados_resumo = mapa_dados
            nome_resumo = bacia_mapa
        indicadores = [
            (
                "Vazão média",
                f"{dados_resumo['Vazao_m3s'].mean():.1f} m³/s",
            ),
            (
                "Disponibilidade",
                f"{dados_resumo['Disponibilidade_Pct'].mean():.1f}%",
            ),
            (
                "Comprometimento",
                f"{_percentual_comprometimento(dados_resumo):.1f}%",
            ),
        ]
        st.caption(f"Resumo da seleção · {nome_resumo}")
        colunas_resumo = st.columns(3)
        for coluna, (rotulo, valor) in zip(colunas_resumo, indicadores):
            with coluna:
                st.html(
                    f"""
                    <div class="summary-card">
                        <span>{rotulo}</span>
                        <strong>{valor}</strong>
                    </div>
                    """
                )


def _exibir_area_empilhada(dados: pd.DataFrame) -> None:
    anual = (
        dados.groupby("Ano", as_index=False)
        .agg(
            Vazao_natural=("Vazao_m3s", "mean"),
            Disponibilidade=("Disponibilidade_m3s", "mean"),
            Demanda=("Demanda_Outorga_m3s", "mean"),
        )
    )
    anual["Demanda_comprometida"] = np.minimum(
        anual["Demanda"],
        anual["Disponibilidade"],
    )
    anual["Disponibilidade_liquida"] = (
        anual["Disponibilidade"] - anual["Demanda_comprometida"]
    ).clip(lower=0)
    anual["Parcela_indisponivel"] = (
        anual["Vazao_natural"] - anual["Disponibilidade"]
    ).clip(lower=0)

    figura = go.Figure()
    camadas = [
        ("Disponibilidade líquida", "Disponibilidade_liquida", PALETA["marinho"]),
        ("Demanda comprometida", "Demanda_comprometida", PALETA["azul_claro"]),
        ("Parcela indisponível", "Parcela_indisponivel", PALETA["ambar"]),
    ]
    for nome, coluna, cor in camadas:
        figura.add_trace(
            go.Scatter(
                x=anual["Ano"],
                y=anual[coluna],
                name=nome,
                mode="lines",
                stackgroup="agua",
                line=dict(color=cor, width=1.5),
                fillcolor=cor,
                hovertemplate="%{x}: %{y:.1f} m³/s<extra>%{fullData.name}</extra>",
            )
        )
    figura.update_layout(
        title="Disponibilidade, demanda e parcela indisponível",
        xaxis_title="Ano",
        yaxis_title="Vazão média (m³/s)",
    )
    st.plotly_chart(
        _finalizar_figura(figura, 360),
        width="stretch",
        alt="Evolução anual da disponibilidade hídrica, demanda e parcela indisponível",
    )


def _exibir_serie_e_ranking(dados: pd.DataFrame, dados_completos: pd.DataFrame, coluna: str, rotulo: str) -> None:
    serie_anual = dados.groupby("Ano", as_index=False)[coluna].mean()
    normal_min = float(dados[coluna].quantile(0.25))
    normal_max = float(dados[coluna].quantile(0.75))
    anos_serie = serie_anual["Ano"].tolist()
    figura_serie = go.Figure()
    figura_serie.add_trace(
        go.Scatter(
            x=anos_serie + anos_serie[::-1],
            y=[normal_max] * len(anos_serie) + [normal_min] * len(anos_serie),
            fill="toself",
            fillcolor="rgba(59, 130, 246, 0.13)",
            line=dict(color="rgba(0,0,0,0)"),
            name="Faixa de normalidade (P25–P75)",
            hoverinfo="skip",
        )
    )
    figura_serie.add_trace(
        go.Scatter(
            x=serie_anual["Ano"],
            y=serie_anual[coluna],
            mode="lines+markers",
            name=rotulo,
            line=dict(color=PALETA["azul"], width=2.5),
        )
    )
    for inicio, fim in [(2015, 2016), (2019, 2020)]:
        if anos_serie and inicio <= max(anos_serie) and fim >= min(anos_serie):
            figura_serie.add_vrect(
                x0=max(inicio, min(anos_serie)) - 0.4,
                x1=min(fim, max(anos_serie)) + 0.4,
                fillcolor="rgba(229, 169, 59, 0.17)",
                line_width=0,
                annotation_text="seca",
                annotation_position="top left",
            )
    figura_serie.update_layout(
        title=f"Série histórica · {rotulo}",
        xaxis_title="Ano",
        yaxis_title=rotulo,
    )

    ranking = (
        dados_completos.groupby("Bacia", as_index=False)[coluna]
        .mean()
        .sort_values(coluna, ascending=True)
    )
    figura_ranking = px.bar(
        ranking,
        x=coluna,
        y="Bacia",
        orientation="h",
        color_discrete_sequence=[PALETA["marinho"]],
        labels={"Bacia": "", coluna: rotulo},
        text_auto=".1f",
    )
    figura_ranking.update_layout(
        title="Comparativo por bacia",
        xaxis_title=rotulo,
        yaxis_title="",
    )

    coluna_serie, coluna_ranking = st.columns(2, gap="large")
    with coluna_serie:
        with st.container(border=True):
            st.plotly_chart(
                _finalizar_figura(figura_serie),
                width="stretch",
                alt=f"Série histórica de {rotulo}, com faixa de normalidade e períodos críticos",
            )
    with coluna_ranking:
        with st.container(border=True):
            st.plotly_chart(
                _finalizar_figura(figura_ranking),
                width="stretch",
                alt=f"Ranking das bacias do Cerrado por {rotulo}",
            )


def _exibir_sazonalidade(
    dados: pd.DataFrame,
    coluna: str,
    rotulo: str,
    chave: str = "sazonalidade_visao",
) -> None:
    mensal = (
        dados.groupby(["Mes_Num", "Mes"], as_index=False)[coluna]
        .mean()
        .sort_values("Mes_Num")
    )
    meses_chuvosos = {10, 11, 12, 1, 2, 3}
    cores = [
        PALETA["azul"] if mes in meses_chuvosos else PALETA["ambar"]
        for mes in mensal["Mes_Num"]
    ]
    figura = go.Figure(
        go.Bar(
            x=mensal["Mes"],
            y=mensal[coluna],
            marker_color=cores,
            name=rotulo,
            hovertemplate="%{x}: %{y:.1f}<extra></extra>",
        )
    )
    figura.add_hline(
        y=float(mensal[coluna].mean()),
        line_dash="dash",
        line_color=PALETA["marinho"],
        annotation_text="Média do período",
    )
    figura.update_layout(
        title=f"Comportamento sazonal · {rotulo}",
        xaxis_title="Mês",
        yaxis_title=rotulo,
    )
    st.plotly_chart(
        _finalizar_figura(figura),
        width="stretch",
        alt=f"Variação mensal de {rotulo}, com meses chuvosos em azul e meses de estiagem em âmbar",
        key=chave,
    )


def _exibir_complementar(dados: pd.DataFrame) -> None:
    coluna_curva, coluna_uso = st.columns(2, gap="large")
    vazoes = dados["Vazao_m3s"].dropna().sort_values(ascending=False).reset_index(drop=True)
    permanencia = (np.arange(1, len(vazoes) + 1) / (len(vazoes) + 1)) * 100
    figura_curva = go.Figure(
        go.Scatter(
            x=permanencia,
            y=vazoes,
            mode="lines",
            line=dict(color=PALETA["azul"], width=2.5),
            name="Vazão observada",
        )
    )
    figura_curva.update_layout(
        title="Curva de permanência de vazões",
        xaxis_title="Permanência (%)",
        yaxis_title="Vazão (m³/s)",
    )
    with coluna_curva:
        with st.container(border=True):
            st.plotly_chart(
                _finalizar_figura(figura_curva),
                width="stretch",
                alt="Curva de permanência das vazões observadas no período selecionado",
            )
            st.caption(
                "A curva mostra a vazão igualada ou superada em cada percentual do tempo; "
                "valores menores à direita sinalizam condições de menor disponibilidade."
            )

    comprometimento = _percentual_comprometimento(dados)
    comprometimento_exibido = min(comprometimento, 100.0)
    figura_rosca = go.Figure(
        go.Pie(
            labels=["Comprometido", "Disponível remanescente"],
            values=[comprometimento_exibido, 100 - comprometimento_exibido],
            hole=0.72,
            marker_colors=[PALETA["ambar"], PALETA["azul"]],
            textinfo="label+percent",
            sort=False,
        )
    )
    figura_rosca.update_layout(
        title="Comprometimento hídrico estimado",
        showlegend=False,
    )
    with coluna_uso:
        with st.container(border=True):
            st.plotly_chart(
                _finalizar_figura(figura_rosca, 300),
                width="stretch",
                alt=f"Comprometimento hídrico estimado em {comprometimento:.1f} por cento",
            )
            st.progress(
                int(comprometimento_exibido),
                text=f"{comprometimento:.1f}% da disponibilidade comprometida",
            )
            if comprometimento > 100:
                st.caption(
                    "A demanda estimada supera a disponibilidade média no recorte."
                )


def _exibir_tabela(dados: pd.DataFrame) -> None:
    tabela = (
        dados.groupby(["Bacia", "Ano"], as_index=False)
        .agg(
            Vazao_media_m3s=("Vazao_m3s", "mean"),
            Disponibilidade_media_pct=("Disponibilidade_Pct", "mean"),
            Demanda_media_m3s=("Demanda_Outorga_m3s", "mean"),
        )
    )
    precipitacao_anual = (
        dados.groupby(["Bacia", "Ano", "Estacao"], as_index=False)
        .agg(Precipitacao_mm=("Precipitacao_mm", "sum"))
        .groupby(["Bacia", "Ano"], as_index=False)
        .agg(Precipitacao_anual_mm=("Precipitacao_mm", "mean"))
    )
    tabela = tabela.merge(precipitacao_anual, on=["Bacia", "Ano"], how="left")
    tabela["Ano"] = tabela["Ano"].astype(str)
    colunas_numericas = [
        "Vazao_media_m3s",
        "Disponibilidade_media_pct",
        "Demanda_media_m3s",
        "Precipitacao_anual_mm",
    ]
    linha_media = {coluna: tabela[coluna].mean() for coluna in colunas_numericas}
    linha_media.update({"Bacia": "Média geral", "Ano": "Média"})
    tabela = pd.concat([tabela, pd.DataFrame([linha_media])], ignore_index=True)
    tabela = tabela.round(2)
    tabela_formatada = tabela.style.apply(
        lambda linha: [
            "background-color: #EAF2F8; font-weight: bold"
            if linha.name == len(tabela) - 1
            else ""
            for _ in linha
        ],
        axis=1,
    )
    st.dataframe(
        tabela_formatada,
        hide_index=True,
        alt="Tabela consolidada de indicadores hidrológicos por bacia e ano",
    )
    st.download_button(
        "Baixar tabela consolidada (CSV)",
        data=tabela.to_csv(index=False).encode("utf-8-sig"),
        file_name="dashidro_resumo_por_bacia_ano.csv",
        mime="text/csv",
        icon=":material/download:",
    )


def _exibir_comparativo(dados: pd.DataFrame, coluna: str, rotulo: str) -> None:
    ano_inicio = int(dados["Ano"].min())
    ano_fim = int(dados["Ano"].max())
    ponto_divisao = (ano_inicio + ano_fim) // 2
    periodo_inicial = dados[dados["Ano"] <= ponto_divisao]
    periodo_recente = dados[dados["Ano"] > ponto_divisao]

    if periodo_recente.empty or periodo_inicial.empty:
        st.info("Selecione pelo menos dois anos para comparar períodos distintos.")
        return

    nome_inicial = f"{ano_inicio}–{ponto_divisao}"
    nome_recente = f"{ponto_divisao + 1}–{ano_fim}"
    valor_inicial = float(periodo_inicial[coluna].mean())
    valor_recente = float(periodo_recente[coluna].mean())
    st.caption(f"Indicador comparado: {rotulo}")
    col_inicial, col_recente = st.columns(2, gap="medium")
    with col_inicial:
        with st.container(border=True):
            st.metric(nome_inicial, f"{valor_inicial:.1f}")
    with col_recente:
        with st.container(border=True):
            st.metric(
                nome_recente,
                f"{valor_recente:.1f}",
                _formatar_delta(valor_recente, valor_inicial),
                delta_color="off",
            )

    mensal_inicial = periodo_inicial.groupby("Mes_Num", as_index=False)[coluna].mean()
    mensal_recente = periodo_recente.groupby("Mes_Num", as_index=False)[coluna].mean()
    figura = go.Figure()
    figura.add_trace(
        go.Scatter(
            x=mensal_inicial["Mes_Num"],
            y=mensal_inicial[coluna],
            name=nome_inicial,
            mode="lines+markers",
            line=dict(color=PALETA["azul"], width=2.5),
        )
    )
    figura.add_trace(
        go.Scatter(
            x=mensal_recente["Mes_Num"],
            y=mensal_recente[coluna],
            name=nome_recente,
            mode="lines+markers",
            line=dict(color=PALETA["ambar"], width=2.5),
        )
    )
    figura.update_layout(
        title=f"Perfil mensal comparado · {rotulo}",
        xaxis=dict(
            tickmode="array",
            tickvals=list(range(1, 13)),
            ticktext=MESES,
        ),
        yaxis_title=rotulo,
    )
    st.plotly_chart(
        _finalizar_figura(figura),
        width="stretch",
        alt=f"Comparação mensal de {rotulo} entre {nome_inicial} e {nome_recente}",
    )
    st.caption(
        "Os intervalos são divididos automaticamente no ponto médio dos anos selecionados. "
        "Dados simulados para demonstração; não representam medições oficiais."
    )


def renderizar_painel() -> None:
    dados = carregar_dados()
    estacoes = carregar_estacoes()

    st.html(
        """
        <header class="dashidro-hero">
            <p class="eyebrow">DASHIDRO · OBSERVATÓRIO HIDROLÓGICO · LPICS / UEG</p>
            <h1>O que você precisa saber sobre as águas do Cerrado hoje?</h1>
            <p>Informação hidrológica para compreender a disponibilidade e os usos da água em Goiás.</p>
        </header>
        """
    )

    st.subheader("Perguntas que orientam o painel")
    _exibir_perguntas()

    st.subheader("Indicadores principais")
    _exibir_kpis(dados, estacoes)
    st.caption("Indicadores calculados a partir da base sintética de demonstração.")

    _exibir_mapa(dados, estacoes)

    st.subheader("Diagnóstico analítico e séries temporais")
    bacias = ["Todas as bacias"] + sorted(dados["Bacia"].unique().tolist())
    col_filtro_bacia, col_filtro_variavel, col_filtro_anos, col_download = st.columns(
        [1.35, 1.4, 2.1, 1.05],
        gap="small",
        vertical_alignment="bottom",
    )
    with col_filtro_bacia:
        bacia_analise = st.selectbox(
            "Bacia da análise",
            bacias,
            key="analise_bacia",
        )
    with col_filtro_variavel:
        rotulo_variavel = st.selectbox(
            "Variável principal",
            list(VARIAVEIS),
            key="analise_variavel",
        )
    with col_filtro_anos:
        intervalo_anos = st.slider(
            "Intervalo de anos",
            min_value=int(dados["Ano"].min()),
            max_value=int(dados["Ano"].max()),
            value=(2005, int(dados["Ano"].max())),
            key="analise_anos",
        )

    coluna_variavel = VARIAVEIS[rotulo_variavel]
    dados_analise = dados[dados["Ano"].between(*intervalo_anos)].copy()
    if bacia_analise != "Todas as bacias":
        dados_analise = dados_analise[dados_analise["Bacia"] == bacia_analise]
    if dados_analise.empty:
        st.warning("Não há dados para os filtros da análise.")
        exibir_rodape()
        return

    with col_download:
        st.download_button(
            "Baixar CSV",
            data=dados_analise.to_csv(index=False).encode("utf-8-sig"),
            file_name="dashidro_dados_filtrados.csv",
            mime="text/csv",
            icon=":material/download:",
            width="stretch",
        )

    aba_geral, aba_vazao, aba_outorgas = st.tabs(
        ["Visão geral", "Vazão & chuva", "Outorgas & demanda"]
    )
    with aba_geral:
        st.markdown("**Resumo do recorte**")
        valor_variavel = float(dados_analise[coluna_variavel].mean())
        comprometimento = _percentual_comprometimento(dados_analise)
        mini_colunas = st.columns(4, gap="small")
        mini_metricas = [
            (
                ":blue[:material/water_drop:] Vazão média",
                f"{dados_analise['Vazao_m3s'].mean():.1f} m³/s",
                "mini_vazao",
            ),
            (
                ":orange[:material/cloud:] Chuva média",
                f"{dados_analise['Precipitacao_mm'].mean():.0f} mm/mês",
                "mini_chuva",
            ),
            (
                ":blue[:material/check_circle:] Disponibilidade",
                f"{dados_analise['Disponibilidade_Pct'].mean():.1f}%",
                "mini_disponibilidade",
            ),
            (
                ":orange[:material/warning:] Comprometimento",
                f"{comprometimento:.1f}%",
                "mini_outorgas",
            ),
        ]
        for coluna, (rotulo, valor, chave) in zip(mini_colunas, mini_metricas):
            with coluna:
                with st.container(border=True, key=chave):
                    st.metric(rotulo, valor)

        _exibir_area_empilhada(dados_analise)
        _exibir_serie_e_ranking(
            dados_analise,
            dados[dados["Ano"].between(*intervalo_anos)],
            coluna_variavel,
            rotulo_variavel,
        )
        _exibir_sazonalidade(dados_analise, coluna_variavel, rotulo_variavel)
        _exibir_complementar(dados_analise)

        st.markdown("**Tabela consolidada por bacia e ano**")
        _exibir_tabela(dados_analise)

        st.markdown("**Comparativo de períodos**")
        _exibir_comparativo(dados_analise, coluna_variavel, rotulo_variavel)
        st.caption(f"Variável selecionada: {valor_variavel:.1f} · {rotulo_variavel}.")

    with aba_vazao:
        st.markdown("**Relação mensal entre vazão e precipitação**")
        mensal = (
            dados_analise.groupby(["Mes_Num", "Mes"], as_index=False)
            .agg(
                Vazao_m3s=("Vazao_m3s", "mean"),
                Precipitacao_mm=("Precipitacao_mm", "mean"),
            )
            .sort_values("Mes_Num")
        )
        figura = go.Figure()
        figura.add_trace(
            go.Scatter(
                x=mensal["Mes"],
                y=mensal["Vazao_m3s"],
                name="Vazão (m³/s)",
                mode="lines+markers",
                line=dict(color=PALETA["azul"], width=2.5),
            )
        )
        figura.add_trace(
            go.Scatter(
                x=mensal["Mes"],
                y=mensal["Precipitacao_mm"],
                name="Precipitação (mm)",
                mode="lines+markers",
                yaxis="y2",
                line=dict(color=PALETA["ambar"], width=2.5),
            )
        )
        figura.update_layout(
            title="Sazonalidade de vazão e chuva",
            yaxis=dict(title="Vazão (m³/s)"),
            yaxis2=dict(title="Precipitação (mm)", overlaying="y", side="right"),
        )
        st.plotly_chart(
            _finalizar_figura(figura, 390),
            width="stretch",
            alt="Sazonalidade mensal comparando vazão dos rios e precipitação",
        )
        _exibir_sazonalidade(
            dados_analise,
            "Vazao_m3s",
            "Vazão média (m³/s)",
            chave="sazonalidade_vazao",
        )

    with aba_outorgas:
        st.markdown("**Pressão de uso e demanda outorgada**")
        anual = (
            dados_analise.groupby("Ano", as_index=False)
            .agg(
                Disponibilidade=("Disponibilidade_m3s", "mean"),
                Demanda=("Demanda_Outorga_m3s", "mean"),
            )
        )
        figura = go.Figure()
        figura.add_trace(
            go.Scatter(
                x=anual["Ano"],
                y=anual["Disponibilidade"],
                name="Disponibilidade (m³/s)",
                mode="lines",
                line=dict(color=PALETA["azul"], width=2.5),
            )
        )
        figura.add_trace(
            go.Scatter(
                x=anual["Ano"],
                y=anual["Demanda"],
                name="Demanda/outorgas (m³/s)",
                mode="lines",
                line=dict(color=PALETA["ambar"], width=2.5),
            )
        )
        figura.update_layout(
            title="Disponibilidade e demanda ao longo do tempo",
            xaxis_title="Ano",
            yaxis_title="Vazão média (m³/s)",
        )
        st.plotly_chart(
            _finalizar_figura(figura, 390),
            width="stretch",
            alt="Evolução anual da disponibilidade hídrica e da demanda por outorgas",
        )
        ranking_uso = (
            dados[dados["Ano"].between(*intervalo_anos)]
            .groupby("Bacia")
            .apply(_percentual_comprometimento, include_groups=False)
            .rename("Comprometimento_pct")
            .reset_index()
            .sort_values("Comprometimento_pct", ascending=True)
        )
        figura_uso = px.bar(
            ranking_uso,
            x="Comprometimento_pct",
            y="Bacia",
            orientation="h",
            color_discrete_sequence=[PALETA["ambar"]],
            labels={"Comprometimento_pct": "Comprometimento (%)", "Bacia": ""},
            text_auto=".1f",
        )
        figura_uso.update_layout(title="Comprometimento estimado por bacia")
        st.plotly_chart(
            _finalizar_figura(figura_uso, 300),
            width="stretch",
            alt="Ranking de comprometimento hídrico estimado por bacia",
        )

    exibir_rodape()
