import json
import requests
import re
from dotenv import load_dotenv
import os

# Load the API endpoints
with open('get_api_endpoints.json', 'r') as file:
    api_endpoints = json.load(file)

valid_urls = set(api_endpoints.values())

OLLAMA_API_URL = "http://localhost:11434/api/generate"

BEARER_TOKEN = os.getenv("API_BEARER_TOKEN")

def get_best_api_endpoint_with_ollama(prompt, current_url):
    # The regex assumes the ID is a numeric value
    id_match = re.search(r'(\d+)', current_url)
    if id_match:
        extracted_id = id_match.group(1)
    else:
        extracted_id = None

    print(f"Extracted ID: {extracted_id}")
    
    ollama_prompt = (
        f"Based on the user's input: '{prompt}', "
        f"identify the relevant API endpoint and incorporate the extracted ID '{extracted_id}' "
        f"into the API call if needed. "
        f"The output should only contain the URL with the appropriate ID substituted. "
        f"If the prompt is a generic response use the Get Listing Data by ID endpoint.\n"
    )

    for name, url in api_endpoints.items():
        ollama_prompt += f"- {name}: {url}\n"

    data = {
        "model": "llama3.2:3b",
        "prompt": ollama_prompt
    }
    
    response = requests.post(OLLAMA_API_URL, json=data, headers={"Content-Type": "application/json"}, stream=True)
    
    if response.status_code == 200:
        endpoint_output = ""
        for line in response.iter_lines():
            if line:
                part = json.loads(line)
                endpoint_output += part.get("response", "")

        cleaned_output = endpoint_output.strip()
        url_match = re.search(r'(https?://[^\s]+)', cleaned_output)
        if url_match:
            selected_url = url_match.group(0)
            if extracted_id and selected_url != "NONE":
                selected_url = selected_url.replace("{id}", extracted_id)
                return selected_url
            else:
                return "NONE"
        else:
            return "NONE"
    else:
        return f"Failed to retrieve data from Ollama. Status code: {response.status_code}"

def determine_api_url(prompt, current_url):
    return get_best_api_endpoint_with_ollama(prompt, current_url)

# # Test example
# prompt = "Get detailed information about the property."
# current_url = "https://krishnam-uat.tlcengine.com/propertydetail/6570389/100-John-T-O-Leary-Boulevard-#225_South-Amboy_NJ_08879"

# selected_url = determine_api_url(prompt, current_url)
# print("Selected API URL:", selected_url)

# # Fetch the property data with a GET request using bearer token authentication
# if selected_url != "NONE":
#     headers = {
#         "Authorization": f"Bearer {BEARER_TOKEN}"
#     }
#     property_response = requests.get(selected_url, headers=headers)
#     if property_response.status_code == 200:
#         property_data = property_response.json()
#         print("Property data:", property_data)
#     else:
#         print(f"Failed to retrieve property data. Status code: {property_response.status_code}")
# else:
#     print("No valid API URL selected.")
