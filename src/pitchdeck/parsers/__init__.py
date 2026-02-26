"""Document parsers for PDF and DOCX files."""

from pitchdeck.models import DocumentParseError


def extract_document(path: str) -> str:
    """Extract text from PDF, DOCX, Markdown, or plain text file."""
    if path.lower().endswith(".pdf"):
        from .pdf import extract_pdf

        return extract_pdf(path)
    elif path.lower().endswith((".docx", ".doc")):
        from .docx_parser import extract_docx

        return extract_docx(path)
    elif path.lower().endswith((".md", ".txt")):
        with open(path, encoding="utf-8") as f:
            return f.read()
    else:
        raise DocumentParseError(path, "Unsupported format. Use PDF, DOCX, MD, or TXT.")
