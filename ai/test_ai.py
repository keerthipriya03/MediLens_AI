import os
from dotenv import load_dotenv
from google import genai


import json
from prompts import MEDICAL_EXTRACTION_PROMPT    #gets the prompts from prompts.py


load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY is not set")

client = genai.Client(api_key=api_key)


report_text = """
Hemoglobin: 10.2 g/dL (Reference range: 12-16 g/dL)
Creatinine: 1.1 mg/dL (Reference range: 0.6-1.2 mg/dL)
WBC: 12,500 /µL (Reference range: 4,000-11,000 /µL)
Platelets: 250,000 /µL (Reference range: 150,000-450,000 /µL)
"""

prompt = MEDICAL_EXTRACTION_PROMPT + "\n" + report_text


response = client.models.generate_content(
    model="gemini-3.7-flash",
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
