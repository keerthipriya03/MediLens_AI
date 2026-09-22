import streamlit as st

from pdf_extractor import extract_text_from_pdf
from ocr import extract_text_from_image
from text_cleaner import clean_text

from ai.medical_ai import analyze_medical_report

st.title("MediExplain AI")

st.write(
    "Upload your medical report and get a simple explanation."
)

language = st.selectbox(
    "Select your language",
    ["English", "Telugu", "Hindi", "Tamil", "Kannada", "Malayalam"]
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
        if not extracted_text.strip():
            st.error(
                "No readable text could be extracted from this report."
            )
            st.stop()

        st.subheader("Extracted Text")

        st.text_area(
            "Report Content",
            extracted_text,
            height=300
        )

        st.subheader("AI Explanation")

        with st.spinner("Analyzing your medical report..."):
            try:
                result = analyze_medical_report(
                    extracted_text,
                    language
                )
            except ValueError as e:
                st.warning(str(e))
            except RuntimeError as e:
                st.error(str(e))
                st.stop()

        st.write(result["explanation"])

        st.warning(
            "Medical Disclaimer: MediExplain AI provides educational "
            "information to help users understand medical reports. "
            "It does not provide a diagnosis or replace advice from "
            "a qualified healthcare professional."
        )








