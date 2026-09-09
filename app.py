from flask import Flask, render_template, request, send_file
import io

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.colors import HexColor
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, HRFlowable, ListFlowable, ListItem,
)
from reportlab.lib.styles import ParagraphStyle

app = Flask(__name__)

INK = HexColor("#22252A")
INK_SOFT = HexColor("#5B5F66")
TEAL_DEEP = HexColor("#0A4F42")
GOLD = HexColor("#B8863B")
LINE = HexColor("#E3E1DA")


def parse_cv_data(form):
    """Ambil & rapikan data form jadi satu struktur dict yang dipakai
    oleh template preview maupun template PDF, biar keduanya konsisten."""

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


def build_pdf(data: dict) -> bytes:
    """Susun dokumen PDF dari data CV pakai ReportLab (platypus)."""

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        topMargin=20 * mm,
        bottomMargin=20 * mm,
        leftMargin=18 * mm,
        rightMargin=18 * mm,
        title=data["nama"] or "CV",
    )

    style_nama = ParagraphStyle(
        "Nama", fontName="Helvetica-Bold", fontSize=22, leading=26,
        textColor=INK, spaceAfter=4, alignment=TA_LEFT,
    )
    style_gelar = ParagraphStyle(
        "Gelar", fontName="Helvetica-Bold", fontSize=11, leading=14,
        textColor=TEAL_DEEP, spaceAfter=6,
    )
    style_kontak = ParagraphStyle(
        "Kontak", fontName="Helvetica", fontSize=9, leading=13,
        textColor=INK_SOFT, spaceAfter=14,
    )
    style_h2 = ParagraphStyle(
        "H2", fontName="Helvetica-Bold", fontSize=9.5, leading=12,
        textColor=GOLD, spaceBefore=14, spaceAfter=8,
    )
    style_body = ParagraphStyle(
        "Body", fontName="Helvetica", fontSize=10, leading=15, textColor=INK,
    )
    style_item = ParagraphStyle(
        "Item", fontName="Helvetica", fontSize=10, leading=15,
        textColor=INK, spaceAfter=4,
    )

    story = []
    story.append(Paragraph(data["nama"] or "Nama Lengkap", style_nama))
    if data["gelar"]:
        story.append(Paragraph(data["gelar"], style_gelar))

    kontak_items = [x for x in [data["email"], data["telepon"], data["lokasi"]] if x]
    kontak_items += data["kontak_lain"]
    if kontak_items:
        story.append(Paragraph("  ·  ".join(kontak_items), style_kontak))

    def add_section(title, body_flowable):
        story.append(HRFlowable(width="100%", color=LINE, thickness=1))
        story.append(Paragraph(title.upper(), style_h2))
        story.append(body_flowable)

    if data["ringkasan"]:
        add_section("Ringkasan", Paragraph(data["ringkasan"], style_body))

    if data["pendidikan"]:
        items = [ListItem(Paragraph(x, style_item), leftIndent=6) for x in data["pendidikan"]]
        add_section("Pendidikan", ListFlowable(items, bulletType="bullet", start="•"))

    if data["pengalaman"]:
        items = [ListItem(Paragraph(x, style_item), leftIndent=6) for x in data["pengalaman"]]
        add_section("Pengalaman & Proyek", ListFlowable(items, bulletType="bullet", start="•"))

    if data["skill"]:
        story.append(HRFlowable(width="100%", color=LINE, thickness=1))
        story.append(Paragraph("SKILL", style_h2))
        story.append(Paragraph(" &nbsp;&nbsp; ".join(data["skill"]), style_body))

    doc.build(story)
    buffer.seek(0)
    return buffer.read()


@app.route("/generate-pdf", methods=["POST"])
def generate_pdf():
    data = parse_cv_data(request.form)
    pdf_bytes = build_pdf(data)
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
