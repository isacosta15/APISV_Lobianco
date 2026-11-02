
import os
from datetime import datetime, timezone

import requests
import pandas as pd
import streamlit as st
import plotly.express as px


# ============================================================
# 1. CONFIGURAÇÕES
# ============================================================

st.set_page_config(
    page_title="Flight Radar | Monitoramento Aéreo",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded",
)

BASE = "https://opensky-network.org/api"

AUTH_URL = (
    "https://auth.opensky-network.org/auth/realms/opensky-network/"
    "protocol/openid-connect/token"
)

CORES = {
    "background": "#080D1A",
    "sidebar": "#0B1323",
    "card": "#111B2E",
    "blue": "#4F8CFF",
    "cyan": "#36D6E7",
    "text": "#F1F5FC",
    "secondary": "#93A4BD",
    "green": "#36D6A0",
    "red": "#FF657A",
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
    background: linear-gradient(
        135deg,
        #080D1A 0%,
        #0D1729 55%,
        #101B30 100%
    );
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
    min-height: 145px;
}

.card-icon {
    font-size: 30px;
    margin-bottom: 10px;
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
    font-size: 24px;
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
# 3. AUTENTICAÇÃO OPCIONAL
# ============================================================

@st.cache_data(ttl=1500, show_spinner=False)
def obter_token(client_id, client_secret):
    """
    Obtém token OAuth2 da OpenSky.
    O token possui validade aproximada de 30 minutos.
    """

    resposta = requests.post(
        AUTH_URL,
        data={
            "grant_type": "client_credentials",
            "client_id": client_id,
            "client_secret": client_secret,
        },
        headers={
            "Content-Type": "application/x-www-form-urlencoded"
        },
        timeout=30,
    )

    resposta.raise_for_status()

    return resposta.json()["access_token"]


def obter_headers(client_id="", client_secret=""):
    """
    Retorna os cabeçalhos de autenticação.
    Sem credenciais, utiliza acesso anônimo.
    """

    if client_id and client_secret:
        token = obter_token(client_id, client_secret)

        return {
            "Authorization": f"Bearer {token}"
        }

    return {}


# ============================================================
# 4. FUNÇÕES DE CONSULTA
# ============================================================

@st.cache_data(ttl=20, show_spinner=False)
def consultar_aeronaves(params, headers):
    """Consulta as posições atuais das aeronaves."""

    resposta = requests.get(
        f"{BASE}/states/all",
        params=params,
        headers=headers,
        timeout=40,
    )

    resposta.raise_for_status()

    return resposta.json()


@st.cache_data(ttl=300, show_spinner=False)
def consultar_trajetoria(icao24, headers):
    """Consulta a trajetória disponível de uma aeronave."""

    resposta = requests.get(
        f"{BASE}/tracks",
        params={
            "icao24": icao24,
            "time": 0,
        },
        headers=headers,
        timeout=40,
    )

    resposta.raise_for_status()

    return resposta.json()


# ============================================================
# 5. FUNÇÕES AUXILIARES
# ============================================================

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
        margin=dict(
            l=20,
            r=20,
            t=55,
            b=20,
        ),
        title_font_size=17,
        legend_title_font_size=12,
    )

    return fig


def mostrar_cabecalho(titulo, descricao):

    st.markdown(
        f'<div class="section-title">{titulo}</div>',
        unsafe_allow_html=True,
    )

    st.caption(descricao)


def mostrar_erro(nome, erro):
    """Apresenta erros de maneira organizada."""

    st.error(f"Não foi possível consultar {nome}.")

    if isinstance(erro, requests.HTTPError):
        status = (
            erro.response.status_code
            if erro.response is not None
            else None
        )

        if status == 401:
            st.warning(
                "Falha na autenticação. Verifique suas credenciais OAuth2."
            )

        elif status == 403:
            st.warning(
                "Acesso não autorizado ou operação não permitida."
            )

        elif status == 429:
            st.warning(
                "Limite de consultas atingido. Aguarde antes de tentar novamente."
            )

        elif status == 404:
            st.warning(
                "Não foram encontrados dados para essa consulta."
            )

    with st.expander("Detalhes técnicos"):
        st.code(str(erro))


def exportar_csv(df, nome):

    st.download_button(
        label="⬇ Baixar dados em CSV",
        data=df.to_csv(index=False).encode("utf-8-sig"),
        file_name=nome,
        mime="text/csv",
    )


def converter_altitude(valor):
    if pd.isna(valor):
        return "N/D"

    return f"{valor:,.0f} m"


def converter_velocidade(valor):
    if pd.isna(valor):
        return "N/D"

    return f"{valor * 3.6:,.1f} km/h"


def converter_horario(valor):
    if pd.isna(valor):
        return "N/D"

    return datetime.fromtimestamp(
        int(valor),
        tz=timezone.utc,
    ).strftime("%d/%m/%Y %H:%M:%S UTC")


def criar_dataframe_aeronaves(resposta):
    """Transforma os vetores de estado em DataFrame."""

    campos = [
        "icao24",
        "callsign",
        "origin_country",
        "time_position",
        "last_contact",
        "longitude",
        "latitude",
        "baro_altitude",
        "on_ground",
        "velocity",
        "true_track",
        "vertical_rate",
        "sensors",
        "geo_altitude",
        "squawk",
        "spi",
        "position_source",
        "category",
    ]

    df = pd.DataFrame(
        resposta.get("states") or [],
        columns=campos,
    )

    if df.empty:
        return df

    df = df.dropna(
        subset=["latitude", "longitude"]
    ).copy()

    # Conversão dos campos numéricos.
    numericos = [
        "latitude",
        "longitude",
        "baro_altitude",
        "geo_altitude",
        "velocity",
        "true_track",
        "vertical_rate",
        "category",
        "time_position",
        "last_contact",
    ]

    for coluna in numericos:
        df[coluna] = pd.to_numeric(
            df[coluna],
            errors="coerce",
        )

    # Limpeza dos indicativos.
    df["callsign"] = (
        df["callsign"]
        .fillna("")
        .str.strip()
    )

    return df


def formatar_aeronaves(df):
    """Aplica nomes amigáveis às colunas."""

    return df.rename(columns={
        "icao24": "ICAO24",
        "callsign": "Indicativo",
        "origin_country": "País de origem",
        "time_position": "Horário da posição (Unix)",
        "last_contact": "Último contato (Unix)",
        "longitude": "Longitude",
        "latitude": "Latitude",
        "baro_altitude": "Altitude barométrica (m)",
        "on_ground": "Em solo",
        "velocity": "Velocidade (m/s)",
        "true_track": "Direção (graus)",
        "vertical_rate": "Taxa vertical (m/s)",
        "sensors": "Sensores",
        "geo_altitude": "Altitude geométrica (m)",
        "squawk": "Squawk",
        "spi": "Indicador SPI",
        "position_source": "Fonte da posição",
        "category": "Categoria",
    })


def nome_categoria(codigo):

    categorias = {
        0: "Sem informação",
        1: "Sem categoria ADS-B",
        2: "Leve",
        3: "Pequena",
        4: "Grande",
        5: "Grande - alto vórtice",
        6: "Pesada",
        7: "Alto desempenho",
        8: "Helicóptero",
        9: "Planador",
        10: "Mais leve que o ar",
        11: "Paraquedista",
        12: "Ultraleve",
        13: "Reservada",
        14: "Drone",
        15: "Veículo espacial",
        16: "Veículo de emergência",
        17: "Veículo de serviço",
        18: "Obstáculo pontual",
        19: "Obstáculo em agrupamento",
        20: "Obstáculo linear",
    }

    if pd.isna(codigo):
        return "Não informada"

    return categorias.get(int(codigo), "Desconhecida")


# ============================================================
# 6. MENU LATERAL
# ============================================================

with st.sidebar:

    st.markdown(
        """
        <div style="text-align:center; padding:15px 0 25px 0;">
            <div style="font-size:48px;">✈️</div>
            <div style="font-size:23px; font-weight:800; color:#F1F5FC;">
                FLIGHT RADAR
            </div>
            <div style="font-size:11px; color:#93A4BD; letter-spacing:2px;">
                AIR TRAFFIC ANALYTICS
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.divider()

    st.markdown("### Navegação")

    modo = st.radio(
        "Selecione uma consulta:",
        [
            "Visão geral",
            "Aeronaves no Brasil",
            "Trajetória por ICAO24",
        ],
        label_visibility="collapsed",
    )

    st.divider()

    st.markdown("### Autenticação")

    with st.expander("Credenciais OpenSky", expanded=False):

        client_id = st.text_input(
            "Client ID",
            value=os.getenv("OPENSKY_CLIENT_ID", ""),
        )

        client_secret = st.text_input(
            "Client Secret",
            value=os.getenv("OPENSKY_CLIENT_SECRET", ""),
            type="password",
        )

        st.caption(
            "Opcional. Sem credenciais, a consulta será anônima."
        )

    st.divider()

    st.markdown(
        """
        <div style="font-size:11px; color:#647895; text-align:center;">
            Fonte: OpenSky Network<br>
            Monitoramento de tráfego aéreo<br>
            © 2026
        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# 7. CABEÇALHO PRINCIPAL
# ============================================================

st.markdown(
    '<div class="main-title">Monitoramento Aéreo</div>',
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="subtitle">
        Acompanhe aeronaves, posições geográficas e trajetórias
        utilizando dados disponibilizados pela OpenSky Network.
    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# 8. VISÃO GERAL
# ============================================================

if modo == "Visão geral":

    st.markdown("## Bem-vindo ao Flight Radar")

    st.write(
        "Uma plataforma de visualização e análise de tráfego aéreo "
        "com dados de rastreamento disponibilizados pela OpenSky Network."
    )

    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown("""
        <div class="info-card">
            <div class="card-icon">🌎</div>
            <div class="card-label">Monitoramento</div>
            <div class="card-value">Brasil</div>
            <div class="card-description">Aeronaves em uma região geográfica</div>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown("""
        <div class="info-card">
            <div class="card-icon">✈️</div>
            <div class="card-label">Rastreamento</div>
            <div class="card-value">ICAO24</div>
            <div class="card-description">Identificação individual de aeronaves</div>
        </div>
        """, unsafe_allow_html=True)

    with c3:
        st.markdown("""
        <div class="info-card">
            <div class="card-icon">📍</div>
            <div class="card-label">Visualização</div>
            <div class="card-value">Mapa</div>
            <div class="card-description">Posições e trajetórias disponíveis</div>
        </div>
        """, unsafe_allow_html=True)

    st.divider()

    st.markdown("### Funcionalidades disponíveis")

    st.write("""
    **Aeronaves no Brasil**
    
    Consulte aeronaves dentro de uma área geográfica, filtre por país
    de origem e categoria, e visualize suas posições no mapa.

    **Trajetória por ICAO24**

    Consulte os pontos de trajetória disponibilizados pela API,
    visualize o percurso e confira informações de altitude e direção.
    """)

    st.info(
        "Selecione uma funcionalidade no menu lateral para começar."
    )

    st.markdown("### Sobre os dados")

    st.write(
        "As informações são provenientes de mensagens ADS-B e "
        "outras fontes de vigilância aérea integradas à OpenSky. "
        "A cobertura e a disponibilidade variam conforme a região "
        "e os receptores disponíveis."
    )


# ============================================================
# 9. AERONAVES NO BRASIL
# ============================================================

elif modo == "Aeronaves no Brasil":

    mostrar_cabecalho(
        "🌎 Aeronaves no Brasil",
        "Consulte posições de aeronaves dentro de uma região geográfica.",
    )

    st.markdown("### Limites geográficos")

    st.caption(
        "Os valores iniciais representam uma caixa aproximada "
        "que cobre o território brasileiro."
    )

    col1, col2 = st.columns(2)

    with col1:

        lat_min = st.number_input(
            "Latitude mínima",
            min_value=-90.0,
            max_value=90.0,
            value=-33.75,
            step=0.1,
        )

        lon_min = st.number_input(
            "Longitude mínima",
            min_value=-180.0,
            max_value=180.0,
            value=-73.99,
            step=0.1,
        )

    with col2:

        lat_max = st.number_input(
            "Latitude máxima",
            min_value=-90.0,
            max_value=90.0,
            value=5.27,
            step=0.1,
        )

        lon_max = st.number_input(
            "Longitude máxima",
            min_value=-180.0,
            max_value=180.0,
            value=-34.79,
            step=0.1,
        )

    st.divider()

    st.markdown("### Filtros")

    col1, col2 = st.columns(2)

    with col1:

        pais = st.text_input(
            "País de origem",
            placeholder="Ex.: Brazil",
            help="Digite parte do nome do país. O filtro não diferencia maiúsculas e minúsculas.",
        )

    with col2:

        categoria = st.selectbox(
            "Categoria da aeronave",
            [
                "Todas",
                "Aviões",
                "Helicópteros",
                "Outras categorias",
            ],
        )

    if st.button("Consultar aeronaves", type="primary"):

        if lat_min >= lat_max:
            st.error("A latitude mínima deve ser menor que a máxima.")

        elif lon_min >= lon_max:
            st.error("A longitude mínima deve ser menor que a máxima.")

        else:

            try:

                headers = obter_headers(
                    client_id,
                    client_secret,
                )

                params = {
                    "lamin": lat_min,
                    "lamax": lat_max,
                    "lomin": lon_min,
                    "lomax": lon_max,
                    "extended": 1,
                }

                with st.spinner("Consultando posições na OpenSky..."):

                    resposta = consultar_aeronaves(
                        params,
                        headers,
                    )

                df = criar_dataframe_aeronaves(resposta)

                if df.empty:
                    st.warning(
                        "Nenhuma aeronave com posição disponível foi retornada."
                    )
                    st.stop()

                total_inicial = len(df)

                # Filtro de país.
                if pais.strip():

                    df = df[
                        df["origin_country"].str.contains(
                            pais.strip(),
                            case=False,
                            na=False,
                            regex=False,
                        )
                    ]

                # Filtro de categoria.
                if categoria == "Aviões":

                    df = df[
                        df["category"].between(2, 7)
                    ]

                elif categoria == "Helicópteros":

                    df = df[
                        df["category"] == 8
                    ]

                elif categoria == "Outras categorias":

                    df = df[
                        ~df["category"].between(2, 8)
                        | df["category"].isna()
                    ]

                if df.empty:
                    st.info(
                        "Nenhuma aeronave corresponde aos filtros selecionados."
                    )
                    st.stop()

                st.divider()

                # Indicadores.
                total = len(df)

                em_solo = int(
                    df["on_ground"].eq(True).sum()
                )

                em_voo = int(
                    df["on_ground"].eq(False).sum()
                )

                velocidade_media = df["velocity"].mean()

                altitude_media = df["baro_altitude"].mean()

                c1, c2, c3, c4 = st.columns(4)

                c1.metric(
                    "Aeronaves encontradas",
                    total,
                )

                c2.metric(
                    "Em voo",
                    em_voo,
                )

                c3.metric(
                    "Em solo",
                    em_solo,
                )

                c4.metric(
                    "Velocidade média",
                    converter_velocidade(velocidade_media),
                )

                st.divider()

                st.markdown("### Distribuição geográfica")

                mapa_df = df.copy()

                mapa_df["Categoria"] = mapa_df[
                    "category"
                ].apply(nome_categoria)

                mapa_df["Situação"] = mapa_df[
                    "on_ground"
                ].map({
                    True: "Em solo",
                    False: "Em voo",
                }).fillna("Não informada")

                mapa_df["Identificação"] = mapa_df[
                    "callsign"
                ].replace("", "Sem indicativo")

                fig = px.scatter_map(
                    mapa_df,
                    lat="latitude",
                    lon="longitude",
                    color="Situação",
                    hover_name="Identificação",
                    hover_data=[
                        "icao24",
                        "origin_country",
                        "baro_altitude",
                        "velocity",
                        "Categoria",
                    ],
                    color_discrete_map={
                        "Em voo": "#36D6E7",
                        "Em solo": "#FFB454",
                        "Não informada": "#93A4BD",
                    },
                    zoom=2.8,
                    height=600,
                    map_style="carto-darkmatter",
                    title="Posições das aeronaves",
                )

                fig = configurar_grafico(fig)

                st.plotly_chart(
                    fig,
                    use_container_width=True,
                )

                st.divider()

                st.markdown("### Análise das aeronaves")

                col1, col2 = st.columns(2)

                with col1:

                    paises = (
                        df["origin_country"]
                        .fillna("Não informado")
                        .value_counts()
                        .head(10)
                        .rename_axis("País")
                        .reset_index(name="Quantidade")
                    )

                    fig_paises = px.bar(
                        paises,
                        x="Quantidade",
                        y="País",
                        orientation="h",
                        text="Quantidade",
                        title="Principais países de origem",
                        color="Quantidade",
                        color_continuous_scale=[
                            "#1D3B65",
                            "#3679F6",
                            "#36D6E7",
                        ],
                    )

                    fig_paises.update_layout(
                        coloraxis_showscale=False,
                        yaxis={
                            "categoryorder": "total ascending"
                        },
                    )

                    fig_paises.update_traces(
                        textposition="outside",
                        cliponaxis=False,
                    )

                    st.plotly_chart(
                        configurar_grafico(fig_paises),
                        use_container_width=True,
                    )

                with col2:

                    situacao = pd.DataFrame({
                        "Situação": [
                            "Em voo",
                            "Em solo",
                            "Não informada",
                        ],
                        "Quantidade": [
                            em_voo,
                            em_solo,
                            int(
                                df["on_ground"].isna().sum()
                            ),
                        ],
                    })

                    fig_situacao = px.pie(
                        situacao,
                        names="Situação",
                        values="Quantidade",
                        hole=0.62,
                        title="Situação operacional",
                        color="Situação",
                        color_discrete_map={
                            "Em voo": "#36D6E7",
                            "Em solo": "#FFB454",
                            "Não informada": "#647895",
                        },
                    )

                    fig_situacao.update_traces(
                        textposition="inside",
                        textinfo="percent+label",
                    )

                    st.plotly_chart(
                        configurar_grafico(fig_situacao),
                        use_container_width=True,
                    )

                st.divider()

                st.markdown("### Dados das aeronaves")

                tabela = df.copy()

                tabela["Categoria"] = tabela[
                    "category"
                ].apply(nome_categoria)

                tabela["Velocidade (km/h)"] = (
                    tabela["velocity"] * 3.6
                )

                tabela["Horário da posição"] = (
                    tabela["time_position"].apply(
                        converter_horario
                    )
                )

                tabela = formatar_aeronaves(tabela)

                st.dataframe(
                    tabela,
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "Longitude": st.column_config.NumberColumn(
                            format="%.4f"
                        ),
                        "Latitude": st.column_config.NumberColumn(
                            format="%.4f"
                        ),
                        "Altitude barométrica (m)": st.column_config.NumberColumn(
                            format="%.0f"
                        ),
                        "Velocidade (m/s)": st.column_config.NumberColumn(
                            format="%.2f"
                        ),
                    },
                )

                exportar_csv(
                    tabela,
                    "aeronaves_brasil.csv",
                )

                st.caption(
                    f"Registros antes dos filtros: {total_inicial} | "
                    f"Registros exibidos: {total}"
                )

                st.caption(
                    f"Horário da consulta: "
                    f"{converter_horario(resposta.get('time'))}"
                )

            except (
                requests.RequestException,
                ValueError,
                KeyError,
            ) as erro:

                mostrar_erro(
                    "OpenSky Network",
                    erro,
                )


# ============================================================
# 10. TRAJETÓRIA POR ICAO24
# ============================================================

elif modo == "Trajetória por ICAO24":

    mostrar_cabecalho(
        "📍 Trajetória da aeronave",
        "Consulte os pontos de percurso disponíveis para um identificador ICAO24.",
    )

    st.markdown("### Identificação da aeronave")

    icao24 = st.text_input(
        "Código ICAO24",
        value="3c6444",
        max_chars=6,
        help="Identificador hexadecimal de 24 bits, com seis caracteres.",
    ).strip().lower()

    st.info(
        "Exemplo de identificação: 3c6444. "
        "A consulta utiliza a trajetória atual disponibilizada pela API."
    )

    if st.button("Consultar trajetória", type="primary"):

        if (
            len(icao24) != 6
            or any(
                caractere not in "0123456789abcdef"
                for caractere in icao24
            )
        ):

            st.error(
                "O ICAO24 deve conter exatamente 6 caracteres hexadecimais."
            )

        else:

            try:

                headers = obter_headers(
                    client_id,
                    client_secret,
                )

                with st.spinner("Buscando trajetória da aeronave..."):

                    track = consultar_trajetoria(
                        icao24,
                        headers,
                    )

                pontos = track.get("path") or []

                if not pontos:
                    st.warning(
                        "Não existem pontos de trajetória disponíveis "
                        "para essa aeronave neste momento."
                    )
                    st.stop()

                # Estrutura retornada:
                # [tempo, latitude, longitude, altitude,
                #  rumo verdadeiro, em solo]

                df = pd.DataFrame(
                    pontos,
                    columns=[
                        "tempo",
                        "latitude",
                        "longitude",
                        "altitude",
                        "rumo",
                        "no_chao",
                    ],
                )

                # Conversão de dados.
                df["tempo"] = pd.to_numeric(
                    df["tempo"],
                    errors="coerce",
                )

                for coluna in [
                    "latitude",
                    "longitude",
                    "altitude",
                    "rumo",
                ]:

                    df[coluna] = pd.to_numeric(
                        df[coluna],
                        errors="coerce",
                    )

                df = df.dropna(
                    subset=[
                        "latitude",
                        "longitude",
                        "tempo",
                    ]
                ).copy()

                if df.empty:
                    st.warning(
                        "A trajetória não possui coordenadas válidas."
                    )
                    st.stop()

                # Ordenação cronológica.
                df = df.sort_values(
                    "tempo"
                ).reset_index(drop=True)

                df["data_hora_utc"] = pd.to_datetime(
                    df["tempo"],
                    unit="s",
                    utc=True,
                )

                df["velocidade"] = None

                # Conversão dos valores de altitude.
                df["altitude_km"] = (
                    df["altitude"] / 1000
                )

                df["situação"] = df[
                    "no_chao"
                ].map({
                    True: "Em solo",
                    False: "Em voo",
                }).fillna("Não informada")

                # Dados gerais.
                total_pontos = len(df)

                primeira_posicao = df.iloc[0]
                ultima_posicao = df.iloc[-1]

                altitude_media = df["altitude"].mean()

                inicio = primeira_posicao["data_hora_utc"]
                fim = ultima_posicao["data_hora_utc"]

                duracao = fim - inicio

                st.divider()

                st.markdown("### Resumo da trajetória")

                c1, c2, c3, c4 = st.columns(4)

                c1.metric(
                    "Pontos registrados",
                    total_pontos,
                )

                c2.metric(
                    "Altitude média",
                    converter_altitude(altitude_media),
                )

                c3.metric(
                    "Primeiro registro",
                    inicio.strftime("%H:%M UTC"),
                )

                c4.metric(
                    "Último registro",
                    fim.strftime("%H:%M UTC"),
                )

                st.caption(
                    f"Período entre os pontos: {duracao}"
                )

                st.divider()

                st.markdown("### Mapa da trajetória")

                fig = px.line_map(
                    df,
                    lat="latitude",
                    lon="longitude",
                    hover_name="data_hora_utc",
                    hover_data=[
                        "altitude",
                        "rumo",
                        "situação",
                    ],
                    zoom=4,
                    height=600,
                    map_style="carto-darkmatter",
                    title=f"Percurso da aeronave {icao24.upper()}",
                )

                # Marcador do primeiro ponto.
                fig.add_scattermap(
                    lat=[primeira_posicao["latitude"]],
                    lon=[primeira_posicao["longitude"]],
                    mode="markers",
                    marker=dict(
                        size=13,
                        color="#36D6A0",
                    ),
                    name="Início",
                    hovertemplate="Início da trajetória<extra></extra>",
                )

                # Marcador do último ponto.
                fig.add_scattermap(
                    lat=[ultima_posicao["latitude"]],
                    lon=[ultima_posicao["longitude"]],
                    mode="markers",
                    marker=dict(
                        size=15,
                        color="#FF657A",
                    ),
                    name="Última posição",
                    hovertemplate="Última posição registrada<extra></extra>",
                )

                fig = configurar_grafico(fig)

                st.plotly_chart(
                    fig,
                    use_container_width=True,
                )

                st.divider()

                st.markdown("### Evolução da altitude")

                altitude_df = df.dropna(
                    subset=["altitude"]
                )

                if not altitude_df.empty:

                    fig_altitude = px.area(
                        altitude_df,
                        x="data_hora_utc",
                        y="altitude",
                        title="Altitude ao longo da trajetória",
                        labels={
                            "data_hora_utc": "Horário (UTC)",
                            "altitude": "Altitude (m)",
                        },
                    )

                    fig_altitude.update_traces(
                        line_color="#36D6E7",
                        fillcolor="rgba(54,214,231,0.15)",
                    )

                    st.plotly_chart(
                        configurar_grafico(fig_altitude),
                        use_container_width=True,
                    )

                else:
                    st.info(
                        "Não há dados de altitude disponíveis."
                    )

                st.divider()

                st.markdown("### Posições registradas")

                tabela = df.rename(columns={
                    "tempo": "Tempo Unix",
                    "latitude": "Latitude",
                    "longitude": "Longitude",
                    "altitude": "Altitude (m)",
                    "rumo": "Direção (graus)",
                    "no_chao": "Em solo",
                    "data_hora_utc": "Data e hora (UTC)",
                    "situação": "Situação",
                })

                st.dataframe(
                    tabela[
                        [
                            "Data e hora (UTC)",
                            "Latitude",
                            "Longitude",
                            "Altitude (m)",
                            "Direção (graus)",
                            "Em solo",
                            "Situação",
                        ]
                    ],
                    use_container_width=True,
                    hide_index=True,
                )

                exportar_csv(
                    tabela,
                    f"trajetoria_{icao24}.csv",
                )

                st.caption(
                    "A trajetória representa os pontos disponibilizados "
                    "pela OpenSky, não necessariamente o percurso completo "
                    "realizado pela aeronave."
                )

            except (
                requests.RequestException,
                ValueError,
                KeyError,
            ) as erro:

                mostrar_erro(
                    "trajetória da aeronave",
                    erro,
                )


# ============================================================
# 11. RODAPÉ
# ============================================================

st.divider()

st.markdown(
    """
    <div class="footer">
        FLIGHT RADAR | AIR TRAFFIC ANALYTICS<br>
        Desenvolvido com Python, Streamlit, Plotly e OpenSky Network.<br>
        Dados sujeitos à disponibilidade da fonte consultada.
    </div>
    """,
    unsafe_allow_html=True,
)
