import os
import json
import time

from dotenv import load_dotenv
from google import genai

from ai.prompts import (
    MEDICAL_EXTRACTION_PROMPT,
    MEDICAL_EXPLANATION_PROMPT,
    TRANSLATION_PROMPT,
)

# Environment / Gemini client

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError(
        "GEMINI_API_KEY is not set. "
        "Please add GEMINI_API_KEY to your .env file."
    )

client = genai.Client(api_key=api_key)

# Use the Gemini model available to your API account.
MODEL_NAME = "gemini-3.5-flash"


# Gemini helper

# def generate_ai_response(prompt):
#     """
#     Send a prompt to Gemini and return the generated text.
#     Retries up to 3 times if the API request fails.
#     """
#     last_error = None
#     for attempt in range(3):
#         try:
#             response = client.models.generate_content(
#                 model=MODEL_NAME,
#                 contents=prompt,
#             )
#             if response is None:
#                 raise RuntimeError("Gemini returned no response.")
#             text = getattr(response, "text", None)
#             if not text:
#                 raise RuntimeError(
#                     "Gemini returned an empty response."
#                 )
#             return text.strip()
#         except Exception as e:
#             last_error = e
#             if attempt < 2:
#                 time.sleep(2)
#     raise RuntimeError(
#         "AI service is temporarily unavailable. "
#         "Please try again in a few moments."
#     ) from last_error
def generate_ai_response(prompt):

    last_error = None

    for attempt in range(3):
        try:
            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=prompt
            )

            if response is None:
                raise RuntimeError("Gemini returned no response.")

            text = getattr(response, "text", None)

            if not text:
                raise RuntimeError("Gemini returned an empty response.")

            return text.strip()

        except Exception as e:
            last_error = e

            error_text = str(e).lower()

            # Token / context limit
            if (
                "token" in error_text
                or "context length" in error_text
                or "maximum" in error_text
                or "too many tokens" in error_text
            ):
                raise ValueError(
                    "The uploaded report is too large to analyze at once. "
                    "Please upload a shorter report or split the report into smaller parts."
                ) from None

            # Other API errors
            if attempt < 2:
                time.sleep(2)
            else:
                raise RuntimeError(
                    "AI service is temporarily unavailable. "
                    "Please try again in a few moments."
                ) from last_error



# JSON cleanup

def clean_json_response(result):
    """
    Gemini may sometimes return JSON inside Markdown
    code fences. This function removes those fences.
    """

    if not result:
        raise ValueError("Gemini returned an empty response.")

    result = result.strip()

    # Remove ```json ... ```
    if result.startswith("```"):
        lines = result.splitlines()

        # Remove first line: ```json or ```
        if lines:
            lines = lines[1:]

        # Remove final ```
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]

        result = "\n".join(lines).strip()

    return result


# Step 1: Extract medical tests

def extract_medical_tests(report_text):

    if not report_text or not report_text.strip():
        raise ValueError(
            "No medical report text was extracted from the file."
        )

    prompt = (
        MEDICAL_EXTRACTION_PROMPT
        + "\n\nMEDICAL REPORT:\n"
        + report_text
    )

    # IMPORTANT:
    # The Gemini response is stored in `result`.
    result = generate_ai_response(prompt)

    result = clean_json_response(result)

    try:
        medical_data = json.loads(result)

    except json.JSONDecodeError as e:
        raise ValueError(
            "Gemini returned an invalid JSON response.\n\n"
            f"Gemini response:\n{result}"
        ) from e

    # Basic validation
    if not isinstance(medical_data, dict):
        raise ValueError(
            "Medical extraction result must be a JSON object."
        )

    if "tests" not in medical_data:
        raise ValueError(
            "Gemini response does not contain a 'tests' field."
        )

    if not isinstance(medical_data["tests"], list):
        raise ValueError(
            "'tests' must be a list."
        )

    return medical_data


# Step 2: Generate English explanations

def generate_explanations(medical_data):

    tests = medical_data.get("tests", [])

    if not tests:
        return (
            "No medical test results could be identified "
            "in the uploaded report."
        )

    tests_info = []

    for test in tests:

        name = test.get("name", "Unknown test")
        value = test.get("value", "Not available")
        unit = test.get("unit", "Not available")
        reference_range = test.get(
            "reference_range",
            "Not available"
        )

        tests_info.append(
            f"""
Test name: {name}
Value: {value}
Unit: {unit}
Reference range: {reference_range}
"""
        )

    tests_info_text = "\n".join(tests_info)

    explanation_prompt = (
        MEDICAL_EXPLANATION_PROMPT
        + "\n\n"
        + "Explain ALL of the following medical tests:\n"
        + tests_info_text
        + """

IMPORTANT:
- Return a separate explanation for every test.
- Clearly mention the test name.
- Explain what the test measures.
- Explain why the test is performed.
- Explain what the reported value means in simple language.
- Explain the unit in simple language when useful.
- Use the reference range provided in the report when discussing whether
  a value is outside that range.
- Do not diagnose the patient.
- Do not recommend medication or treatment.
- If information is insufficient, clearly say so.
"""
    )

    return generate_ai_response(explanation_prompt)


# Step 3: Translate

def translate_explanations(explanation_text, language):

    if not explanation_text:
        return ""

    if not language:
        language = "English"

    translation_prompt = (
        TRANSLATION_PROMPT.format(
            language=language
        )
        + "\n\nTEXT TO TRANSLATE:\n"
        + explanation_text
    )

    return generate_ai_response(translation_prompt)


# Complete medical report analysis

def analyze_medical_report(report_text, language):

    if not report_text or not report_text.strip():
        raise ValueError(
            "The uploaded report does not contain readable text."
        )

    # Step 1
    medical_data = extract_medical_tests(report_text)

    # Step 2
    explanation_text = generate_explanations(
        medical_data
    )

    # Step 3
    if language and language.strip().lower() == "english":

        final_explanation = explanation_text

    else:

        final_explanation = translate_explanations(
            explanation_text,
            language
        )

    return {
        "medical_data": medical_data,
        "explanation": final_explanation,
    }






















# import os
# import json

# import time

# from dotenv import load_dotenv
# from google import genai

# from ai.prompts import (
#     MEDICAL_EXTRACTION_PROMPT,
#     MEDICAL_EXPLANATION_PROMPT,
#     TRANSLATION_PROMPT
# )

# load_dotenv()

# api_key = os.getenv("GEMINI_API_KEY")
# if not api_key:
#     raise ValueError("GEMINI_API_KEY is not set")
# client = genai.Client(api_key=api_key)


# def generate_ai_response(prompt):

#     for attempt in range(3):

#         try:

#             response = client.models.generate_content(
#                 model="gemini-3.5-flash",
#                 contents=prompt
#             )

#             return response.text

#         except Exception as e:

#             if attempt < 2:
#                 time.sleep(2)
#             else:
#                 raise RuntimeError(
#                     "AI service is temporarily unavailable. "
#                     "Please try again in a few moments."
#                 ) from e



# def extract_medical_tests(report_text):
#     prompt = MEDICAL_EXTRACTION_PROMPT + "\n" + report_text
#     # response = client.models.generate_content(
#     #     model="gemini-3.5-flash",
#     #     contents=prompt
#     # )

#     # response = generate_ai_response(prompt)

#     # result = response.text
#     result = generate_ai_response(prompt)
#     try:
#         medical_data = json.loads(result)
#         return medical_data
#     except json.JSONDecodeError:
#         raise ValueError(
#             "Gemini returned an invalid JSON response."
#         )


# def generate_explanations(medical_data):
#     tests_info = ""
#     for test in medical_data["tests"]:
#         tests_info += f"""
# Test name: {test["name"]}
# Value: {test["value"]}
# Unit: {test["unit"]}
# Reference range: {test["reference_range"]}
# """

#     explanation_prompt = MEDICAL_EXPLANATION_PROMPT + f"""
# Explain ALL of the following tests:
# {tests_info}

# Return a separate explanation for each test.
# Clearly mention the test name before each explanation.
# """

#     # response = client.models.generate_content(
#     #     model="gemini-3.5-flash",
#     #     contents=explanation_prompt
#     # )
#     # return response.text


#     return generate_ai_response(explanation_prompt)


# def translate_explanations(explanation_text, language):
#     translation_prompt = TRANSLATION_PROMPT.format(
#         language=language
#     ) + "\n" + explanation_text
#     # response = client.models.generate_content(
#     #     model="gemini-3.5-flash",
#     #     contents=translation_prompt
#     # )
#     # return response.text


#     return generate_ai_response(translation_prompt)


# def analyze_medical_report(report_text, language):

#     # Step 1: Extract medical tests
#     medical_data = extract_medical_tests(report_text)

#     # Step 2: Generate English explanations
#     explanation_text = generate_explanations(medical_data)

#     # Step 3: Translate if a language other than English is selected
#     if language == "English":
#         final_explanation = explanation_text
#     else:
#         final_explanation = translate_explanations(
#             explanation_text,
#             language
#         )

#     return {
#         "medical_data": medical_data,
#         "explanation": final_explanation
#     }











# # app.py      ↓   pdf_extractor.py / ocr.py    ↓  text_cleaner.py    ↓     medical_ai.py       ← YOUR AI PIPELINE     ↓    Gemini     ↓    results    ↓     app.py   ↓    Streamlit UI
