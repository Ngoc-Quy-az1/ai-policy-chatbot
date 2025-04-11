import pdfplumber
import docx

def extract_from_pdf(path):
    with pdfplumber.open(path) as pdf:
        return "\n".join([page.extract_text() for page in pdf.pages])

def extract_from_docx(path):
    doc = docx.Document(path)
    return "\n".join([para.text for para in doc.paragraphs])
