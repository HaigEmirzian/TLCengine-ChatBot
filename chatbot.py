from dotenv import load_dotenv
from flask import Flask, request, jsonify
from pymongo import MongoClient
from transformers import LlamaForCausalLM, LlamaTokenizer
import torch

app = Flask(__name__)

# TODO: MongoDB init
client = MongoClient("???")
db = client["???"]
collection = db["???"]

# LLaMA3 init
model_name = "meta-llama/Llama-3.2-1B"
tokenizer = LlamaTokenizer.from_pretrained(model_name)
model = LlamaForCausalLM.from_pretrained(model_name)

# Get data from MongoDB
def retrieve_data_from_mongo(user_query):
    mongo_query = {
        # TODO: Implement parameters
        "$or": [
            {"location": {"$regex": user_query, "$options": "i"}},
            {"price": {"$regex": user_query, "$options": "i"}},
            {"bedrooms": {"$regex": user_query, "$options": "i"}},
            {"square_footage": {"$regex": user_query, "$options": "i"}},
            {"consensus_info": {"$regex": user_query, "$options": "i"}}
        ]
    }

    # Fetch matching documents from MongoDB
    retrieved_docs = list(collection.find(mongo_query))

    if len(retrieved_docs) == 0:
        return "No relevant property information found in the database."

    # TODO: Update parameters
    # Format retrieved data into a string for the LLaMA model
    processed_data = ""
    for doc in retrieved_docs:
        processed_data += (
            f"Location: {doc.get('location', 'N/A')}, "
            f"Price: {doc.get('price', 'N/A')}, "
            f"Bedrooms: {doc.get('bedrooms', 'N/A')}, "
            f"Square Footage: {doc.get('square_footage', 'N/A')}, "
            f"Consensus Info: {doc.get('consensus_info', 'N/A')}\n"
        )

    return processed_data

# Route for chatbot window
@app.route('/', methods=['POST'])
def index():
    # Get user input
    data = request.get_json()
    user_input = data.get('message')

    # Fetch mongo data
    mongo_data = retrieve_data_from_mongo(user_input)

    # Tokenize inputs
    inputs = tokenizer(mongo_data + user_input, return_tensors="pt")

    # Generate a response
    outputs = model.generate(**inputs, max_length=500, num_return_sequences=1, do_sample=False)
    
    # Decode the model's response
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)

    return jsonify({"response": response})

if __name__ == '__main__':
    app.run(debug=True)
