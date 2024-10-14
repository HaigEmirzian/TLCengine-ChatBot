from flask import Flask, request, jsonify
import requests
import os
import re

app = Flask(__name__)

PROPERTY_API_URL = "???"
OLLAMA_API_URL = "http://localhost:11434/api/generate"

@app.route('/propertydetails', methods=['POST'])
def property_details():
    current_url = request.json.get('url', '')
    
    match = re.search(r'/propertydetail/(\d+)/', current_url)
    
    if not match:
        return jsonify({"error": "Invalid URL or property ID not found"}), 400
    
    property_id = match.group(1)

    property_api_url = f"{PROPERTY_API_URL}/{property_id}"
    property_response = requests.get(property_api_url)
    
    if property_response.status_code != 200:
        return jsonify({"error": "Property not found or failed to retrieve"}), 404

    property_data = property_response.json()
    user_prompt = request.json.get('prompt', '')

    ollama_response = ollama_generate(user_prompt, property_data)

    return jsonify({
        "property_data": property_data,
        "ollama_response": ollama_response
    })

def ollama_generate(prompt, data):
    combined_prompt = f"{prompt}\n\nProperty Details: {data}"
    
    payload = {
        "prompt": combined_prompt,
        "model": "llama3.2:3b"
    }
    
    response = requests.post(OLLAMA_API_URL, json=payload)
    
    if response.status_code == 200:
        return response.json().get('response', '')
    else:
        return {"error": "Failed to retrieve response from Ollama"}

if __name__ == '__main__':
    app.run(debug=True)
