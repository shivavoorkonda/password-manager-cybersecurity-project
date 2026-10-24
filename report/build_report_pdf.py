"""Build the academic report PDF from its Markdown source using ReportLab."""
from __future__ import annotations

import math
import re
import shutil
from pathlib import Path

from PIL import Image as PILImage, ImageDraw, ImageFont
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    Image, KeepTogether, PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table,
    TableStyle,
)

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "ACADEMIC_PROJECT_REPORT.md"
OUTPUT = ROOT.parent / "output" / "pdf" / "secure_password_manager_project_report.pdf"
TEMP = ROOT / ".pdf-build"


def clean(value: str) -> str:
    value = value.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    value = re.sub(r"`([^`]+)`", r"<font name='Courier'>\1</font>", value)
    value = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", value)
    value = re.sub(r"\*(.+?)\*", r"<i>\1</i>", value)
    value = re.sub(r"\[([^]]+)\]\([^)]+\)", r"\1", value)
    return value.replace("—", "-").replace("–", "-").replace("’", "'").replace("“", '"').replace("”", '"')


def image_flowable(relative_path: str) -> Image:
    source = ROOT / relative_path
    if source.suffix.lower() == ".svg":
        TEMP.mkdir(exist_ok=True)
        rendered = TEMP / f"{source.stem}.png"
        render_diagram(source.stem, rendered)
        source = rendered
    image = Image(str(source))
    max_width, max_height = 6.85 * inch, 5.5 * inch
    # Evaluation evidence should be readable without dominating the results pages.
    if source.name == "confusion_matrix_rf_clean.png":
        max_width, max_height = 4.6 * inch, 2.8 * inch
    scale = min(max_width / image.imageWidth, max_height / image.imageHeight, 1)
    image.drawWidth = image.imageWidth * scale
    image.drawHeight = image.imageHeight * scale
    image.hAlign = "CENTER"
    return image


def render_diagram(name: str, output: Path) -> None:
    """Portable raster render of the two editable report diagrams."""
    width, height = (1400, 820) if name == "system_architecture" else (1400, 700)
    canvas = PILImage.new("RGB", (width, height), "#f8fafc")
    draw = ImageDraw.Draw(canvas)
    regular = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 20)
    bold = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", 24)
    title_font = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", 38)
    small = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 16)

    def text_box(box, title, lines, fill, outline):
        x1, y1, x2, y2 = box
        draw.rounded_rectangle(box, radius=16, fill=fill, outline=outline, width=3)
        draw.text((x1 + 22, y1 + 18), title, font=bold, fill="#0f172a")
        y = y1 + 62
        for line in lines:
            draw.text((x1 + 22, y), line, font=regular, fill="#334155")
            y += 28

    def arrow(start, end, label=None):
        draw.line([start, end], fill="#475569", width=4)
        angle = math.atan2(end[1] - start[1], end[0] - start[0])
        left = angle + math.pi * 0.83
        right = angle - math.pi * 0.83
        draw.polygon([
            end,
            (end[0] + 18 * math.cos(left), end[1] + 18 * math.sin(left)),
            (end[0] + 18 * math.cos(right), end[1] + 18 * math.sin(right)),
        ], fill="#475569")
        if label:
            draw.text(((start[0] + end[0]) / 2 - 55, (start[1] + end[1]) / 2 - 24), label, font=small, fill="#475569")

    if name == "system_architecture":
        regular = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 18)
        bold = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", 21)
        title_font = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", 34)
        small = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 16)
        canvas = PILImage.new("RGB", (width, height), "#f8fafc")
        draw = ImageDraw.Draw(canvas)
        draw.text((width / 2, 34), "Secure Password Manager - System Architecture", font=title_font, fill="#0f172a", anchor="ma")
        draw.rounded_rectangle((65, 95, 1335, 395), radius=20, fill="#f4f8ff", outline="#2563eb", width=3)
        draw.text((100, 112), "Browser - React + TypeScript", font=bold, fill="#102238")

        def card(box, title, lines, fill, outline):
            x1, y1, x2, y2 = box
            draw.rounded_rectangle(box, radius=12, fill=fill, outline=outline, width=3)
            draw.text((x1 + 22, y1 + 20), title, font=bold, fill="#102238")
            y = y1 + 58
            for line in lines:
                draw.text((x1 + 22, y), line, font=regular, fill="#334155")
                y += 34

        def arrow_left(start, end, label=None):
            draw.line([start, end], fill="#475569", width=4)
            draw.polygon([end, (end[0] + 17, end[1] - 10), (end[0] + 17, end[1] + 10)], fill="#475569")
            if label:
                draw.text(((start[0] + end[0]) / 2, (start[1] + end[1]) / 2 - 24), label, font=small, fill="#475569", anchor="mm")

        # Browser components and internal flow.
        draw.line((450, 260, 520, 260), fill="#475569", width=4)
        draw.polygon([(520, 260), (503, 250), (503, 270)], fill="#475569")
        draw.line((870, 260, 940, 260), fill="#475569", width=4)
        draw.polygon([(940, 260), (923, 250), (923, 270)], fill="#475569")
        card((100, 150, 450, 350), "Encrypted local vault", ["PBKDF2-HMAC-SHA256 (600,000)", "AES-256-GCM; fresh IV per entry", "Encrypted records in localStorage"], "#ffffff", "#60a5fa")
        card((520, 150, 870, 350), "Password interface", ["Generator, search and categories", "Rule meter + zxcvbn in browser", "Analysis sends password to local Flask"], "#ffffff", "#60a5fa")
        card((940, 150, 1300, 350), "Security feedback", ["ML verdict and confidence", "Breach status and consensus", "Recommendations when needed"], "#ffffff", "#60a5fa")

        # Password-analysis request/response and HIBP range exchange.
        arrow((650, 350), (500, 450), "password -> Flask")
        arrow((620, 450), (850, 350), "analysis result")
        arrow((670, 545), (780, 545), "prefix only")
        arrow_left((780, 600), (670, 600), "suffixes")
        card((170, 450, 670, 665), "Local Flask service - 127.0.0.1:5000", ["Receives plaintext password over loopback", "Extracts 17 features -> active ML model", "/analyze returns verdict; /recommend is separate", "Computes SHA-1 and calls HIBP", "Input handled in memory; not stored"], "#ecfdf5", "#059669")
        card((780, 450, 1200, 665), "HIBP range API", ["Only first 5 hash characters leave device", "Returns suffix/count list for the prefix", "Flask checks full suffix locally", "HIBP never receives the full password"], "#fff7ed", "#ea580c")

        draw.rounded_rectangle((250, 725, 1150, 780), radius=10, fill="#f8fafc", outline="#64748b", width=3)
        draw.text((700, 752), "Separate Node.js / PostgreSQL scaffold - not connected to the browser-vault flow", font=small, fill="#334155", anchor="mm")
    else:
        draw.text((465, 30), "Operational Workflow", font=title_font, fill="#0f172a")
        steps = [
            (70, 125, "1. Unlock vault", "Master password", "#dbeafe", "#2563eb"),
            (390, 125, "2. Derive key", "Decrypt local vault", "#dbeafe", "#2563eb"),
            (710, 125, "3. Enter password", "Or use generator", "#dbeafe", "#2563eb"),
            (1030, 125, "4. Browser feedback", "Rule meter + zxcvbn", "#dbeafe", "#2563eb"),
            (1030, 330, "5. Loopback request", "Browser to Flask", "#d1fae5", "#059669"),
            (710, 330, "6. ML analysis", "17 features -> prediction", "#d1fae5", "#059669"),
            (390, 330, "7. HIBP range check", "Five SHA-1 chars only", "#ffedd5", "#ea580c"),
            (70, 330, "8. Return results", "Consensus + breach status", "#dbeafe", "#2563eb"),
            (390, 535, "9. Render UI", "Show recommendations if needed", "#dbeafe", "#2563eb"),
        ]
        for x, y, title, subtitle, fill, outline in steps:
            draw.rounded_rectangle((x, y, x + 250, y + 85), radius=14, fill=fill, outline=outline, width=3)
            draw.text((x + 20, y + 20), title, font=bold, fill="#0f172a")
            draw.text((x + 20, y + 53), subtitle, font=regular, fill="#334155")
        arrow((320, 168), (390, 168)); arrow((640, 168), (710, 168)); arrow((960, 168), (1030, 168)); arrow((1155, 210), (1155, 330)); arrow((1030, 373), (960, 373)); arrow((710, 373), (640, 373)); arrow((390, 373), (320, 373)); arrow((195, 415), (390, 577))
        draw.rounded_rectangle((760, 535, 1160, 615), radius=14, fill="#ffffff", outline="#64748b", width=2)
        draw.text((790, 556), "Security boundary", font=bold, fill="#0f172a")
        draw.text((790, 588), "Full password never reaches HIBP", font=regular, fill="#334155")
    canvas.save(output, "PNG")


def footer(canvas, doc):
    canvas.saveState()
    canvas.setStrokeColor(colors.HexColor("#b8ccc5"))
    canvas.line(doc.leftMargin, 0.53 * inch, A4[0] - doc.rightMargin, 0.53 * inch)
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.HexColor("#49635f"))
    canvas.drawString(doc.leftMargin, 0.34 * inch, "Secure Password Manager - Academic Project Report")
    canvas.drawRightString(A4[0] - doc.rightMargin, 0.34 * inch, f"Page {doc.page}")
    canvas.restoreState()


def build() -> None:
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="TitleCustom", parent=styles["Title"], fontName="Helvetica-Bold", fontSize=21, leading=26, textColor=colors.HexColor("#173b3f"), alignment=TA_CENTER, spaceAfter=18))
    styles.add(ParagraphStyle(name="H1Custom", parent=styles["Heading1"], fontName="Helvetica-Bold", fontSize=15, leading=19, textColor=colors.HexColor("#173b3f"), spaceBefore=16, spaceAfter=8, keepWithNext=True))
    styles.add(ParagraphStyle(name="H2Custom", parent=styles["Heading2"], fontName="Helvetica-Bold", fontSize=12, leading=15, textColor=colors.HexColor("#2f6f6d"), spaceBefore=12, spaceAfter=6, keepWithNext=True))
    styles.add(ParagraphStyle(name="BodyCustom", parent=styles["BodyText"], fontName="Helvetica", fontSize=9.4, leading=13.3, textColor=colors.HexColor("#263238"), spaceAfter=6, alignment=TA_LEFT))
    styles.add(ParagraphStyle(name="Caption", parent=styles["BodyText"], fontName="Helvetica-Oblique", fontSize=8.5, leading=11, textColor=colors.HexColor("#5b5c4f"), alignment=TA_CENTER, spaceAfter=10))
    styles.add(ParagraphStyle(name="ListCustom", parent=styles["BodyText"], fontName="Helvetica", fontSize=9.4, leading=13, leftIndent=15, firstLineIndent=-10, spaceAfter=3))

    story = []
    lines = SOURCE.read_text(encoding="utf-8").splitlines()
    index = 0
    while index < len(lines):
        line = lines[index].strip()
        if not line:
            index += 1
            continue
        if line == "<!-- pagebreak -->":
            story.append(PageBreak())
            index += 1
            continue
        image_match = re.match(r"!\[([^]]*)\]\(([^)]+)\)", line)
        if image_match:
            story.append(KeepTogether([image_flowable(image_match.group(2)), Spacer(1, 7)]))
            index += 1
            continue
        if line.startswith("# "):
            story.append(Paragraph(clean(line[2:]), styles["TitleCustom"]))
        elif line.startswith("## "):
            story.append(Paragraph(clean(line[3:]), styles["H1Custom"]))
        elif line.startswith("### "):
            story.append(Paragraph(clean(line[4:]), styles["H2Custom"]))
        elif line.startswith("|") and index + 1 < len(lines) and re.match(r"^\|[-:| ]+\|$", lines[index + 1].strip()):
            raw_rows = []
            index += 2
            while index < len(lines) and lines[index].strip().startswith("|"):
                raw_rows.append([cell.strip() for cell in lines[index].strip().strip("|").split("|")])
                index += 1
            header = [Paragraph(clean(c), styles["BodyCustom"]) for c in [cell.strip() for cell in line.strip().strip("|").split("|")]]
            data = [header] + [[Paragraph(clean(cell), styles["BodyCustom"]) for cell in row] for row in raw_rows]
            widths = [6.8 * inch / len(header)] * len(header)
            table = Table(data, colWidths=widths, repeatRows=1, hAlign="LEFT")
            table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2f6f6d")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#b8ccc5")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 6), ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f2f7f4")]),
            ]))
            story.extend([table, Spacer(1, 8)])
            continue
        elif re.match(r"^(\d+\.|-) ", line):
            story.append(Paragraph(clean(line), styles["ListCustom"]))
        elif line.startswith("---"):
            story.append(Spacer(1, 4))
        else:
            style = styles["Caption"] if line.startswith("**Figure ") else styles["BodyCustom"]
            story.append(Paragraph(clean(line), style))
        index += 1

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(str(OUTPUT), pagesize=A4, leftMargin=0.72 * inch, rightMargin=0.72 * inch, topMargin=0.65 * inch, bottomMargin=0.72 * inch, title="Secure Password Manager")
    doc.build(story, onFirstPage=footer, onLaterPages=footer)
    shutil.rmtree(TEMP, ignore_errors=True)


if __name__ == "__main__":
    build()
