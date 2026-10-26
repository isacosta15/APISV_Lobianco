
import requests
import pandas as pd
import streamlit as st
import plotly.express as px

BASE = "https://opensky-network.org/api"

st.set_page_config(page_title="Rastreador de Voos", layout="wide")
st.title("✈️ Rastreador de Voos")
st.caption("Dados da OpenSky Network")

modo = st.sidebar.radio(
    "Modo de consulta",
    ["Aeronaves no Brasil", "Trajetória por ICAO24"],
)

if modo == "Aeronaves no Brasil":
    st.write(
        "Consulte posições dentro de uma caixa geográfica "
        "aproximada que cobre o Brasil."
    )

    col1, col2 = st.columns(2)
    with col1:
        lat_min = st.number_input("Latitude mínima", value=-33.75)
        lon_min = st.number_input("Longitude mínima", value=-73.99)
    with col2:
        lat_max = st.number_input("Latitude máxima", value=5.27)
        lon_max = st.number_input("Longitude máxima", value=-34.79)

    pais = st.text_input(
        "Filtrar país de origem (opcional)", ""
    )
    categoria = st.selectbox(
        "Categoria da aeronave",
        ["Todas", "Avião", "Helicóptero", "Outra/desconhecida"],
    )

    if st.button("Consultar aeronaves", type="primary"):
        if lat_min >= lat_max or lon_min >= lon_max:
            st.error("Confira os limites geográficos.")
            st.stop()

        try:
            with st.spinner("Consultando a OpenSky..."):
                r = requests.get(
                    f"{BASE}/states/all",
                    params={
                        "lamin": lat_min,
                        "lamax": lat_max,
                        "lomin": lon_min,
                        "lomax": lon_max,
                        "extended": 1,
                    },
                    timeout=60,
                )
                r.raise_for_status()
                resposta = r.json()

            campos = [
                "icao24", "callsign", "origin_country",
                "time_position", "last_contact", "longitude",
                "latitude", "baro_altitude", "on_ground",
                "velocity", "true_track", "vertical_rate",
                "sensors", "geo_altitude", "squawk",
                "spi", "position_source", "category",
            ]

            df = pd.DataFrame(
                resposta.get("states") or [],
                columns=campos,
            )

            if df.empty:
                st.warning("Nenhuma aeronave retornada.")
                st.stop()

            df = df.dropna(subset=["latitude", "longitude"])

            if pais.strip():
                df = df[
                    df["origin_country"].str.contains(
                        pais, case=False, na=False, regex=False
                    )
                ]

            # A categoria estendida é um código numérico.
            # Código 6 = avião; código 8 = helicóptero.
            if categoria == "Avião":
                df = df[df["category"] == 6]
            elif categoria == "Helicóptero":
                df = df[df["category"] == 8]
            elif categoria == "Outra/desconhecida":
                df = df[
                    ~df["category"].isin([6, 8])
                    | df["category"].isna()
                ]

            st.metric("Aeronaves encontradas", len(df))

            if df.empty:
                st.info("Nenhuma aeronave corresponde aos filtros.")
                st.stop()

            fig = px.scatter_map(
                df,
                lat="latitude",
                lon="longitude",
                hover_name="callsign",
                hover_data=[
                    "icao24", "origin_country",
                    "baro_altitude", "velocity", "category",
                ],
                color="origin_country",
                zoom=2,
                height=650,
                title="Posições atuais retornadas pela API",
            )
            st.plotly_chart(fig, use_container_width=True)
            st.dataframe(df, use_container_width=True)

            st.download_button(
                "Baixar dados CSV",
                df.to_csv(index=False).encode("utf-8-sig"),
                "aeronaves.csv",
                "text/csv",
            )

        except requests.RequestException as e:
            st.error(
                f"Erro de acesso à OpenSky: {e}. "
                "Verifique os limites de consulta e tente novamente."
            )

else:
    st.write(
        "Informe o endereço ICAO24 hexadecimal de uma aeronave, "
        "por exemplo: 3c6444."
    )
    icao24 = st.text_input("ICAO24", "3c6444").strip().lower()

    if st.button("Consultar trajetória", type="primary"):
        if len(icao24) != 6 or any(
            c not in "0123456789abcdef" for c in icao24
        ):
            st.error("O ICAO24 deve conter 6 caracteres hexadecimais.")
            st.stop()

        try:
            with st.spinner("Buscando trajetória..."):
                r = requests.get(
                    f"{BASE}/tracks/all/{icao24}",
                    timeout=60,
                )
                r.raise_for_status()
                track = r.json()

            pontos = track.get("path") or []
            if not pontos:
                st.warning(
                    "A API não retornou pontos de trajetória para "
                    "essa aeronave. Tente outro ICAO24."
                )
                st.stop()

            # Formato da trajetória:
            # [tempo Unix, latitude, longitude, altitude,
            #  rumo verdadeiro, no_chao]
            df = pd.DataFrame(
                pontos,
                columns=[
                    "tempo", "latitude", "longitude",
                    "altitude", "rumo", "no_chao",
                ],
            )
            df = df.dropna(subset=["latitude", "longitude"])
            df["data_hora_utc"] = pd.to_datetime(
                df["tempo"], unit="s", utc=True
            )

            st.metric("Pontos de trajetória", len(df))
            st.write("Última posição registrada:")
            st.dataframe(df.tail(1), use_container_width=True)

            fig = px.line_map(
                df,
                lat="latitude",
                lon="longitude",
                hover_name="data_hora_utc",
                hover_data=["altitude", "rumo"],
                zoom=3,
                height=650,
                title=f"Trajetória ICAO24: {icao24}",
            )
            fig.add_scattermap(
                lat=df["latitude"],
                lon=df["longitude"],
                mode="markers",
                name="Posições",
            )
            st.plotly_chart(fig, use_container_width=True)
            st.dataframe(df, use_container_width=True)

            st.download_button(
                "Baixar trajetória CSV",
                df.to_csv(index=False).encode("utf-8-sig"),
                f"trajetoria_{icao24}.csv",
                "text/csv",
            )

        except requests.RequestException as e:
            st.error(
                f"Erro na consulta: {e}. "
                "A trajetória pode não estar disponível para "
                "a aeronave ou o período solicitado."
            )
