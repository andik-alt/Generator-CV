from flask import Flask, render_template, request, send_file
import io

app = Flask(__name__)


def parse_cv_data(form):
    def split_lines(field_name):
        raw = form.get(field_name, "")
        return [line.strip() for line in raw.splitlines() if line.strip()]

    return {
        "nama": form.get("nama", "").strip(),
        "gelar": form.get("gelar", "").strip(),
        "email": form.get("email", "").strip(),
        "telepon": form.get("telepon", "").strip(),
        "lokasi": form.get("lokasi", "").strip(),
        "ringkasan": form.get("ringkasan", "").strip(),
        "pendidikan": split_lines("pendidikan"),
        "pengalaman": split_lines("pengalaman"),
        "skill": [s.strip() for s in form.get("skill", "").split(",") if s.strip()],
        "kontak_lain": split_lines("kontak_lain"),
    }


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@app.route("/generate-pdf", methods=["POST"])
def generate_pdf():
    data = parse_cv_data(request.form)
    html = render_template("cv_pdf.html", data=data)

    from weasyprint import HTML  # import lokal: cukup dibutuhkan di route ini

    pdf_bytes = HTML(string=html).write_pdf()
    buffer = io.BytesIO(pdf_bytes)
    buffer.seek(0)

    nama_file = (data["nama"] or "cv").lower().replace(" ", "-")
    return send_file(
        buffer,
        mimetype="application/pdf",
        as_attachment=True,
        download_name=f"cv-{nama_file}.pdf",
    )


if __name__ == "__main__":
    app.run(debug=True)
