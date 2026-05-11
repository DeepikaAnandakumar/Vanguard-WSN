"""
Extract plain text from a .docx file (WordprocessingML) without rewriting wording.

Usage (PowerShell):
  python .\extract_docx_text.py ".\final final final.docx" ".\case study\final final final.docx"

This writes sibling files:
  <input>.extracted.txt
"""

from __future__ import annotations

import sys
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path


W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
NS = {"w": W_NS}


def extract_docx_text(docx_path: Path) -> str:
    with zipfile.ZipFile(docx_path) as z:
        xml = z.read("word/document.xml")

    root = ET.fromstring(xml)
    out_paras: list[str] = []

    # Paragraphs, in document order
    for p in root.findall(".//w:body/w:p", NS):
        parts: list[str] = []
        for node in p.iter():
            if node.tag == f"{{{W_NS}}}t":
                parts.append(node.text or "")
            elif node.tag == f"{{{W_NS}}}tab":
                parts.append("\t")
            elif node.tag == f"{{{W_NS}}}br":
                parts.append("\n")
        out_paras.append("".join(parts))

    text = "\n\n".join(out_paras).strip() + "\n"
    return text


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print("Usage: python extract_docx_text.py <doc1.docx> [<doc2.docx> ...]")
        return 2

    for raw in argv[1:]:
        p = Path(raw)
        if not p.exists():
            print(f"MISSING: {p}")
            continue

        text = extract_docx_text(p)
        out = p.with_suffix(p.suffix + ".extracted.txt")
        out.write_text(text, encoding="utf-8")
        print(f"{p} -> {out} (chars={len(text)})")

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))


