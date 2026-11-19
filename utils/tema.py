import streamlit as st

PALETA = {
    "marinho": "#0B2C4D",
    "azul": "#1E6BB8",
    "azul_claro": "#3B82F6",
    "ambar": "#E5A93B",
    "texto": "#334155",
    "borda": "#E2E8F0",
    "fundo": "#F4F7FA",
    "branco": "#FFFFFF",
}


def aplicar_estilos() -> None:
    st.html(
        """
        <style>
        .dashidro-hero {
            background: linear-gradient(110deg, #0B2C4D 0%, #164875 100%);
            color: #FFFFFF;
            border-radius: 14px;
            padding: 1.7rem 2rem;
            margin: 0 0 1.4rem;
        }
        .dashidro-hero .eyebrow {
            color: #CBD5E1;
            font-size: .78rem;
            font-weight: 700;
            letter-spacing: .12em;
            margin: 0 0 .45rem;
        }
        .dashidro-hero h1 {
            color: #FFFFFF;
            font-size: clamp(1.45rem, 2.5vw, 2rem);
            line-height: 1.2;
            margin: 0;
        }
        .dashidro-hero p {
            color: #D8E4F0;
            margin: .55rem 0 0;
        }
        .question-card {
            background: #FFFFFF;
            border: 1px solid #E2E8F0;
            border-top: 4px solid #E5A93B;
            border-radius: 12px;
            box-shadow: 0 2px 8px rgba(11, 44, 77, .05);
            height: 100%;
            min-height: 142px;
            padding: 1rem 1.1rem;
        }
        .question-card h3 {
            color: #0B2C4D;
            font-size: 1rem;
            margin: .45rem 0;
        }
        .question-card p {
            color: #475569;
            font-size: .88rem;
            margin: 0;
        }
        .question-number {
            color: #1E6BB8;
            font-size: .76rem;
            font-weight: 700;
            letter-spacing: .08em;
        }
        .summary-card {
            background: #FFFFFF;
            border: 1px solid #E2E8F0;
            border-radius: 10px;
            box-shadow: 0 1px 5px rgba(11, 44, 77, .05);
            padding: .8rem 1rem;
        }
        .summary-card span {
            color: #64748B;
            display: block;
            font-size: .78rem;
        }
        .summary-card strong {
            color: #0B2C4D;
            display: block;
            font-size: 1.2rem;
            margin-top: .2rem;
        }
        .st-key-mini_vazao,
        .st-key-mini_disponibilidade {
            border-left: 4px solid #1E6BB8;
            border-radius: 10px;
            padding-left: .45rem;
        }
        .st-key-mini_chuva,
        .st-key-mini_outorgas {
            border-left: 4px solid #E5A93B;
            border-radius: 10px;
            padding-left: .45rem;
        }
        .st-key-sidebar_logo img {
            height: 72px;
            object-fit: cover;
            object-position: center;
            width: 100%;
        }
        .st-key-nav_painel_selecionado button,
        .st-key-nav_dados_selecionado button,
        .st-key-nav_contato_selecionado button {
            background: #FFFFFF !important;
            border: 1px solid #FFFFFF !important;
            color: #0B2C4D !important;
            justify-content: flex-start !important;
        }
        .st-key-nav_painel_selecionado button *,
        .st-key-nav_dados_selecionado button *,
        .st-key-nav_contato_selecionado button * {
            color: #0B2C4D !important;
        }
        .st-key-nav_painel_normal button,
        .st-key-nav_dados_normal button,
        .st-key-nav_contato_normal button {
            background: rgba(255, 255, 255, .08) !important;
            border: 1px solid rgba(255, 255, 255, .32) !important;
            color: #FFFFFF !important;
            justify-content: flex-start !important;
        }
        .st-key-nav_painel_normal button *,
        .st-key-nav_dados_normal button *,
        .st-key-nav_contato_normal button * {
            color: #FFFFFF !important;
        }
        .institutional-footer {
            background: #0B2C4D;
            border-radius: 10px;
            color: #FFFFFF;
            margin-top: 2rem;
            padding: 1rem 1.2rem;
            text-align: center;
        }
        .institutional-footer span {
            color: #CBD5E1;
            display: block;
            font-size: .82rem;
            margin-top: .2rem;
        }
        .sidebar-institution {
            color: #D8E4F0;
            font-size: .78rem;
            line-height: 1.5;
            margin-top: 2rem;
        }
        .sidebar-institution strong {
            color: #FFFFFF;
        }
        .sidebar-institution hr {
            border-color: #315574;
        }
        </style>
        """
    )


def exibir_rodape() -> None:
    st.html(
        """
        <footer class="institutional-footer">
            <strong>DASHIDRO · Conhecer o Cerrado pelas suas águas</strong>
            <span>Laboratório LPICS · Universidade Estadual de Goiás (UEG)</span>
        </footer>
        """
    )
