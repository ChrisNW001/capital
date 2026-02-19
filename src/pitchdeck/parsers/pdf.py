"""PDF document parser using pymupdf4llm."""

import os

import pymupdf4llm

from pitchdeck.models import DocumentParseError


def extract_pdf(path: str) -> str:
    """Extract PDF content as LLM-ready Markdown.

    Uses pymupdf4llm which preserves headings, tables, and lists
    in a format optimized for LLM consumption.
    """
    if not os.path.exists(path):
        raise DocumentParseError(path, "File not found")
    try:
        return pymupdf4llm.to_markdown(path)
    except Exception as e:
        raise DocumentParseError(path, str(e)) from e
