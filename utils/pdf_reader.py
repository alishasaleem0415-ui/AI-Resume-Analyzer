import fitz  # PyMuPDF
import os

def extract_text_from_pdf(uploaded_file):
    """Extract text from a Streamlit uploaded PDF file object."""
    text = ""
    try:
        with fitz.open(stream=uploaded_file.read(), filetype="pdf") as doc:
            for page in doc:
                text += page.get_text()
    except Exception as e:
        return f"Error reading PDF: {str(e)}"
    return text


def extract_text_from_pdf_path(pdf_path):
    """Extract text from a PDF file on disk (used for dataset PDFs)."""
    text = ""
    try:
        with fitz.open(pdf_path) as doc:
            for page in doc:
                text += page.get_text()
    except Exception as e:
        return ""
    return text.strip()
