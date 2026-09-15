import streamlit as st

from pdf_extractor import extract_text_from_pdf
from ocr import extract_text_from_image
from text_cleaner import clean_text

st.title("MediExplain AI")

st.write(
    "Upload your medical report and get a simple explanation."
)

language = st.selectbox(
    "Select your language",
    ["English", "Telugu"]
)

uploaded_file = st.file_uploader(
    "Upload your medical report",
    type=["pdf", "png", "jpg", "jpeg"]
)

if uploaded_file:

    st.success("File uploaded successfully!")

    if st.button("Analyze Report"):

        file_name = uploaded_file.name.lower()

        if file_name.endswith(".pdf"):

            extracted_text = extract_text_from_pdf(
                uploaded_file
            )

        else:

            extracted_text = extract_text_from_image(
                uploaded_file
            )

        # Clean the extracted text
        extracted_text = clean_text(extracted_text)

        st.subheader("Extracted Text")

        st.text_area(
            "Report Content",
            extracted_text,
            height=300
        )