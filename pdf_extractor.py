import fitz
from PIL import Image
import pytesseract
import io


def extract_text_from_pdf(file):

    pdf = fitz.open(stream=file.read(), filetype="pdf")

    text = ""

    # First try normal PDF text extraction
    for page in pdf:
        text += page.get_text()

    # If text was found, return it
    if text.strip():
        pdf.close()
        return text

    # If no text was found, use OCR
    text = ""

    for page in pdf:

        # Convert PDF page to image
        pix = page.get_pixmap()

        image_bytes = pix.tobytes("png")

        image = Image.open(
            io.BytesIO(image_bytes)
        )

        # OCR
        page_text = pytesseract.image_to_string(
            image
        )

        text += page_text + "\n"

    pdf.close()

    return text