
import calendar
from collections import Counter
from datetime import date

import requests
import pandas as pd
import streamlit as st
import plotly.express as px

# =========================================================
# CONFIGURAÇÃO
# =========================================================

BASE = "https://dadosabertos.camara.leg.br/api/v2"
TIMEOUT = 30
LIMITE_AUTORES = 100
ITENS_POR_PAGINA = 100

st.set_page_config(
    page_title="Painel Legislativo",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# =========================================================
# ESTILO VISUAL
# =========================================================

st.markdown("""
<style>
    .stApp {
        background-color: #f4f6fa;
    }

    [data-testid="stHeader"] {
        background-color: rgba(244,246,250,0.92);
    }

    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #111c35 0%, #1b3157 100%);
    }

    /* Texto geral da barra lateral */
    [data-testid="stSidebar"] * {
        color: #f4f7ff;
    }

    /* CORREÇÃO: campos de entrada com texto escuro */
    [data-testid="stSidebar"] input,
    [data-testid="stSidebar"] textarea,
    [data-testid="stSidebar"] [data-baseweb="input"] input,
    [data-testid="stSidebar"] [data-baseweb="textarea"] textarea {
        color: #182b49 !important;
        background-color: #ffffff !important;
        -webkit-text-fill-color: #182b49 !important;
        caret-color: #182b49 !important;
    }

    /* Texto de exemplo dos campos */
    [data-testid="stSidebar"] input::placeholder,
    [data-testid="stSidebar"] textarea::placeholder {
        color: #7b8798 !important;
        -webkit-text-fill-color: #7b8798 !important;
        opacity: 1;
    }

    /* Mantém os rótulos brancos */
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] [data-testid="stWidgetLabel"] {
        color: #f4f7ff !important;
    }

    .hero {
        background: linear-gradient(120deg, #142440, #244d78);
        padding: 30px;
        border-radius: 18px;
        color: white;
        margin-bottom: 24px;
        box-shadow: 0 8px 24px rgba(20,36,64,0.13);
    }

    .hero h1 {
        color: white;
        font-size: 30px;
        margin: 0 0 8px 0;
    }

    .hero p {
        color: #dce8f7;
        font-size: 15px;
        margin: 0;
    }

    div[data-testid="stMetric"] {
        background: white;
        border: 1px solid #e6eaf1;
        padding: 18px;
        border-radius: 14px;
        box-shadow: 0 3px 12px rgba(20,36,64,0.04);
    }

    div[data-testid="stMetricLabel"] {
        color: #52627a;
    }

    h2, h3 {
        color: #182b49;
    }

    div.stButton > button[kind="primary"] {
        background: #2d6cdf;
        color: white !important;
        border: none;
        border-radius: 10px;
        min-height: 45px;
        font-weight: 600;
    }

    div.stButton > button[kind="primary"]:hover {
        background: #1c53b7;
    }

    .section-note {
        color: #68778c;
        font-size: 13px;
    }

    footer {
        visibility: hidden;
    }
</style>
""", unsafe_allow_html=True)

# =========================================================
# CABEÇALHO
# =========================================================

st.markdown("""
<div class="hero">
    <h1>🏛️ Painel de Atividade Legislativa</h1>
    <p>
        Explore proposições da Câmara dos Deputados,
        acompanhe tendências e consulte seus autores.
    </p>
</div>
""", unsafe_allow_html=True)

# =========================================================
# FILTROS
# =========================================================

st.sidebar.markdown("## ⚙️ Configurações")
st.sidebar.caption("Personalize sua consulta legislativa.")

ano = st.sidebar.number_input(
    "Ano de apresentação",
    min_value=2000,
    max_value=2026,
    value=2025,
    step=1,
)

tema = st.sidebar.text_input(
    "Palavra-chave",
    value="saúde",
    help="A busca considera o texto da ementa retornada pela API.",
)

paginas = st.sidebar.slider(
    "Páginas consultadas por mês",
    min_value=1,
    max_value=10,
    value=3,
)

st.sidebar.info(
    "Cada página solicita até 100 registros por mês. "
    "A consulta anual percorre os 12 meses."
)

# =========================================================
# ACESSO À API
# =========================================================

def criar_sessao():
    sessao = requests.Session()
    sessao.headers.update({
        "Accept": "application/json",
        "User-Agent": "PainelLegislativo/1.0",
    })
    return sessao


@st.cache_data(ttl=3600, show_spinner=False)
def buscar_proposicoes(ano, paginas):
    registros = []
    ids_vistos = set()

    with criar_sessao() as sessao:
        for mes in range(1, 13):
            inicio = date(ano, mes, 1)
            ultimo_dia = calendar.monthrange(ano, mes)[1]
            fim = date(ano, mes, ultimo_dia)

            for pagina in range(1, paginas + 1):
                params = {
                    "dataInicio": inicio.isoformat(),
                    "dataFim": fim.isoformat(),
                    "pagina": pagina,
                    "itens": ITENS_POR_PAGINA,
                }

                resposta = sessao.get(
                    f"{BASE}/proposicoes",
                    params=params,
                    timeout=TIMEOUT,
                )

                if not resposta.ok:
                    raise RuntimeError(
                        f"API respondeu HTTP {resposta.status_code}. "
                        f"Detalhes: {resposta.text[:1000]}"
                    )

                try:
                    conteudo = resposta.json()
                except requests.exceptions.JSONDecodeError as erro:
                    raise RuntimeError(
                        "A API não retornou um JSON válido."
                    ) from erro

                dados = conteudo.get("dados", [])

                for registro in dados:
                    identificador = registro.get("id")

                    if identificador is None:
                        registros.append(registro)
                    elif identificador not in ids_vistos:
                        ids_vistos.add(identificador)
                        registros.append(registro)

                if len(dados) < ITENS_POR_PAGINA:
                    break

    return registros


@st.cache_data(ttl=3600, show_spinner=False)
def buscar_autores(id_proposicao):
    resposta = requests.get(
        f"{BASE}/proposicoes/{id_proposicao}/autores",
        headers={"Accept": "application/json"},
        timeout=TIMEOUT,
    )
    resposta.raise_for_status()
    return resposta.json().get("dados", [])


# =========================================================
# EXECUÇÃO DA CONSULTA
# =========================================================

if st.button(
    "🔎 Buscar proposições",
    type="primary",
    use_container_width=True,
):
    if not tema.strip():
        st.warning("Digite uma palavra-chave antes de pesquisar.")
        st.stop()

    try:
        with st.spinner("Consultando os dados legislativos..."):
            dados = buscar_proposicoes(int(ano), int(paginas))

        df = pd.DataFrame(dados)

        if df.empty:
            st.warning(
                "A API não retornou proposições no período consultado."
            )
            st.stop()

        if "ementa" not in df.columns:
            df["ementa"] = ""

        if "id" not in df.columns:
            st.error(
                "A resposta não contém o identificador das proposições."
            )
            st.stop()

        df["ementa"] = df["ementa"].fillna("").astype(str)

        if "dataApresentacao" in df.columns:
            df["dataApresentacao"] = pd.to_datetime(
                df["dataApresentacao"],
                errors="coerce",
            )
            df = df.sort_values(
                "dataApresentacao",
                ascending=True,
                na_position="last",
            )

        filtrado = df[
            df["ementa"].str.contains(
                tema.strip(),
                case=False,
                na=False,
                regex=False,
            )
        ].copy()

        st.session_state["resultado"] = filtrado
        st.session_state["ano_resultado"] = int(ano)
        st.session_state["tema_resultado"] = tema.strip()
        st.session_state["total_consultado"] = len(df)

    except (
        requests.RequestException,
        RuntimeError,
        ValueError,
    ) as erro:
        st.error(f"Não foi possível consultar a API: {erro}")
        st.stop()

# =========================================================
# APRESENTAÇÃO DOS RESULTADOS
# =========================================================

if "resultado" in st.session_state:
    filtrado = st.session_state["resultado"]
    ano_atual = st.session_state["ano_resultado"]
    tema_atual = st.session_state["tema_resultado"]
    total_consultado = st.session_state["total_consultado"]

    st.markdown("## 📊 Visão geral")

    m1, m2, m3 = st.columns(3)

    m1.metric(
        "Proposições consultadas",
        f"{total_consultado:,}".replace(",", "."),
    )
    m2.metric(
        "Correspondências",
        f"{len(filtrado):,}".replace(",", "."),
    )
    m3.metric("Ano selecionado", str(ano_atual))

    st.caption(
        f"Pesquisa por “{tema_atual}” · "
        "A busca considera as ementas das proposições consultadas."
    )

    if filtrado.empty:
        st.info(
            "Nenhuma correspondência encontrada. "
            "Tente outra palavra-chave ou consulte mais páginas."
        )
        st.stop()

    # =====================================================
    # GRÁFICO MENSAL
    # =====================================================

    st.markdown("## 📅 Evolução mensal")

    if "dataApresentacao" in filtrado.columns:
        datas_validas = filtrado.dropna(
            subset=["dataApresentacao"]
        ).copy()

        if not datas_validas.empty:
            meses = [
                "Jan", "Fev", "Mar", "Abr", "Mai", "Jun",
                "Jul", "Ago", "Set", "Out", "Nov", "Dez",
            ]

            mensal = (
                datas_validas.assign(
                    mes=datas_validas["dataApresentacao"].dt.month
                )
                .groupby("mes")
                .size()
                .reindex(range(1, 13), fill_value=0)
                .rename("Quantidade")
                .reset_index()
            )

            mensal["Mês"] = mensal["mes"].map(
                lambda n: meses[n - 1]
            )

            fig_mensal = px.bar(
                mensal,
                x="Mês",
                y="Quantidade",
                text="Quantidade",
                category_orders={"Mês": meses},
                color_discrete_sequence=["#3478d4"],
                labels={"Quantidade": "Proposições"},
                title=f"Proposições sobre {tema_atual} em {ano_atual}",
            )

            fig_mensal.update_layout(
                plot_bgcolor="white",
                paper_bgcolor="white",
                font=dict(color="#182b49"),
                margin=dict(l=20, r=20, t=60, b=20),
                xaxis_title="Mês",
                yaxis_title="Número de proposições",
            )

            st.plotly_chart(
                fig_mensal,
                use_container_width=True,
            )

    # =====================================================
    # RANKING DE AUTORES
    # =====================================================

    st.markdown("## 👥 Autores mais frequentes")

    amostra = filtrado.head(LIMITE_AUTORES)
    ranking = Counter()
    falhas = 0

    progresso = st.progress(0)
    status = st.empty()

    for i, (_, prop) in enumerate(amostra.iterrows()):
        try:
            autores = buscar_autores(int(prop["id"]))

            nomes = {
                autor.get("nome", "").strip()
                for autor in autores
                if isinstance(autor.get("nome"), str)
                and autor.get("nome", "").strip()
            }

            ranking.update(nomes)

        except (
            requests.RequestException,
            ValueError,
            TypeError,
        ):
            falhas += 1

        progresso.progress((i + 1) / len(amostra))
        status.caption(
            f"Consultando autoria: {i + 1} de {len(amostra)}"
        )

    progresso.empty()
    status.empty()

    if falhas:
        st.warning(
            f"Falha ao recuperar os autores de {falhas} proposição(ões). "
            "O ranking pode estar incompleto."
        )

    if ranking:
        ranking_df = pd.DataFrame(
            ranking.most_common(20),
            columns=["Autor", "Proposições"],
        )

        fig_autores = px.bar(
            ranking_df.sort_values("Proposições"),
            x="Proposições",
            y="Autor",
            orientation="h",
            text="Proposições",
            color_discrete_sequence=["#1e9a87"],
            title="Até 20 autores com mais participações na amostra",
        )

        fig_autores.update_layout(
            plot_bgcolor="white",
            paper_bgcolor="white",
            font=dict(color="#182b49"),
            margin=dict(l=20, r=20, t=60, b=20),
            xaxis_title="Participações em proposições",
            yaxis_title="",
        )

        st.plotly_chart(
            fig_autores,
            use_container_width=True,
        )
    else:
        st.info("Não foi possível montar o ranking de autores.")

    st.caption(
        f"O ranking considera no máximo {LIMITE_AUTORES} proposições "
        "correspondentes. Autores podem incluir pessoas e entidades; "
        "participação não significa necessariamente autoria individual."
    )

    # =====================================================
    # TABELA E EXPORTAÇÃO
    # =====================================================

    st.markdown("## 📄 Proposições encontradas")

    preferidas = [
        "id",
        "siglaTipo",
        "numero",
        "ano",
        "dataApresentacao",
        "ementa",
        "uri",
    ]

    colunas = [
        coluna for coluna in preferidas
        if coluna in filtrado.columns
    ]

    tabela = filtrado[colunas].copy()

    if "dataApresentacao" in tabela.columns:
        tabela["dataApresentacao"] = (
            tabela["dataApresentacao"].dt.strftime("%d/%m/%Y")
        )

    st.dataframe(
        tabela,
        use_container_width=True,
        hide_index=True,
        column_config={
            "id": st.column_config.NumberColumn("ID"),
            "siglaTipo": st.column_config.TextColumn("Tipo"),
            "numero": st.column_config.NumberColumn("Número"),
            "ano": st.column_config.NumberColumn("Ano"),
            "dataApresentacao": st.column_config.TextColumn(
                "Data de apresentação"
            ),
            "ementa": st.column_config.TextColumn(
                "Ementa", width="large"
            ),
            "uri": st.column_config.LinkColumn("Link oficial"),
        },
    )

    csv = filtrado.to_csv(index=False).encode("utf-8-sig")

    st.download_button(
        "⬇️ Baixar resultados em CSV",
        data=csv,
        file_name=f"proposicoes_{ano_atual}.csv",
        mime="text/csv",
        use_container_width=True,
    )

    st.caption(
        "Fonte: Dados Abertos da Câmara dos Deputados. "
        "Os resultados correspondem às páginas consultadas em cada mês."
    )

else:
    st.info(
        "Configure os filtros na barra lateral e clique em "
        "“Buscar proposições” para iniciar."
    )