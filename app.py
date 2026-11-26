from pathlib import Path

import streamlit as st

from utils.tema import aplicar_estilos

BASE_DIR = Path(__file__).parent

st.set_page_config(
    page_title="DASHIDRO · Observatório Hidrológico do Cerrado",
    page_icon=":material/water_drop:",
    layout="wide",
    initial_sidebar_state="expanded",
)

aplicar_estilos()

PAGINAS = {
    "Painel Hidrológico": "painel",
    "Base de Dados & Metodologia": "dados",
    "Contato & Equipe": "contato",
    "Peixárea": "peixarea",
    "Explore as bacias": "explore_bacias",
    "Viagem pelo tempo": "viagem_tempo",
}
PAGINAS_SIDEBAR = {
    titulo: identificador
    for titulo, identificador in PAGINAS.items()
    if identificador in {"painel", "dados", "contato"}
}

if "pagina_global" not in st.session_state:
    st.session_state["pagina_global"] = "Painel Hidrológico"


def selecionar_pagina(pagina: str) -> None:
    st.session_state["pagina_global"] = pagina


with st.sidebar:
    with st.container(key="sidebar_logo"):
        st.image(
            str(BASE_DIR / "imagens" / "DASHIDRO-logo.png"),
            width=220,
            alt="Logo DASHIDRO",
        )
    st.caption("Observatório Hidrológico do Cerrado")
    for titulo, identificador in PAGINAS_SIDEBAR.items():
        estado = (
            "selecionado"
            if st.session_state["pagina_global"] == titulo
            else "normal"
        )
        with st.container(key=f"nav_{identificador}_{estado}"):
            st.button(
                titulo,
                key=f"botao_{identificador}",
                on_click=selecionar_pagina,
                args=(titulo,),
                width="stretch",
            )
    st.markdown(
        """
        <div class="sidebar-institution">
            <strong>UEG · LPICS</strong><br>
            <span>Laboratório LPICS</span>
            <hr>
        </div>
        """,
        unsafe_allow_html=True,
    )

if PAGINAS[st.session_state["pagina_global"]] == "painel":
    from views.painel_hidrologico import renderizar_painel

    renderizar_painel()
elif PAGINAS[st.session_state["pagina_global"]] == "dados":
    from views.base_metodologia import renderizar_base

    renderizar_base()
elif PAGINAS[st.session_state["pagina_global"]] == "contato":
    from views.contato_equipe import renderizar_contato

    renderizar_contato()
else:
    st.write("Área em desenvolvimento")
