from flask import Flask, request, jsonify
from pymongo import MongoClient
import requests
from fields import MONGO_FIELDS

app = Flask(__name__)

# MongoDB init
client = MongoClient("???")
db = client["???"]
collection = db["???"]

# Model init
OLLAMA_API_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "meta-llama/Llama-3.2-1B"

# Query MongoDB based on user input and fields
def query_mongo(user_input):
    query = {"$text": {"$search": user_input}}
    projection = {field: 1 for field in MONGO_FIELDS}
    projection["_id"] = 0
    documents = collection.find(query, projection)
    return list(documents)

# Generate a response with Ollama
def generate_response_with_ollama(prompt):
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt
    }
    response = requests.post(OLLAMA_API_URL, json=payload)
    
    if response.status_code == 200:
        return response.json().get("response", "No response generated.")
    else:
        return f"Error: {response.status_code}, {response.text}"

# Create a prompt for Ollama based on the retrieved MongoDB data
def generate_prompt(user_input, relevant_data):
    prompt = f"User: {user_input}\nRelevant Information:\n"
    for doc in relevant_data:
        for key, value in doc.items():
            prompt += f"{key}: {value}\n"
        prompt += "---\n"
    prompt += "Assistant:"
    return prompt

@app.route('/chatbot', methods=['POST'])
def ask_question():
    data = request.json
    user_input = data.get("question", "")
    
    if not user_input:
        return jsonify({"error": "No question provided"}), 400
    
    relevant_data = query_mongo(user_input)
    prompt = generate_prompt(user_input, relevant_data)
    response = generate_response_with_ollama(prompt)
    
    return jsonify({"response": response})

if __name__ == '__main__':
    app.run(debug=True)
