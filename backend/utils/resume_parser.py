import pdfplumber
import docx
import logging

logger = logging.getLogger(__name__)


def extract_text_from_pdf(file_path):
    logger.info("Extracting text from PDF: %s", file_path)
    text = ""
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            logger.debug("Extracting page: %s", page.page_number)
            text += page.extract_text() or ""
    return text.strip()


def extract_text_from_docx(file_path):
    logger.info("Extracting text from Docx: %s", file_path)
    doc = docx.Document(file_path)
    return "\n".join([para.text for para in doc.paragraphs])
