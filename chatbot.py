from flask import Flask, request, jsonify
import requests
import json
from api_decider import determine_api_url
from dotenv import load_dotenv
import os
from pymongo import MongoClient
from llama_index import GPTSimpleVectorIndex, MongoDBReader, ServiceContext

app = Flask(__name__)

# Load environment variables
load_dotenv()
BEARER_TOKEN = os.getenv("API_BEARER_TOKEN")
OLLAMA_API_URL = "http://localhost:11434/api/generate"  # Ensure Ollama is running locally
MONGO_URI = os.getenv("MONGO_URI")

client = MongoClient(MONGO_URI)
db = client['poi']
collection = db['amenities']

# Init LlamaIndex with MongoDB data
mongo_reader = MongoDBReader(collection)
index = GPTSimpleVectorIndex.from_documents(mongo_reader)

# Init service context for LlamaIndex
service_context = ServiceContext.from_defaults()

@app.route('/propertydetails', methods=['GET'])
def property_details():
    # Get the URL and prompt from query parameters
    current_url = request.args.get('url', '')
    user_prompt = request.args.get('prompt', '')

    if not current_url or not user_prompt:
        return jsonify({"error": "Both 'url' and 'prompt' query parameters are required."}), 400

    property_data = retrieve_property_data(current_url)
    if not property_data:
        augmented_data = index.query(user_prompt, service_context=service_context)
    else:
        augmented_data = augment_with_llamaindex(property_data, user_prompt)

    ollama_response = call_ollama(augmented_data, user_prompt)

    return ollama_response, 200

def retrieve_property_data(current_url):
    query = {"url": current_url}
    property_document = collection.find_one(query)
    
    if property_document:
        return property_document
    else:
        return None

def augment_with_llamaindex(property_data, user_prompt):
    query = user_prompt
    augmented_data = index.query(query, service_context=service_context)
    return augmented_data

def call_ollama(augmented_data, user_prompt):
    # Send property data and user prompt to Ollama and return its response
    ollama_prompt = (
        f"You are a chatbot helping someone learn more about a real estate property\n"
        f"Here's the property data:\n{json.dumps(augmented_data, indent=2)}\n\n"
        f"User question: {user_prompt}\n"
        f"Be straightforward and provide a clear, concise, and helpful answer for the user based on the property details."
    )

    headers = {"Content-Type": "application/json"}
    payload = {
        "model": "llama3.2:3b",
        "prompt": ollama_prompt
    }

    response = requests.post(OLLAMA_API_URL, headers=headers, json=payload)

    if response.status_code == 200:
        response_data = ""
        for line in response.iter_lines():
            if line:
                part = json.loads(line)
                response_data += part.get("response", "")
        return response_data.strip()
    else:
        return f"Failed to get a response from Ollama. Status code: {response.status_code}"

if __name__ == '__main__':
    app.run(debug=True)
