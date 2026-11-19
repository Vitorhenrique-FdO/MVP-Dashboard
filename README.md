# DASHIDRO · Observatório Hidrológico do Cerrado

Aplicação Streamlit para explorar indicadores hidrológicos das bacias goianas do
Meia Ponte, Corumbá, Vermelho e Paranã.

## Executar

Ative o ambiente Python do projeto e inicie o Streamlit:

```powershell
.\.venv\Scripts\streamlit.exe run app.py
```

## Estrutura

- `app.py`: identidade global e roteamento das páginas.
- `views/`: painel hidrológico, base/metodologia e contato/equipe.
- `utils/dados.py`: base sintética compartilhada e cache de dados.
- `utils/tema.py`: paleta e identidade visual compartilhada.
- `.streamlit/config.toml`: tema claro e cores do DASHIDRO.

## Dados

O painel é preenchido por dados simulados para demonstração. Eles não representam
medições oficiais nem devem ser usados para decisões operacionais. A função
`carregar_dados()` em `utils/dados.py` centraliza a geração da série; ela pode ser
substituída por um carregador de CSV ou por integrações com fontes oficiais.