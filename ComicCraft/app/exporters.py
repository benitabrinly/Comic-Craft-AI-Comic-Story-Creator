"""PDF export with FPDF (fpdf2)."""
from datetime import datetime
from pathlib import Path

from fpdf import FPDF
from fpdf.enums import XPos, YPos

from . import config

_SWAPS = {"\u2018": "'", "\u2019": "'", "\u201c": '"', "\u201d": '"',
          "\u2013": "-", "\u2014": "-", "\u2026": "...", "\u00a0": " "}


def _clean(text: str) -> str:
    """The built-in PDF font only supports Latin-1, so swap/replace other characters."""
    for old, new in _SWAPS.items():
        text = text.replace(old, new)
    return text.encode("latin-1", "replace").decode("latin-1")


def _line(pdf: FPDF, height: float, text: str, align: str = "L"):
    pdf.multi_cell(0, height, _clean(text), align=align, new_x=XPos.LMARGIN, new_y=YPos.NEXT)


def save_pdf(layout, title: str = "My Comic") -> str:
    """Title page + one page per panel. Returns the saved file path."""
    pdf = FPDF(orientation="P", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=True, margin=15)

    pdf.add_page()
    pdf.set_y(100)
    pdf.set_font("Helvetica", "B", 26)
    _line(pdf, 14, title, "C")
    pdf.ln(6)
    pdf.set_font("Helvetica", "", 12)
    _line(pdf, 8, "Made with ComicCraft", "C")

    for panel in layout:
        pdf.add_page()
        pdf.set_font("Helvetica", "B", 16)
        _line(pdf, 10, f"Panel {panel['panel_number']}: {panel['title']}")
        pdf.ln(2)
        if Path(panel["image_path"]).is_file():
            y = pdf.get_y()
            pdf.image(panel["image_path"], x=30, y=y, w=150, h=150)
            pdf.set_y(y + 156)
        pdf.set_font("Helvetica", "", 12)
        _line(pdf, 7, panel["text"])

    path = config.EXPORTS_DIR / f"comic_{datetime.now():%Y%m%d_%H%M%S}.pdf"
    pdf.output(str(path))
    return str(path)
