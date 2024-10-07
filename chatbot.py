from flask import Flask, request, jsonify
from pymongo import MongoClient
from transformers import LlamaForCausalLM, LlamaTokenizer
import torch

app = Flask(__name__)

# TODO: MongoDB init
client = MongoClient("???")
db = client["???"]
collection = db["???"]

# llama init
model_name = "meta-llama/Llama-3.2-1B"
tokenizer = LlamaTokenizer.from_pretrained(model_name)
model = LlamaForCausalLM.from_pretrained(model_name)

# Get data from MongoDB
def retrieve_data_from_mongo(user_query):
    mongo_query = {
        "$text": {
            # Full-text search on all fields indexed for text search
            "$search": user_query
        }
    }

    # Fetch matching documents from MongoDB
    retrieved_docs = list(collection.find(mongo_query).limit(10))

    if len(retrieved_docs) == 0:
        return "No relevant property information found."

    # Format retrieved data into a string for the llama model
    processed_data = ""
    for doc in retrieved_docs:
        for key, value in doc.items():
            # Exclude mongo internal id field
            if key != "_id":
                processed_data += f"{key.capitalize()}: {value}\n"
        processed_data += "\n"

    return processed_data

# Route for chatbot window
@app.route('/', methods=['POST'])
def index():
    # Get user input
    data = request.get_json()
    user_input = data.get('message')

    # Fetch mongo data
    mongo_data = retrieve_data_from_mongo(user_input)

    # Input for llama
    model_input = mongo_data + "\nUser Question: " + user_input

    # Tokenize inputs
    inputs = tokenizer(model_input, return_tensors="pt")

    # Generate response from the model
    outputs = model.generate(**inputs, max_length=500, num_return_sequences=1, do_sample=False)
    
    # Decode the model's output to a readable response
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)

    return jsonify({"response": response})

if __name__ == '__main__':
    app.run(debug=True)
