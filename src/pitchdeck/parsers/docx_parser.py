"""DOCX document parser using python-docx."""

import os

from docx import Document

from pitchdeck.models import DocumentParseError


def extract_docx(path: str) -> str:
    """Extract DOCX content as Markdown-formatted text.

    Preserves heading hierarchy and paragraph structure.
    """
    if not os.path.exists(path):
        raise DocumentParseError(path, "File not found")
    try:
        doc = Document(path)
    except Exception as e:
        raise DocumentParseError(path, str(e)) from e

    sections = []
    for para in doc.paragraphs:
        style = para.style.name
        text = para.text.strip()
        if not text:
            continue
        if style.startswith("Heading"):
            level_str = style.split()[-1]
            try:
                level = int(level_str)
            except ValueError:
                level = 2
            sections.append(f"{'#' * level} {text}")
        else:
            sections.append(text)

    return "\n\n".join(sections)
