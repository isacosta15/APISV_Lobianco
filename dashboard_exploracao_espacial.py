import os
import requests
import pandas as pd
import streamlit as st
import plotly.express as px
from datetime import date, timedelta

st.set_page_config(page_title="Exploração Espacial", layout="wide")
st.title("🚀 Dashboard de Exploração Espacial")
st.caption("Dados científicos da NASA e do NASA Exoplanet Archive")

NASA_BASE = "https://api.nasa.gov"
EONET_URL = "https://eonet.gsfc.nasa.gov/api/v3/events"
EXOPLANET_URL = (
    "https://exoplanetarchive.ipac.caltech.edu/TAP/sync"
)

api_key = st.sidebar.text_input(
    "Chave NASA API",
    value=os.getenv("NASA_API_KEY", "DEMO_KEY"),
    type="password",
)

aba = st.sidebar.radio(
    "Escolha uma consulta",
    [
        "Asteroides",
        "Imagem APOD",
        "Exoplanetas",
        "Eventos naturais",
    ],
)

def consultar_json(url, params=None):
    response = requests.get(
        url, params=params, timeout=60
    )
    response.raise_for_status()
    return response.json()

if aba == "Asteroides":
    st.subheader("☄️ Asteroides próximos da Terra")

    hoje = date.today()
    inicio = st.date_input(
        "Data inicial", hoje - timedelta(days=6)
    )
    fim = st.date_input("Data final", hoje)

    if st.button("Buscar asteroides", type="primary"):
        if inicio > fim:
            st.error("A data inicial deve ser anterior à final.")
            st.stop()

        if (fim - inicio).days > 6:
            st.error(
                "A NeoWs permite no máximo 7 dias por consulta. "
                "Escolha um intervalo menor."
            )
            st.stop()

        try:
            with st.spinner("Buscando asteroides..."):
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
                    aprox = aproximacoes[0] if aproximacoes else {}

                    registros.append({
                        "nome": obj.get("name"),
                        "data": data,
                        "diametro_m": (
                            obj.get("estimated_diameter", {})
                            .get("meters", {})
                            .get("estimated_diameter_max")
                        ),
                        "potencialmente_perigoso": (
                            obj.get("is_potentially_hazardous_asteroid")
                        ),
                        "distancia_km": (
                            aprox.get("miss_distance", {})
                            .get("kilometers")
                        ),
                        "velocidade_km_s": (
                            aprox.get("relative_velocity", {})
                            .get("kilometers_per_second")
                        ),
                    })

            df = pd.DataFrame(registros)

            if df.empty:
                st.info("Nenhum asteroide retornado.")
                st.stop()

            for col in [
                "diametro_m", "distancia_km", "velocidade_km_s"
            ]:
                df[col] = pd.to_numeric(df[col], errors="coerce")

            st.metric("Objetos encontrados", len(df))
            st.metric(
                "Potencialmente perigosos",
                int(df["potencialmente_perigoso"].sum()),
            )

            fig = px.scatter(
                df,
                x="distancia_km",
                y="velocidade_km_s",
                size="diametro_m",
                color="potencialmente_perigoso",
                hover_name="nome",
                hover_data=["data"],
                log_x=True,
                title="Distância da Terra x velocidade relativa",
                labels={
                    "distancia_km": "Distância (km)",
                    "velocidade_km_s": "Velocidade (km/s)",
                    "potencialmente_perigoso": "Potencialmente perigoso",
                },
            )
            st.plotly_chart(fig, use_container_width=True)
            st.dataframe(df, use_container_width=True)

            st.download_button(
                "Baixar CSV",
                df.to_csv(index=False).encode("utf-8-sig"),
                "asteroides.csv",
                "text/csv",
            )

        except requests.RequestException as e:
            st.error(f"Erro na NASA NeoWs: {e}")

elif aba == "Imagem APOD":
    st.subheader("🌌 Astronomy Picture of the Day")

    data_apod = st.date_input("Data da imagem", date.today())

    if st.button("Buscar imagem", type="primary"):
        try:
            # Endpoint legado da APOD, ainda disponível
            # durante o período de migração documentado pela NASA.
            dados = consultar_json(
                f"{NASA_BASE}/planetary/apod",
                {
                    "date": data_apod.isoformat(),
                    "api_key": api_key,
                },
            )

            st.header(dados.get("title", "Imagem astronômica"))
            st.caption(dados.get("date", ""))

            if dados.get("media_type") == "image":
                st.image(
                    dados.get("url"),
                    caption=dados.get("title"),
                    use_container_width=True,
                )
            elif dados.get("url"):
                st.video(dados["url"])

            st.write(dados.get("explanation", ""))
            if dados.get("copyright"):
                st.caption(f"Crédito: {dados['copyright']}")

        except requests.RequestException as e:
            st.error(
                f"Erro na APOD: {e}. Verifique a chave e a "
                "disponibilidade do endpoint."
            )

elif aba == "Exoplanetas":
    st.subheader("🪐 Exoplanetas confirmados")

    limite = st.slider(
        "Quantidade de registros", 100, 2000, 500, step=100
    )

    if st.button("Buscar exoplanetas", type="primary"):
        try:
            with st.spinner("Consultando o arquivo de exoplanetas..."):
                query = (
                    "select pl_name, discoverymethod "
                    "from ps where default_flag = 1 "
                    f"order by pl_name"
                    f""
                )
                # Limite aplicado à consulta para reduzir o volume.
                query += f""

                r = requests.get(
                    EXOPLANET_URL,
                    params={
                        "query": query,
                        "format": "json",
                    },
                    timeout=60,
                )
                r.raise_for_status()
                dados = r.json()

            df = pd.DataFrame(dados)

            if df.empty:
                st.warning("Nenhum registro encontrado.")
                st.stop()

            df = df.head(limite)
            st.metric("Registros exibidos", len(df))

            metodos = (
                df["discoverymethod"]
                .fillna("Não informado")
                .value_counts()
                .rename_axis("Método")
                .reset_index(name="Quantidade")
            )

            fig = px.bar(
                metodos,
                x="Quantidade",
                y="Método",
                orientation="h",
                title="Métodos de descoberta dos exoplanetas",
            )
            fig.update_layout(yaxis={"categoryorder": "total ascending"})
            st.plotly_chart(fig, use_container_width=True)
            st.dataframe(df, use_container_width=True)

            st.download_button(
                "Baixar CSV",
                df.to_csv(index=False).encode("utf-8-sig"),
                "exoplanetas.csv",
                "text/csv",
            )

        except requests.RequestException as e:
            st.error(f"Erro no arquivo de exoplanetas: {e}")

elif aba == "Eventos naturais":
    st.subheader("🌍 Eventos naturais nas últimas 48 horas")

    if st.button("Buscar eventos", type="primary"):
        try:
            with st.spinner("Consultando eventos..."):
                dados = consultar_json(
                    EONET_URL,
                    {"status": "all", "days": 2, "limit": 500},
                )

            eventos = []
            for evento in dados.get("events", []):
                geometrias = evento.get("geometry", [])
                if not geometrias:
                    continue

                # Usa a geometria mais recente que tenha coordenadas.
                geo = next(
                    (
                        g for g in reversed(geometrias)
                        if g.get("coordinates")
                    ),
                    None,
                )
                if not geo:
                    continue

                coords = geo["coordinates"]
                if geo.get("type") == "Point":
                    lon, lat = coords[0], coords[1]
                else:
                    # Para linhas/polígonos, usa uma coordenada
                    # disponível como marcador aproximado.
                    ponto = coords[0]
                    while isinstance(ponto[0], list):
                        ponto = ponto[0]
                    lon, lat = ponto[0], ponto[1]

                categorias = ", ".join(
                    c.get("title", "")
                    for c in evento.get("categories", [])
                )

                eventos.append({
                    "nome": evento.get("title"),
                    "categoria": categorias,
                    "data": geo.get("date"),
                    "latitude": lat,
                    "longitude": lon,
                    "url": evento.get("sources", [{}])[0].get("url"),
                })

            df = pd.DataFrame(eventos)

            if df.empty:
                st.info("Nenhum evento com coordenadas disponível.")
                st.stop()

            st.metric("Eventos com localização", len(df))

            fig = px.scatter_map(
                df,
                lat="latitude",
                lon="longitude",
                color="categoria",
                hover_name="nome",
                hover_data=["data"],
                zoom=1,
                height=650,
                title="Eventos naturais reportados",
            )
            st.plotly_chart(fig, use_container_width=True)
            st.dataframe(df, use_container_width=True)

            st.download_button(
                "Baixar CSV",
                df.to_csv(index=False).encode("utf-8-sig"),
                "eventos_naturais.csv",
                "text/csv",
            )

        except requests.RequestException as e:
            st.error(f"Erro no EONET: {e}")
