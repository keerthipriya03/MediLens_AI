import os
import json

import time

from dotenv import load_dotenv
from google import genai

from ai.prompts import (
    MEDICAL_EXTRACTION_PROMPT,
    MEDICAL_EXPLANATION_PROMPT,
    TRANSLATION_PROMPT
)

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY is not set")
client = genai.Client(api_key=api_key)


def generate_ai_response(prompt):

    for attempt in range(3):

        try:

            response = client.models.generate_content(
                model="gemini-3.5-flash",
                contents=prompt
            )

            return response.text

        except Exception as e:

            if attempt < 2:
                time.sleep(2)
            else:
                raise RuntimeError(
                    "AI service is temporarily unavailable. "
                    "Please try again in a few moments."
                ) from e



def extract_medical_tests(report_text):
    prompt = MEDICAL_EXTRACTION_PROMPT + "\n" + report_text
    # response = client.models.generate_content(
    #     model="gemini-3.5-flash",
    #     contents=prompt
    # )

    response = generate_ai_response(prompt)

    # result = response.text
    try:
        medical_data = json.loads(result)
        return medical_data
    except json.JSONDecodeError:
        raise ValueError(
            "Gemini returned an invalid JSON response."
        )


def generate_explanations(medical_data):
    tests_info = ""
    for test in medical_data["tests"]:
        tests_info += f"""
Test name: {test["name"]}
Value: {test["value"]}
Unit: {test["unit"]}
Reference range: {test["reference_range"]}
"""

    explanation_prompt = MEDICAL_EXPLANATION_PROMPT + f"""
Explain ALL of the following tests:
{tests_info}

Return a separate explanation for each test.
Clearly mention the test name before each explanation.
"""

    # response = client.models.generate_content(
    #     model="gemini-3.5-flash",
    #     contents=explanation_prompt
    # )
    # return response.text


    return generate_ai_response(explanation_prompt)


def translate_explanations(explanation_text, language):
    translation_prompt = TRANSLATION_PROMPT.format(
        language=language
    ) + "\n" + explanation_text
    # response = client.models.generate_content(
    #     model="gemini-3.5-flash",
    #     contents=translation_prompt
    # )
    # return response.text


    return generate_ai_response(translation_prompt)


def analyze_medical_report(report_text, language):

    # Step 1: Extract medical tests
    medical_data = extract_medical_tests(report_text)

    # Step 2: Generate English explanations
    explanation_text = generate_explanations(medical_data)

    # Step 3: Translate if a language other than English is selected
    if language == "English":
        final_explanation = explanation_text
    else:
        final_explanation = translate_explanations(
            explanation_text,
            language
        )

    return {
        "medical_data": medical_data,
        "explanation": final_explanation
    }











# app.py      ↓   pdf_extractor.py / ocr.py    ↓  text_cleaner.py    ↓     medical_ai.py       ← YOUR AI PIPELINE     ↓    Gemini     ↓    results    ↓     app.py   ↓    Streamlit UI