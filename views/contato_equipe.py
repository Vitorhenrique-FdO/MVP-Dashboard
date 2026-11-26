import streamlit as st

from utils.tema import exibir_rodape


def renderizar_contato() -> None:
    st.title("Contato & equipe", icon=":material/groups:")
    st.caption("Conheça o laboratório responsável e entre em contato com o projeto.")

    coluna_lab, coluna_equipe = st.columns([1.1, 1], gap="large")
    with coluna_lab:
        with st.container(border=True):
            st.subheader("LPICS · UEG")
            st.write(
                "O DASHIDRO é apresentado como iniciativa do LPICS, da Universidade "
                "Estadual de Goiás (UEG), dedicada à organização "
                "e comunicação de informações "
                "sobre as águas do Cerrado."
            )
            st.link_button(
                "Universidade Estadual de Goiás",
                "https://www.ueg.br/",
                icon=":material/open_in_new:",
            )

    with coluna_equipe:
        with st.container(border=True):
            st.subheader("Equipe do projeto")
            st.markdown(
                """
                - **Coordenação científica:** LPICS / UEG
                - **Dados hidrológicos e metodologia:** equipe DASHIDRO
                - **Desenvolvimento e visualização:** equipe do projeto
                """
            )

    st.subheader("Links de referência")
    links = st.columns(3, gap="small")
    with links[0]:
        st.link_button(
            "Agência Nacional de Águas (ANA)",
            "https://www.gov.br/ana/",
            width="stretch",
        )
    with links[1]:
        st.link_button(
            "INMET",
            "https://portal.inmet.gov.br/",
            width="stretch",
        )
    with links[2]:
        st.link_button(
            "MapBiomas",
            "https://brasil.mapbiomas.org/",
            width="stretch",
        )

    st.subheader("Fale com o projeto")
    with st.form("formulario_contato", border=True):
        nome = st.text_input("Nome")
        email = st.text_input("E-mail")
        assunto = st.text_input("Assunto")
        mensagem = st.text_area("Mensagem", height=140)
        enviado = st.form_submit_button(
            "Validar mensagem",
            type="primary",
            icon=":material/send:",
        )

    if enviado:
        if not all(campo.strip() for campo in (nome, email, assunto, mensagem)):
            st.error("Preencha todos os campos para continuar.")
        elif "@" not in email or "." not in email.rsplit("@", 1)[-1]:
            st.error("Informe um endereço de e-mail válido.")
        else:
            st.success("Mensagem validada.")

    exibir_rodape()
