from flask import Flask, request, send_file
import pandas as pd
import re

app = Flask(__name__)

produse = []
faptic = {}

@app.route("/")
def home():

    return f"""
    <h1>MegaGen Inventar</h1>

    <form action="/upload" method="post" enctype="multipart/form-data">
        <input type="file" name="fisier" required>
        <button type="submit">Import Excel</button>
    </form>

    <br><br>

    <a href="/scan">SCANARE</a>

    <br><br>

    <a href="/raport">VEZI RAPORT</a>

    <br><br>

    Produse importate: {len(produse)}
    """


@app.route("/upload", methods=["POST"])
def upload():

    global produse

    fisier = request.files["fisier"]

    df = pd.read_excel(fisier)

    df.columns = df.columns.str.strip()

    produse = df.to_dict("records")

    return """
    <h2>Import realizat cu succes</h2>
    <a href="/">Inapoi</a>
    """


@app.route("/scan")
def scan():

    return """
    <h2>Scanare QR / DataMatrix</h2>

    <script src="https://unpkg.com/html5-qrcode"></script>

    <div id="reader" style="width:400px"></div>

    <form id="formular" action="/cauta" method="post">
        <input type="hidden" id="cod" name="cod">
    </form>

    <script>

    let scanat = false;

    function onScanSuccess(decodedText) {

        if(scanat) return;

        scanat = true;

        document.getElementById("cod").value = decodedText;

        document.getElementById("formular").submit();
    }

    let scanner = new Html5QrcodeScanner(
        "reader",
        {
            fps: 10,
            qrbox: 250
        }
    );

    scanner.render(onScanSuccess);

    </script>

    <br>

    <a href="/">Acasa</a>
    """


@app.route("/cauta", methods=["POST"])
def cauta():

    text_scanat = request.form["cod"].strip()

    cod = ""

    match = re.search(r"240([A-Za-z0-9]+)", text_scanat)

    if match:
        cod = match.group(1)
    else:
        cod = text_scanat

    cod = cod.strip()

    for p in produse:

        cod_excel = str(p.get("COD", "")).strip()

        if cod_excel.upper() == cod.upper():

            if cod not in faptic:
                faptic[cod] = 0

            faptic[cod] += 1

            return f"""
            <h2 style='color:green'>PRODUS GASIT</h2>

            <p><b>Cod:</b> {cod}</p>
            <p><b>Denumire:</b> {p.get('DENUMIRE','')}</p>
            <p><b>Faptic:</b> {faptic[cod]}</p>

            <script>
            setTimeout(function(){{
                window.location='/scan';
            }},1500);
            </script>
            """

    return f"""
    <h2 style='color:red'>PRODUS NEGASIT</h2>

    <p><b>Text scanat:</b></p>

    <pre>{text_scanat}</pre>

    <p><b>Cod extras:</b> {cod}</p>

    <script>
    setTimeout(function(){{
        window.location='/scan';
    }},3000);
    </script>
    """


@app.route("/raport")
def raport():

    html = """
    <h1>Raport Inventar</h1>

    <table border="1" cellpadding="5">
    <tr>
        <th>COD</th>
        <th>DENUMIRE</th>
        <th>FAPTIC</th>
    </tr>
    """

    for cod, cant in faptic.items():

        denumire = ""

        for p in produse:

            if str(p.get("COD","")).strip().upper() == cod.upper():

                denumire = str(p.get("DENUMIRE",""))

                break

        html += f"""
        <tr>
            <td>{cod}</td>
            <td>{denumire}</td>
            <td>{cant}</td>
        </tr>
        """

    html += """
    </table>

    <br><br>

    <a href="/export">EXPORT EXCEL</a>

    <br><br>

    <a href="/">Acasa</a>
    """

    return html


@app.route("/export")
def export():

    raport = []

    for cod, cant in faptic.items():

        denumire = ""

        for p in produse:

            if str(p.get("COD","")).strip().upper() == cod.upper():

                denumire = str(p.get("DENUMIRE",""))

                break

        raport.append({
            "COD": cod,
            "DENUMIRE": denumire,
            "FAPTIC": cant
        })

    df = pd.DataFrame(raport)

    fisier = "raport_inventar.xlsx"

    df.to_excel(fisier, index=False)

    return send_file(fisier, as_attachment=True)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)