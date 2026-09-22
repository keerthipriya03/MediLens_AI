import fitz
from PIL import Image
import pytesseract
import io
import shutil
import os


def configure_tesseract():
    """
    Find the Tesseract executable in the current environment.

    Works on both Windows and Linux/Render.
    """
    # Allow an explicit path through an environment variable
    tesseract_path = os.getenv("TESSERACT_CMD")
    # Otherwise search the system PATH
    if not tesseract_path:
        tesseract_path = shutil.which("tesseract")
    if not tesseract_path:
        raise RuntimeError(
            "Tesseract OCR is not installed or is not available "
            "in the system PATH."
        )
    pytesseract.pytesseract.tesseract_cmd = tesseract_path


def extract_text_from_pdf(file):

    configure_tesseract()
    pdf = fitz.open(stream=file.read(), filetype="pdf")
    text = ""

    # First try normal PDF text extraction
    for page in pdf:
        pg_txt = page.get_text()
        if pg_txt:
            text += pg_txt + "\n"

    # If text was found, return it
    if text.strip():
        pdf.close()
        return text

    # If no text was found, use OCR
    text = ""
    for page in pdf:
        # Convert PDF page to image
        pix = page.get_pixmap(
            matrix=fitz.Matrix(2,2),
            alpha=False
        )
        image_bytes = pix.tobytes("png")
        image = Image.open(
            io.BytesIO(image_bytes)
        )
        # OCR
        page_text = pytesseract.image_to_string(
            image, lang="eng"
        )
        text += page_text + "\n"

    pdf.close()
    return text

    return text
