from PIL import Image
import pytesseract
import shutil
import os

# find the tesseract executable automatically and allows application to work on both(windows and linux)
def configure_tesseract():
    """
    Find the Tesseract executable in the current environment.

    Works both locally on Windows and on Linux deployment
    environments such as Render.
    """
    # First allow an explicit environment variable
    tesseract_path = os.getenv("TESSERACT_CMD")
    # Otherwise find Tesseract from PATH
    if not tesseract_path:
        tesseract_path = shutil.which("tesseract")
    if not tesseract_path:
        raise RuntimeError(
            "Tesseract OCR is not installed or is not available "
            "in the system PATH."
        )
    pytesseract.pytesseract.tesseract_cmd = tesseract_path

def extract_text_from_image(file):
    configure_tesseract()
    image = Image.open(file)
    text = pytesseract.image_to_string(
        image,
        lang="eng"
    )
    return text





# from PIL import Image
# import pytesseract


# pytesseract.pytesseract.tesseract_cmd = (
#     r"C:\Program Files\Tesseract-OCR\tesseract.exe"
# )


# def extract_text_from_image(file):

#     image = Image.open(file)

#     text = pytesseract.image_to_string(image)

#     return text
