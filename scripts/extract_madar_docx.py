from pathlib import Path
from docx import Document
from docx.text.paragraph import Paragraph
from docx.table import Table
from docx.oxml.text.paragraph import CT_P
from docx.oxml.table import CT_Tbl

ROOT = Path(".")
OUT = ROOT / "extracted"
OUT.mkdir(exist_ok=True)

SOURCES = [
    ("MADAR ERP  2.4.docx", "MADAR_ERP_2.4_FULL.txt"),
    ("MADAR ERP 2.5.docx", "MADAR_ERP_2.5_FULL.txt"),
]

def iter_blocks(parent):
    if hasattr(parent, "element"):
        element = parent.element.body
    else:
        element = parent
    for child in element.iterchildren():
        if isinstance(child, CT_P):
            yield Paragraph(child, parent)
        elif isinstance(child, CT_Tbl):
            yield Table(child, parent)

for source, target in SOURCES:
    path = ROOT / source
    if not path.exists():
        raise FileNotFoundError(f"Source document not found: {source}")
    doc = Document(path)
    lines = [f"SOURCE: {source}", f"PARAGRAPHS_AND_TABLES: {len(doc.paragraphs)} paragraphs; {len(doc.tables)} tables", ""]
    for block in iter_blocks(doc):
        if isinstance(block, Paragraph):
            value = block.text.strip()
            if value:
                lines.append(value)
        else:
            lines.append("[جدول]")
            for row in block.rows:
                cells = [" ".join(cell.text.split()) for cell in row.cells]
                lines.append(" | ".join(cells))
            lines.append("[نهاية الجدول]")
        lines.append("")
    content = "\n".join(lines).rstrip() + "\n"
    (OUT / target).write_text(content, encoding="utf-8")
    print(f"{source} -> {OUT / target}: {len(content)} characters")
