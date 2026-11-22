import os
import re
import json
from datetime import datetime
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from fpdf import FPDF


def _clean_md_inline(text: str) -> str:
    text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)
    text = re.sub(r"`(.*?)`", r"\1", text)
    return text.strip()


def build_reports(ticker: str, output_dir: str = "output") -> dict:
    t_clean = ticker.strip().upper()
    fact_path = os.path.join(output_dir, f"{t_clean}_fact_sheet.json")
    chart_path = os.path.join(output_dir, f"{t_clean}_chart.png")

    with open(fact_path, "r", encoding="utf-8") as f:
        fact = json.load(f)

    summary = fact.get("summary", {})
    company_name = summary.get("company_name", t_clean)
    as_of = summary.get("as_of_date", datetime.now().strftime("%Y-%m-%d"))
    date_compact = as_of.replace("-", "")

    sections = []
    for idx in range(1, 5):
        sec_path = os.path.join(output_dir, f"{t_clean}_0{idx}.md")
        if os.path.exists(sec_path):
            with open(sec_path, "r", encoding="utf-8") as f:
                sections.append(f.read())
        else:
            sections.append(f"# Section 0{idx} (미생성)\n해당 섹션 파일({sec_path})이 아직 작성되지 않았습니다.")

    full_md = "\n\n---\n\n".join(sections)

    docx_path = os.path.join(output_dir, f"{t_clean}_Research_Report_{date_compact}.docx")
    pdf_path = os.path.join(output_dir, f"{t_clean}_Research_Report_{date_compact}.pdf")

    _build_docx(docx_path, company_name, t_clean, as_of, summary, chart_path, full_md)
    _build_pdf(pdf_path, company_name, t_clean, as_of, chart_path, full_md)

    return {"docx": docx_path, "pdf": pdf_path}


def _build_docx(path: str, company_name: str, ticker: str, as_of: str, summary: dict, chart_path: str, full_md: str):
    doc = Document()
    style = doc.styles["Normal"]
    style.font.name = "Malgun Gothic"
    style.font.size = Pt(10)

    title = doc.add_heading(f"[Institutional Equity Research] {company_name} ({ticker})", level=0)
    title.runs[0].font.color.rgb = RGBColor(17, 24, 39)

    meta = doc.add_paragraph(
        f"데이터 기준일: {as_of}  |  현재가: {summary.get('current_price')} {summary.get('currency', '')}  |  "
        f"시가총액: {summary.get('market_cap')}"
    )
    meta.runs[0].bold = True

    if os.path.exists(chart_path):
        doc.add_picture(chart_path, width=Inches(6.2))

    lines = full_md.splitlines()
    table_buffer = []

    def flush_table(buf):
        if len(buf) < 2:
            for raw in buf:
                doc.add_paragraph(_clean_md_inline(raw))
            return
        rows_data = []
        for raw in buf:
            cells = [c.strip() for c in raw.strip().strip("|").split("|")]
            if all(set(c) <= set("-: ") for c in cells):
                continue
            rows_data.append(cells)
        if not rows_data:
            return
        cols = max(len(r) for r in rows_data)
        tbl = doc.add_table(rows=len(rows_data), cols=cols)
        tbl.style = "Light Grid Accent 1"
        for r_i, r_vals in enumerate(rows_data):
            for c_i in range(cols):
                val = _clean_md_inline(r_vals[c_i]) if c_i < len(r_vals) else ""
                cell_p = tbl.cell(r_i, c_i).paragraphs[0]
                run = cell_p.add_run(val)
                run.font.size = Pt(8.5)
                if r_i == 0:
                    run.bold = True

    for line in lines:
        s = line.strip()
        if s.startswith("|") and s.endswith("|"):
            table_buffer.append(s)
            continue
        elif table_buffer:
            flush_table(table_buffer)
            table_buffer = []

        if not s or s == "---":
            continue
        elif s.startswith("### "):
            doc.add_heading(_clean_md_inline(s[4:]), level=3)
        elif s.startswith("## "):
            doc.add_heading(_clean_md_inline(s[3:]), level=2)
        elif s.startswith("# "):
            doc.add_heading(_clean_md_inline(s[2:]), level=1)
        elif s.startswith(("- ", "* ")):
            p = doc.add_paragraph(style="List Bullet")
            p.add_run(_clean_md_inline(s[2:]))
        else:
            doc.add_paragraph(_clean_md_inline(s))

    if table_buffer:
        flush_table(table_buffer)

    doc.save(path)


def _build_pdf(path: str, company_name: str, ticker: str, as_of: str, chart_path: str, full_md: str):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # Load Korean font on Windows (fallback to built-in if non-Windows)
    font_candidates = [
        "C:/Windows/Fonts/malgun.ttf",
        "C:/Windows/Fonts/NanumGothic.ttf",
        "/usr/share/fonts/truetype/nanum/NanumGothic.ttf",
    ]
    font_family = "Helvetica"
    for fp in font_candidates:
        if os.path.exists(fp):
            pdf.add_font("KoreanFont", "", fp)
            font_family = "KoreanFont"
            break

    pdf.set_font(font_family, size=16)
    pdf.multi_cell(0, 9, f"[Equity Research] {company_name} ({ticker})")
    pdf.set_font(font_family, size=9)
    pdf.multi_cell(0, 6, f"Data As-Of: {as_of}")
    pdf.ln(3)

    if os.path.exists(chart_path):
        pdf.image(chart_path, w=180)
        pdf.ln(4)

    for line in full_md.splitlines():
        s = _clean_md_inline(line)
        if not s or s == "---":
            pdf.ln(2)
            continue
        if line.strip().startswith("# "):
            pdf.ln(3)
            pdf.set_font(font_family, size=13)
            pdf.multi_cell(0, 7, s.lstrip("# "))
            pdf.set_font(font_family, size=9.5)
        elif line.strip().startswith("## "):
            pdf.ln(2)
            pdf.set_font(font_family, size=11.5)
            pdf.multi_cell(0, 6.5, s.lstrip("# "))
            pdf.set_font(font_family, size=9.5)
        elif line.strip().startswith("### "):
            pdf.set_font(font_family, size=10.5)
            pdf.multi_cell(0, 6, s.lstrip("# "))
            pdf.set_font(font_family, size=9.5)
        else:
            pdf.set_font(font_family, size=9.5)
            pdf.multi_cell(0, 5.5, s)

    pdf.output(path)
