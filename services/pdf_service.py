import logging
import pdfplumber

logger = logging.getLogger(__name__)

def advanced_pdf_parse(filepath):
    """Extracts text and splits it into logical chunks for RAG."""
    full_text = ""
    chunks = []
    try:
        with pdfplumber.open(filepath) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if not text: continue
                full_text += text + "\n"
                page_chunks = [c.strip() for c in text.split('\n\n') if len(c) > 50]
                chunks.extend(page_chunks)
    except Exception as e:
        logger.error(f"PDF Error: {e}")
    return full_text, chunks
