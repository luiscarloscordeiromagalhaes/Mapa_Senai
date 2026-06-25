from flask import Flask, render_template
import pandas as pd
import folium
import json
import os

app = Flask(__name__)

# =====================================
# GOOGLE SHEETS
# =====================================

SHEET_ID = "1cHfxBwPm0Q3ctoQvcP096S2iuGrF_yNphSDBO-ineQA"

CSV_URL = (
    f"https://docs.google.com/spreadsheets/d/"
    f"{SHEET_ID}/export?format=csv"
)

# =====================================
# ROTA PRINCIPAL
# =====================================

@app.route("/")
def index():

    # Lê a planilha
    df = pd.read_csv(CSV_URL)

    # Remove espaços extras dos nomes das colunas
    df.columns = df.columns.str.strip()



    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

    GEOJSON_PATH = os.path.join(
        BASE_DIR,
        "static",
        "geojs-26-mun.json"
    )

    with open(GEOJSON_PATH, "r", encoding="utf-8") as arquivo:
        geojson = json.load(arquivo)

    # Centro de Pernambuco
    mapa = folium.Map(
        location=[-8.4, -37.5],
        zoom_start=8,
        tiles="OpenStreetMap"
    )

    # =====================================
    # MUNICÍPIOS
    # =====================================

    folium.GeoJson(
        geojson,
        style_function=lambda feature: {
            "fillColor": "#D9D9D9",
            "color": "black",
            "weight": 0.5,
            "fillOpacity": 0.2
        }
    ).add_to(mapa)

    # =====================================
    # EMPRESAS
    # =====================================

    for _, empresa in df.iterrows():

        try:

            nome = str(empresa["Empresa"])

            latitude = float(str(empresa["Latitude"]).replace(",", "."))
            longitude = float(str(empresa["Longitude"]).replace(",", "."))

            consultor = str(empresa.get("Consultor", "")).strip().upper()

            if consultor == "":
                cor = "black"
            elif consultor == "KALLEBY":
                cor = "orange"
            elif consultor == "DEOCLECIO":
                cor = "red"
            elif consultor == "LUÍS" or consultor == "LUIS":
                cor = "green"
            else:
                cor = "black"  # outros consultores

            folium.Marker(
                location=[latitude, longitude],
                popup=f"""
                <b>{nome}</b><br>
                Consultor: {consultor if consultor else 'Não informado'}<br>
                Latitude: {latitude}<br>
                Longitude: {longitude}
                """,
                tooltip=nome,
                icon=folium.Icon(
                    color=cor,
                    icon="briefcase",
                    prefix="fa"
                )
            ).add_to(mapa)

        except Exception as e:
            print(f"Erro empresa: {e}")
            continue


    legenda = """
    <div style="
    position: fixed;
    bottom: 50px;
    left: 50px;
    width: 180px;
    background-color: white;
    border:2px solid grey;
    z-index:9999;
    font-size:14px;
    padding:10px;
    ">
    <b>Consultores</b><br>
    🟢 Luís<br>
    🔴 Deoclecio<br>
    🟡 Kalleby<br>
    ⚫ Sem consultor
    </div>
    """

    mapa.get_root().html.add_child(folium.Element(legenda))
    mapa_html = mapa._repr_html_()

    return render_template(
        "index.html",
        mapa=mapa_html,
        total_empresas=len(df)
    )

# =====================================
# EXECUÇÃO LOCAL
# =====================================

if __name__ == "__main__":
    app.run(debug=True)