#!/usr/bin/env python3
"""办公桥 —— 文档/表格/幻灯片/PDF 的本地处理服务，全部开源库实现。
默认 127.0.0.1:8091。LibreOffice 装了就能做格式互转，没装只影响 /convert。
"""
import os, shutil, subprocess, sys, tempfile, uuid
from pathlib import Path
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Any
import uvicorn

app = FastAPI(title="办公桥", version="1.0.0")

CJK_FONTS = ["/Library/Fonts/Arial Unicode.ttf",
             "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
             "/System/Library/Fonts/Hiragino Sans GB.ttc",
             "C:/Windows/Fonts/msyh.ttf", "C:/Windows/Fonts/simhei.ttf"]


def out_path(out, default):
    o = out or default
    Path(os.path.dirname(os.path.abspath(o)) or ".").mkdir(parents=True, exist_ok=True)
    return o


def soffice():
    for c in ["/Applications/LibreOffice.app/Contents/MacOS/soffice",
              os.path.expanduser("~/Applications/LibreOffice.app/Contents/MacOS/soffice"),
              "C:/Program Files/LibreOffice/program/soffice.exe",
              "C:/Program Files (x86)/LibreOffice/program/soffice.exe"]:
        if os.path.exists(c):
            return c
    return shutil.which("soffice")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/capabilities")
def capabilities():
    mods = {}
    for name in ["docx", "openpyxl", "pptx", "pypdf", "fpdf"]:
        try:
            __import__(name)
            mods[name] = True
        except Exception:
            mods[name] = False
    return {"docx": mods["docx"], "xlsx": mods["openpyxl"], "pptx": mods["pptx"],
            "pdf_read": mods["pypdf"], "pdf_write": mods["fpdf"],
            "convert": {"engine": "LibreOffice", "ok": bool(soffice()), "path": soffice()}}


# ---------- Word ----------
class Para(BaseModel):
    text: str = ""
    style: Optional[str] = None
    level: Optional[int] = None
    bold: bool = False


class DocxIn(BaseModel):
    title: Optional[str] = None
    paragraphs: List[Para] = []
    table: Optional[Any] = None
    out: Optional[str] = None


@app.post("/docx/create")
def docx_create(b: DocxIn):
    import docx
    from docx.shared import Pt
    d = docx.Document()
    if b.title:
        h = d.add_heading(b.title, level=0)
        for r in h.runs:
            r.font.size = Pt(22)
    for p in b.paragraphs:
        if p.level:
            d.add_heading(p.text, level=min(max(p.level, 1), 9))
        else:
            par = d.add_paragraph()
            run = par.add_run(p.text)
            run.bold = p.bold
    if b.table and isinstance(b.table, dict):
        rows = b.table.get("rows") or []
        if rows:
            t = d.add_table(rows=len(rows), cols=len(rows[0]))
            t.style = "Table Grid"
            for i, row in enumerate(rows):
                for j, cell in enumerate(row):
                    t.cell(i, j).text = str(cell)
    o = out_path(b.out, os.path.join(tempfile.gettempdir(), "doc_" + uuid.uuid4().hex[:8] + ".docx"))
    d.save(o)
    return {"out": o, "bytes": os.path.getsize(o), "paragraphs": len(d.paragraphs)}


class PathIn(BaseModel):
    path: str
    out: Optional[str] = None


@app.post("/docx/extract")
def docx_extract(b: PathIn):
    import docx
    d = docx.Document(b.path)
    paras = [{"text": p.text, "style": p.style.name} for p in d.paragraphs if p.text.strip()]
    tables = []
    for t in d.tables:
        tables.append([[c.text for c in row.cells] for row in t.rows])
    return {"paragraphs": paras, "tables": tables,
            "text": "\n".join(p["text"] for p in paras)}


# ---------- Excel ----------
class Sheet(BaseModel):
    name: str = "Sheet1"
    rows: List[List[Any]] = []
    width: Optional[List[int]] = None


class XlsxIn(BaseModel):
    sheets: List[Sheet] = []
    out: Optional[str] = None


@app.post("/xlsx/create")
def xlsx_create(b: XlsxIn):
    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill, Alignment
    wb = Workbook()
    wb.remove(wb.active)
    for s in b.sheets or [Sheet(name="Sheet1", rows=[[""]] )]:
        ws = wb.create_sheet(s.name or "Sheet")
        for row in s.rows:
            ws.append(row)
        if s.rows:
            for c in ws[1]:
                c.font = Font(bold=True)
                c.fill = PatternFill("solid", fgColor="EEEEEE")
                c.alignment = Alignment(horizontal="center")
            ws.freeze_panes = "A2"
        if s.width:
            from openpyxl.utils import get_column_letter
            for i, w in enumerate(s.width, 1):
                ws.column_dimensions[get_column_letter(i)].width = w
        else:
            from openpyxl.utils import get_column_letter
            for i, col in enumerate(zip(*s.rows) if s.rows else [], 1):
                ln = max((len(str(v)) for v in col if v is not None), default=8)
                ws.column_dimensions[get_column_letter(i)].width = min(max(ln + 2, 8), 60)
    o = out_path(b.out, os.path.join(tempfile.gettempdir(), "book_" + uuid.uuid4().hex[:8] + ".xlsx"))
    wb.save(o)
    return {"out": o, "bytes": os.path.getsize(o), "sheets": len(wb.sheetnames)}


@app.post("/xlsx/extract")
def xlsx_extract(b: PathIn):
    from openpyxl import load_workbook
    wb = load_workbook(b.path, data_only=True)
    out = {}
    for name in wb.sheetnames:
        ws = wb[name]
        out[name] = [[c for c in row] for row in ws.iter_rows(values_only=True)]
    return {"sheets": out, "names": wb.sheetnames}


# ---------- PPT ----------
class Slide(BaseModel):
    title: str = ""
    bullets: List[str] = []
    notes: Optional[str] = None
    image: Optional[str] = None


class PptxIn(BaseModel):
    slides: List[Slide] = []
    out: Optional[str] = None
    title: Optional[str] = None


@app.post("/pptx/create")
def pptx_create(b: PptxIn):
    from pptx import Presentation
    from pptx.util import Inches, Pt
    prs = Presentation()
    if b.title:
        s = prs.slides.add_slide(prs.slide_layouts[0])
        s.shapes.title.text = b.title
    for item in b.slides:
        layout = prs.slide_layouts[1]
        s = prs.slides.add_slide(layout)
        s.shapes.title.text = item.title
        body = s.placeholders[1].text_frame
        body.clear()
        for i, line in enumerate(item.bullets):
            p = body.paragraphs[0] if i == 0 else body.add_paragraph()
            p.text = line
            p.font.size = Pt(18)
        if item.notes:
            s.notes_slide.notes_text_frame.text = item.notes
        if item.image and os.path.exists(item.image):
            s.shapes.add_picture(item.image, Inches(6.2), Inches(1.8), width=Inches(3.2))
    o = out_path(b.out, os.path.join(tempfile.gettempdir(), "deck_" + uuid.uuid4().hex[:8] + ".pptx"))
    prs.save(o)
    return {"out": o, "bytes": os.path.getsize(o), "slides": len(prs.slides)}


@app.post("/pptx/extract")
def pptx_extract(b: PathIn):
    from pptx import Presentation
    prs = Presentation(b.path)
    out = []
    for i, s in enumerate(prs.slides, 1):
        texts = []
        for sh in s.shapes:
            if sh.has_text_frame and sh.text_frame.text.strip():
                texts.append(sh.text_frame.text)
        out.append({"slide": i, "text": "\n".join(texts)})
    return {"slides": out, "count": len(out)}


# ---------- PDF ----------
class PdfCreate(BaseModel):
    title: Optional[str] = None
    paragraphs: List[str] = []
    out: Optional[str] = None


def cjk_font():
    for f in CJK_FONTS:
        if os.path.exists(f):
            return f
    return None


@app.post("/pdf/create")
def pdf_create(b: PdfCreate):
    from fpdf import FPDF
    pdf = FPDF()
    pdf.add_page()
    font = cjk_font()
    cjk = False
    if font:
        try:
            pdf.add_font("cjk", "", font)
            pdf.set_font("cjk", size=12)
            cjk = True
        except Exception:
            cjk = False
    if not cjk:
        pdf.set_font("Helvetica", size=12)
    if b.title:
        pdf.set_font_size(18)
        pdf.multi_cell(0, 10, b.title.encode("latin-1", "replace").decode("latin-1") if not cjk else b.title)
        pdf.ln(4)
    pdf.set_font_size(12)
    for p in b.paragraphs:
        txt = p if cjk else p.encode("latin-1", "replace").decode("latin-1")
        pdf.multi_cell(0, 8, txt)
        pdf.ln(2)
    o = out_path(b.out, os.path.join(tempfile.gettempdir(), "pdf_" + uuid.uuid4().hex[:8] + ".pdf"))
    pdf.output(o)
    return {"out": o, "bytes": os.path.getsize(o), "cjk": cjk}


class PdfExtract(PathIn):
    pages: Optional[List[int]] = None


@app.post("/pdf/extract")
def pdf_extract(b: PdfExtract):
    from pypdf import PdfReader
    r = PdfReader(b.path)
    idx = b.pages or range(len(r.pages))
    texts = []
    for i in idx:
        try:
            texts.append(r.pages[i].extract_text() or "")
        except Exception:
            texts.append("")
    return {"pages": len(r.pages), "read": len(texts), "text": "\n\n".join(texts)}


class PdfMerge(BaseModel):
    paths: List[str]
    out: Optional[str] = None


@app.post("/pdf/merge")
def pdf_merge(b: PdfMerge):
    from pypdf import PdfWriter
    w = PdfWriter()
    for p in b.paths:
        w.append(p)
    o = out_path(b.out, os.path.join(tempfile.gettempdir(), "merged_" + uuid.uuid4().hex[:8] + ".pdf"))
    with open(o, "wb") as f:
        w.write(f)
    return {"out": o, "bytes": os.path.getsize(o), "sources": len(b.paths)}


# ---------- 格式互转 ----------
class ConvertIn(BaseModel):
    path: str
    to: str = "pdf"
    out: Optional[str] = None


@app.post("/convert")
def convert(b: ConvertIn):
    so = soffice()
    if not so:
        raise HTTPException(501, "LibreOffice 未安装，/convert 不可用。装 LibreOffice（MPL-2.0）后自动生效。")
    outdir = os.path.dirname(os.path.abspath(b.out or tempfile.gettempdir()))
    Path(outdir).mkdir(parents=True, exist_ok=True)
    r = subprocess.run([so, "--headless", "--convert-to", b.to, "--outdir", outdir, b.path],
                       capture_output=True, text=True, timeout=600)
    stem = Path(b.path).stem
    cand = os.path.join(outdir, stem + "." + b.to)
    if not os.path.exists(cand):
        raise HTTPException(500, (r.stderr or r.stdout or "转换失败")[-500:])
    if b.out and os.path.abspath(b.out) != os.path.abspath(cand):
        Path(os.path.dirname(os.path.abspath(b.out))).mkdir(parents=True, exist_ok=True)
        shutil.move(cand, b.out)
        cand = b.out
    return {"out": cand, "bytes": os.path.getsize(cand)}


if __name__ == "__main__":
    port = int(os.environ.get("OB_PORT", "8091"))
    print("办公桥 -> http://127.0.0.1:" + str(port))
    for k, v in capabilities().items():
        print("  %-10s %s" % (k, v if not isinstance(v, dict) else ("OK" if v.get("ok") else "未安装")))
    uvicorn.run(app, host="127.0.0.1", port=port, log_level="warning")