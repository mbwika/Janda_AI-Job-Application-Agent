import pdfplumber
import docx

def extract_text_from_pdf(file_path):
    print("Extracting text from PDF:", file_path)
    text = ""
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            print("Extracting page:", page.page_number)
            text += page.extract_text() or ""
    return text.strip()

def extract_text_from_docx(file_path):
    print("Extracting text from Docx:", file_path)
    doc = docx.Document(file_path)
    return "\n".join([para.text for para in doc.paragraphs])
