from flask import Flask, request, send_file
import pandas as pd
import os

app = Flask(__name__)

produse = []
faptic = {}

@app.route("/")
def home():

    html = """
    <h1>MegaGen Inventar</h1>

    <form action="/upload" method="post" enctype="multipart/form-data">
        <input type="file" name="fisier">
        <button type="submit">Import Excel</button>
    </form>

    <br>
    <a href="/scan">SCANARE</a>

<br><br>
<a href="/raport">VEZI RAPORT</a>

    <p>Produse importate: """ + str(len(produse)) + """</p>
    """

    return html


@app.route("/upload", methods=["POST"])
def upload():

    global produse

    fisier = request.files["fisier"]

    df = pd.read_excel(fisier)

    produse = df.to_dict("records")

    return """
    <h2>Import realizat cu succes</h2>
    <a href="/">Inapoi</a>
    """


@app.route("/scan")
def scan():

    return """
    <h2>Scanare QR</h2>

    <script src="https://unpkg.com/html5-qrcode"></script>

    <div id="reader" style="width:350px"></div>

    <form id="formular" action="/cauta" method="post">
        <input type="text" id="cod" name="cod" style="width:300px">
        <button type="submit">Scaneaza</button>
    </form>

    <script>
    function onScanSuccess(decodedText) {
        document.getElementById("cod").value = decodedText;
        document.getElementById("formular").submit();
    }

    let scanner = new Html5QrcodeScanner(
        "reader",
        { fps: 10, qrbox: 250 }
    );

    scanner.render(onScanSuccess);
    </script>

    <br>
    <a href="/">Acasa</a>
    """

@app.route("/cauta", methods=["POST"])
def cauta():

    cod = request.form["cod"].strip()

    for p in produse:

        if str(p.get("COD","")).strip() == cod:

            if cod not in faptic:
                faptic[cod] = 0

            faptic[cod] += 1

            return f"""
            <h2>Produs gasit</h2>

            <p><b>Cod:</b> {cod}</p>
            <p><b>Denumire:</b> {p.get('DENUMIRE','')}</p>
            <p><b>Scriptic:</b> {p.get('Stoc Scriptic','')}</p>
            <p><b>Faptic:</b> {faptic[cod]}</p>

            <a href="/scan">Scanare urmatoare</a>
            """

    return """
    <h2>Produs negasit</h2>
    <a href="/scan">Inapoi</a>
    """
@app.route("/raport")
def raport():

    html = """
    <h1>Raport inventar</h1>

    <table border="1">
    <tr>
        <th>Cod</th>
        <th>Denumire</th>
        <th>Scriptic</th>
        <th>Faptic</th>
        <th>Diferenta</th>
    </tr>
    """

    for cod, cant in faptic.items():

        denumire = ""
        scriptic = 0

        for p in produse:

            if str(p.get("COD","")).strip() == cod:

                denumire = str(p.get("DENUMIRE",""))
                scriptic = int(p.get("Stoc Scriptic",0))

                break

        diferenta = cant - scriptic

        html += f"""
        <tr>
            <td>{cod}</td>
            <td>{denumire}</td>
            <td>{scriptic}</td>
            <td>{cant}</td>
            <td>{diferenta}</td>
        </tr>
        """

    html += """
    </table>

    <br><br>

    <a href='/export'>EXPORT EXCEL</a>

    <br><br>

    <a href='/'>Acasa</a>
    """

    return html
@app.route("/export")
def export():

    raport = []

    for cod, cant in faptic.items():

        denumire = ""
        scriptic = 0

        for p in produse:

            if str(p.get("COD","")).strip() == cod:

                denumire = str(p.get("DENUMIRE",""))
                scriptic = int(p.get("Stoc Scriptic",0))

                break

        raport.append({
            "COD": cod,
            "DENUMIRE": denumire,
            "SCRIPTIC": scriptic,
            "FAPTIC": cant,
            "DIFERENTA": cant - scriptic
        })

    df = pd.DataFrame(raport)

    fisier = "raport_inventar.xlsx"

    df.to_excel(fisier, index=False)

    return send_file(fisier, as_attachment=True)
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)