# Gemini/API testing + running the pipeline.
import os
from dotenv import load_dotenv
from google import genai


import json
from prompts import MEDICAL_EXTRACTION_PROMPT, MEDICAL_EXPLANATION_PROMPT    #gets the prompts from prompts.py
    

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY is not set")

client = genai.Client(api_key=api_key)


# temporarily added to see exactly which models API key can use
# print("Available models:")
# for model in client.models.list():
#     print(model.name)


report_text = """
Hemoglobin: 10.2 g/dL (Reference range: 12-16 g/dL)
Creatinine: 1.1 mg/dL (Reference range: 0.6-1.2 mg/dL)
WBC: 12,500 /µL (Reference range: 4,000-11,000 /µL)
Platelets: 250,000 /µL (Reference range: 150,000-450,000 /µL)
"""

prompt = MEDICAL_EXTRACTION_PROMPT + "\n" + report_text


response = client.models.generate_content(
    model="gemini-3.5-flash",
    contents=prompt
)

# print(response.text)



result = response.text
try:
    medical_data = json.loads(result)
    print("\nExtracted medical Data:")
    print(medical_data)
except json.JSONDecodeError:
    print("Failed to parse JSON. Response text:")
    print(result)



# Generate explanation for the first test
# test = medical_data["tests"][0]           #explains only for 1
# ## extracting the tests
# for test in medical_data["tests"]:

#     test_info = f"""
#     Test name: {test["name"]}
#     Value: {test["value"]}
#     Unit: {test["unit"]}
#     Reference range: {test["reference_range"]}
#     """

#     explanation_prompt = MEDICAL_EXPLANATION_PROMPT + "\n" + test_info

#     explanation_response = client.models.generate_content(
#         model="gemini-3.7-flash",
#         contents=explanation_prompt
#     )

#     # print("\nSimple Medical Explanation:")
#     print("\n" + "=" * 50)
#     print(f"Test: {test['name']}")
#     print("=" * 50)
#     print(explanation_response.text)

#explain all tests
# Generate explanations for all extracted tests in one Gemini request

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

explanation_response = client.models.generate_content(
    model="gemini-3.5-flash",
    contents=explanation_prompt
)

print("\n" + "=" * 60)
print("SIMPLE MEDICAL EXPLANATIONS")
print("=" * 60)

print(explanation_response.text)