"""Document parsers for PDF and DOCX files."""

from pitchdeck.models import DocumentParseError


def extract_document(path: str) -> str:
    """Extract text from PDF or DOCX file."""
    if path.lower().endswith(".pdf"):
        from .pdf import extract_pdf

        return extract_pdf(path)
    elif path.lower().endswith((".docx", ".doc")):
        from .docx_parser import extract_docx

        return extract_docx(path)
    else:
        raise DocumentParseError(path, "Unsupported format. Use PDF or DOCX.")
