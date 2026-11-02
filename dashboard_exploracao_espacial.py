
import os
from datetime import date, timedelta

import requests
import pandas as pd
import streamlit as st
import plotly.express as px


# ============================================================
# 1. CONFIGURAÇÕES
# ============================================================

st.set_page_config(
    page_title="Cosmos | Exploração Espacial",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
)

NASA_BASE = "https://api.nasa.gov"
APOD_URL = "https://science.nasa.gov/wp-json/wp/v2/apod-basic/"
EONET_URL = "https://eonet.gsfc.nasa.gov/api/v3/events"
EXOPLANET_URL = "https://exoplanetarchive.ipac.caltech.edu/TAP/sync"

CORES = {
    "fundo": "#080D1A",
    "card": "#111B2E",
    "azul": "#4F8CFF",
    "ciano": "#36D6E7",
    "texto": "#F1F5FC",
    "secundario": "#93A4BD",
}

# ============================================================
# 2. ESTILIZAÇÃO
# ============================================================

st.markdown("""
<style>

@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background: linear-gradient(135deg, #080D1A 0%, #0D1729 55%, #101B30 100%);
    color: #F1F5FC;
}

[data-testid="stSidebar"] {
    background: #0B1323;
    border-right: 1px solid #1E304C;
}

[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 {
    color: #F1F5FC;
}

.main-title {
    font-size: 36px;
    font-weight: 800;
    color: #F1F5FC;
    letter-spacing: -1.5px;
    margin-bottom: 4px;
}

.subtitle {
    color: #93A4BD;
    font-size: 14px;
    margin-bottom: 28px;
}

.section-title {
    font-size: 23px;
    font-weight: 700;
    color: #F1F5FC;
    margin-top: 12px;
    margin-bottom: 16px;
}

.info-card {
    background: linear-gradient(145deg, #15243B, #101A2C);
    border: 1px solid #243A5B;
    border-radius: 14px;
    padding: 20px;
    margin-bottom: 12px;
}

.card-label {
    color: #93A4BD;
    font-size: 12px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 1px;
}

.card-value {
    color: #F1F5FC;
    font-size: 27px;
    font-weight: 800;
    margin-top: 7px;
}

.card-description {
    color: #36D6E7;
    font-size: 12px;
    margin-top: 5px;
}

div[data-testid="stMetric"] {
    background: linear-gradient(145deg, #15243B, #101A2C);
    border: 1px solid #243A5B;
    padding: 17px;
    border-radius: 13px;
}

div[data-testid="stMetricLabel"] {
    color: #93A4BD;
}

div[data-testid="stMetricValue"] {
    color: #F1F5FC;
}

.stButton > button {
    background: linear-gradient(90deg, #3679F6, #36B9D6);
    color: white;
    border: none;
    border-radius: 9px;
    font-weight: 700;
    padding: 10px 22px;
    transition: 0.2s;
}

.stButton > button:hover {
    background: linear-gradient(90deg, #2865DC, #229DBB);
    border: none;
    transform: translateY(-1px);
}

.stDownloadButton > button {
    background: #15243B;
    border: 1px solid #36D6E7;
    color: #36D6E7;
    border-radius: 9px;
}

.stDownloadButton > button:hover {
    background: #203652;
    color: white;
}

div[data-testid="stDataFrame"] {
    border: 1px solid #243A5B;
    border-radius: 10px;
    overflow: hidden;
}

hr {
    border-color: #243A5B;
}

.footer {
    text-align: center;
    color: #647895;
    font-size: 12px;
    padding: 25px 0 10px 0;
}

</style>
""", unsafe_allow_html=True)


# ============================================================
# 3. FUNÇÕES AUXILIARES
# ============================================================

@st.cache_data(ttl=900, show_spinner=False)
def consultar_json(url, params=None):
    """Consulta uma API e armazena o resultado em cache."""

    response = requests.get(
        url,
        params=params,
        timeout=40,
    )

    response.raise_for_status()

    return response.json()


def configurar_grafico(fig):
    """Padroniza a aparência dos gráficos."""

    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(
            family="Inter",
            color="#F1F5FC",
        ),
        margin=dict(l=20, r=20, t=55, b=20),
        title_font_size=17,
        legend_title_font_size=12,
    )

    return fig


def exportar_csv(df, nome):
    """Gera arquivo CSV compatível com Excel."""

    return st.download_button(
        label="⬇ Baixar dados em CSV",
        data=df.to_csv(index=False).encode("utf-8-sig"),
        file_name=nome,
        mime="text/csv",
    )


def encontrar_coordenada(coordenadas):
    """
    Localiza um par longitude/latitude em estruturas
    de coordenadas GeoJSON aninhadas.
    """

    if not isinstance(coordenadas, (list, tuple)):
        return None

    if (
        len(coordenadas) >= 2
        and isinstance(coordenadas[0], (int, float))
        and isinstance(coordenadas[1], (int, float))
    ):
        lon, lat = coordenadas[0], coordenadas[1]

        if -180 <= lon <= 180 and -90 <= lat <= 90:
            return lon, lat

        return None

    for item in coordenadas:
        resultado = encontrar_coordenada(item)

        if resultado:
            return resultado

    return None


def mostrar_erro(nome, erro):
    """Exibe erros de maneira amigável."""

    st.error(f"Não foi possível consultar {nome}.")

    with st.expander("Detalhes do erro"):
        st.code(str(erro))


def mostrar_cabecalho(titulo, descricao):
    st.markdown(
        f'<div class="section-title">{titulo}</div>',
        unsafe_allow_html=True,
    )
    st.caption(descricao)


# ============================================================
# 4. MENU LATERAL
# ============================================================

with st.sidebar:

    st.markdown(
        """
        <div style="text-align:center; padding:15px 0 25px 0;">
            <div style="font-size:48px;">🚀</div>
            <div style="font-size:23px; font-weight:800; color:#F1F5FC;">
                COSMOS
            </div>
            <div style="font-size:11px; color:#93A4BD; letter-spacing:2px;">
                SPACE EXPLORATION
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.divider()

    st.markdown("### Navegação")

    aba = st.radio(
        "Selecione uma exploração:",
        [
            "Visão geral",
            "Asteroides",
            "Imagem APOD",
            "Exoplanetas",
            "Eventos naturais",
        ],
        label_visibility="collapsed",
    )

    st.divider()

    st.markdown("### Configurações")

    api_key = st.text_input(
        "Chave NASA API",
        value=os.getenv("NASA_API_KEY", "DEMO_KEY"),
        type="password",
        help="Você pode obter uma chave gratuita em api.nasa.gov.",
    )

    st.caption("Fonte: NASA Open APIs")

    st.divider()

    st.markdown(
        """
        <div style="font-size:11px; color:#647895; text-align:center;">
            COSMOS DASHBOARD<br>
            Dados científicos e exploração espacial<br>
            © 2026
        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# 5. CABEÇALHO PRINCIPAL
# ============================================================

st.markdown(
    '<div class="main-title">Exploração Espacial</div>',
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="subtitle">
        Explore o universo através de dados científicos,
        imagens astronômicas e informações disponibilizadas pela NASA.
    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# 6. VISÃO GERAL
# ============================================================

if aba == "Visão geral":

    st.markdown("## Bem-vindo ao Cosmos")

    st.write(
        "Uma plataforma de exploração científica para descobrir "
        "mais sobre o espaço, os planetas e os fenômenos naturais."
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        <div class="info-card">
            <div style="font-size:30px;">☄️</div>
            <div class="card-label">Asteroides</div>
            <div class="card-value">NeoWs</div>
            <div class="card-description">Objetos próximos da Terra</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="info-card">
            <div style="font-size:30px;">🌌</div>
            <div class="card-label">Astronomia</div>
            <div class="card-value">APOD</div>
            <div class="card-description">Imagem astronômica do dia</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class="info-card">
            <div style="font-size:30px;">🪐</div>
            <div class="card-label">Exoplanetas</div>
            <div class="card-value">NASA Archive</div>
            <div class="card-description">Planetas fora do Sistema Solar</div>
        </div>
        """, unsafe_allow_html=True)

    st.divider()

    st.markdown("### Explore as funcionalidades")

    st.write("""
    - **Asteroides:** acompanhe objetos próximos da Terra e suas características.
    - **Imagem APOD:** descubra imagens astronômicas publicadas pela NASA.
    - **Exoplanetas:** consulte planetas identificados fora do Sistema Solar.
    - **Eventos naturais:** visualize fenômenos naturais registrados mundialmente.
    """)

    st.info(
        "Selecione uma das opções no menu lateral para iniciar sua exploração."
    )


# ============================================================
# 7. ASTEROIDES
# ============================================================

elif aba == "Asteroides":

    mostrar_cabecalho(
        "☄️ Asteroides próximos da Terra",
        "Consulte objetos próximos ao nosso planeta e suas características.",
    )

    hoje = date.today()

    col1, col2 = st.columns(2)

    with col1:
        inicio = st.date_input(
            "Data inicial",
            value=hoje - timedelta(days=6),
            max_value=hoje,
        )

    with col2:
        fim = st.date_input(
            "Data final",
            value=hoje,
            min_value=inicio,
            max_value=hoje,
        )

    if st.button("Consultar asteroides", type="primary"):

        if inicio > fim:
            st.error("A data inicial não pode ser posterior à data final.")

        elif (fim - inicio).days > 6:
            st.error("O intervalo máximo permitido é de 7 dias.")

        else:

            try:

                with st.spinner("Consultando dados da NASA..."):

                    dados = consultar_json(
                        f"{NASA_BASE}/neo/rest/v1/feed",
                        {
                            "start_date": inicio.isoformat(),
                            "end_date": fim.isoformat(),
                            "api_key": api_key,
                        },
                    )

                registros = []

                for data, objetos in dados.get(
                    "near_earth_objects", {}
                ).items():

                    for obj in objetos:

                        aproximacoes = obj.get(
                            "close_approach_data", []
                        )

                        aprox = next(
                            (
                                item for item in aproximacoes
                                if item.get("miss_distance")
                            ),
                            {},
                        )

                        registros.append({
                            "Nome": obj.get("name"),
                            "Data": data,
                            "Diâmetro máximo (m)": (
                                obj.get("estimated_diameter", {})
                                .get("meters", {})
                                .get("estimated_diameter_max")
                            ),
                            "Potencialmente perigoso": (
                                obj.get("is_potentially_hazardous_asteroid")
                            ),
                            "Distância (km)": (
                                aprox.get("miss_distance", {})
                                .get("kilometers")
                            ),
                            "Velocidade (km/s)": (
                                aprox.get("relative_velocity", {})
                                .get("kilometers_per_second")
                            ),
                        })

                df = pd.DataFrame(registros)

                if df.empty:
                    st.info("Nenhum asteroide encontrado no período.")
                    st.stop()

                for coluna in [
                    "Diâmetro máximo (m)",
                    "Distância (km)",
                    "Velocidade (km/s)",
                ]:
                    df[coluna] = pd.to_numeric(
                        df[coluna],
                        errors="coerce",
                    )

                perigosos = df["Potencialmente perigoso"].eq(True).sum()

                st.divider()

                c1, c2, c3 = st.columns(3)

                c1.metric("Total de asteroides", len(df))
                c2.metric("Potencialmente perigosos", int(perigosos))
                c3.metric(
                    "Diâmetro médio",
                    f"{df['Diâmetro máximo (m)'].mean():.1f} m"
                    if df["Diâmetro máximo (m)"].notna().any()
                    else "N/D",
                )

                st.divider()

                st.markdown("### Distância x velocidade")

                grafico_df = df.dropna(
                    subset=["Distância (km)", "Velocidade (km/s)"]
                )

                if not grafico_df.empty:

                    fig = px.scatter(
                        grafico_df,
                        x="Distância (km)",
                        y="Velocidade (km/s)",
                        size="Diâmetro máximo (m)",
                        color="Potencialmente perigoso",
                        hover_name="Nome",
                        hover_data=["Data"],
                        log_x=True,
                        color_discrete_map={
                            True: "#FF657A",
                            False: "#36D6E7",
                        },
                        title="Aproximação dos asteroides em relação à Terra",
                    )

                    fig = configurar_grafico(fig)

                    st.plotly_chart(
                        fig,
                        use_container_width=True,
                    )

                else:
                    st.info("Não há dados suficientes para gerar o gráfico.")

                st.markdown("### Dados encontrados")

                st.dataframe(
                    df,
                    use_container_width=True,
                    hide_index=True,
                )

                exportar_csv(df, "asteroides.csv")

            except (requests.RequestException, ValueError) as erro:
                mostrar_erro("NeoWs", erro)


# ============================================================
# 8. IMAGEM ASTRONÔMICA DO DIA - APOD
# ============================================================

elif aba == "Imagem APOD":

    mostrar_cabecalho(
        "🌌 Astronomy Picture of the Day",
        "Uma imagem do universo selecionada diariamente pela NASA.",
    )

    data_apod = st.date_input(
        "Escolha uma data",
        value=date.today(),
        min_value=date(1995, 6, 16),
        max_value=date.today(),
    )

    if st.button("Descobrir imagem", type="primary"):

        try:

            with st.spinner("Carregando imagem astronômica..."):

                dados = consultar_json(
                    APOD_URL,
                    {
                        "date": data_apod.isoformat(),
                        "api_key": api_key,
                    },
                )

            st.divider()

            st.markdown(f"## {dados.get('title', 'Imagem astronômica')}")

            st.caption(f"Publicação: {dados.get('date', '')}")

            tipo = dados.get("media_type", "")

            # A API atual utiliza hdurl para a imagem.
            if tipo == "image":

                imagem = dados.get("hdurl")

                if imagem:
                    st.image(
                        imagem,
                        caption=dados.get("alt") or dados.get("title"),
                        use_container_width=True,
                    )
                else:
                    st.warning("A imagem não está disponível para esta data.")

            elif tipo in ("video", "iframe"):

                st.info(
                    "Esta publicação contém conteúdo audiovisual. "
                    "Acesse a página original da NASA para visualizá-lo."
                )

                if dados.get("url"):
                    st.link_button(
                        "Assistir conteúdo na NASA",
                        dados["url"],
                    )

                if dados.get("hdurl"):
                    st.image(
                        dados["hdurl"],
                        caption="Imagem de pré-visualização",
                        use_container_width=True,
                    )

            st.divider()

            st.markdown("### Sobre esta publicação")

            st.write(dados.get("explanation", "Descrição indisponível."))

            credito = dados.get("credit") or dados.get("copyright")

            if credito:
                st.caption(f"Créditos: {credito}")

            if dados.get("permalink"):
                st.link_button(
                    "Ver publicação original",
                    dados["permalink"],
                )

        except (requests.RequestException, ValueError) as erro:
            mostrar_erro("APOD", erro)


# ============================================================
# 9. EXOPLANETAS
# ============================================================

elif aba == "Exoplanetas":

    mostrar_cabecalho(
        "🪐 Exoplanetas confirmados",
        "Explore planetas localizados fora do nosso Sistema Solar.",
    )

    limite = st.slider(
        "Quantidade máxima de registros",
        min_value=100,
        max_value=2000,
        value=500,
        step=100,
    )

    if st.button("Consultar exoplanetas", type="primary"):

        try:

            with st.spinner("Consultando NASA Exoplanet Archive..."):

                query = (
                    f"select top {limite} pl_name, discoverymethod "
                    "from ps "
                    "where default_flag = 1 "
                    "order by pl_name"
                )

                resposta = requests.get(
                    EXOPLANET_URL,
                    params={
                        "query": query,
                        "format": "json",
                    },
                    timeout=60,
                )

                resposta.raise_for_status()

                dados = resposta.json()

            df = pd.DataFrame(dados)

            if df.empty:
                st.warning("Nenhum exoplaneta encontrado.")
                st.stop()

            df = df.rename(columns={
                "pl_name": "Nome do exoplaneta",
                "discoverymethod": "Método de descoberta",
            })

            df["Método de descoberta"] = (
                df["Método de descoberta"]
                .fillna("Não informado")
            )

            st.divider()

            c1, c2 = st.columns(2)

            c1.metric("Exoplanetas encontrados", len(df))

            c2.metric(
                "Métodos de descoberta",
                df["Método de descoberta"].nunique(),
            )

            st.divider()

            st.markdown("### Métodos de descoberta")

            metodos = (
                df["Método de descoberta"]
                .value_counts()
                .rename_axis("Método")
                .reset_index(name="Quantidade")
            )

            fig = px.bar(
                metodos,
                x="Quantidade",
                y="Método",
                orientation="h",
                text="Quantidade",
                color="Quantidade",
                color_continuous_scale=[
                    "#1D3B65",
                    "#3679F6",
                    "#36D6E7",
                ],
                title="Distribuição por método de descoberta",
            )

            fig.update_layout(
                coloraxis_showscale=False,
                yaxis={"categoryorder": "total ascending"},
            )

            fig.update_traces(
                textposition="outside",
                cliponaxis=False,
            )

            fig = configurar_grafico(fig)

            st.plotly_chart(
                fig,
                use_container_width=True,
            )

            st.markdown("### Catálogo de exoplanetas")

            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True,
            )

            exportar_csv(df, "exoplanetas.csv")

        except (requests.RequestException, ValueError) as erro:
            mostrar_erro("Exoplanet Archive", erro)


# ============================================================
# 10. EVENTOS NATURAIS - EONET
# ============================================================

elif aba == "Eventos naturais":

    mostrar_cabecalho(
        "🌍 Eventos naturais",
        "Visualize fenômenos naturais registrados ao redor do mundo.",
    )

    dias = st.slider(
        "Período de consulta (dias)",
        min_value=1,
        max_value=30,
        value=7,
    )

    if st.button("Consultar eventos", type="primary"):

        try:

            with st.spinner("Mapeando eventos naturais..."):

                dados = consultar_json(
                    EONET_URL,
                    {
                        "status": "all",
                        "days": dias,
                        "limit": 500,
                    },
                )

            eventos = []

            for evento in dados.get("events", []):

                geometrias = evento.get("geometry", [])

                if not geometrias:
                    continue

                # Seleciona a geometria mais recente com coordenadas válidas.
                geo = None
                coordenada = None

                for geometria in reversed(geometrias):

                    resultado = encontrar_coordenada(
                        geometria.get("coordinates")
                    )

                    if resultado:
                        geo = geometria
                        coordenada = resultado
                        break

                if coordenada is None:
                    continue

                lon, lat = coordenada

                categorias = ", ".join(
                    categoria.get("title", "Não informado")
                    for categoria in evento.get("categories", [])
                )

                fontes = evento.get("sources", [])

                eventos.append({
                    "Evento": evento.get("title"),
                    "Categoria": categorias or "Não informada",
                    "Data": geo.get("date"),
                    "Latitude": lat,
                    "Longitude": lon,
                    "Status": (
                        "Encerrado"
                        if evento.get("closed")
                        else "Em andamento"
                    ),
                    "Fonte": fontes[0].get("url") if fontes else None,
                })

            df = pd.DataFrame(eventos)

            if df.empty:
                st.info(
                    "Nenhum evento com coordenadas disponíveis "
                    "foi encontrado no período."
                )
                st.stop()

            st.divider()

            c1, c2, c3 = st.columns(3)

            c1.metric("Eventos localizados", len(df))

            c2.metric(
                "Categorias identificadas",
                df["Categoria"].nunique(),
            )

            c3.metric(
                "Eventos em andamento",
                int((df["Status"] == "Em andamento").sum()),
            )

            st.divider()

            st.markdown("### Mapa global de eventos")

            fig = px.scatter_map(
                df,
                lat="Latitude",
                lon="Longitude",
                color="Categoria",
                hover_name="Evento",
                hover_data=[
                    "Data",
                    "Status",
                ],
                zoom=1,
                height=600,
                map_style="carto-darkmatter",
                title="Distribuição geográfica dos eventos naturais",
            )

            fig = configurar_grafico(fig)

            st.plotly_chart(
                fig,
                use_container_width=True,
            )

            st.markdown("### Eventos registrados")

            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Fonte": st.column_config.LinkColumn(
                        "Fonte de informação"
                    ),
                },
            )

            exportar_csv(df, "eventos_naturais.csv")

        except (requests.RequestException, ValueError) as erro:
            mostrar_erro("EONET", erro)


# ============================================================
# 11. RODAPÉ
# ============================================================

st.divider()

st.markdown(
    """
    <div class="footer">
        COSMOS | EXPLORAÇÃO ESPACIAL<br>
        Desenvolvido com Python, Streamlit, Plotly e APIs da NASA.<br>
        Os dados apresentados são disponibilizados pelas fontes científicas
        consultadas.
    </div>
    """,
    unsafe_allow_html=True,
)
