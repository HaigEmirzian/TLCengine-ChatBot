from dotenv import load_dotenv
from flask import Flask, request, jsonify
from pymongo import MongoClient
from transformers import LlamaForCausalLM, LlamaTokenizer
import torch


# Load environment variables
load_dotenv()

app = Flask(__name__)

# TODO: MongoDB init
client = MongoClient("???")
db = client["???"]
collection = db["???"]

# LLaMA3 init
model_name = "meta-llama/Llama-3.2-1B"
tokenizer = LlamaTokenizer.from_pretrained(model_name)
model = LlamaForCausalLM.from_pretrained(model_name)

# Route for chatbot window
@app.route('/', methods=['POST'])
def index():
    # Get user input
    data = request.get_json()
    user_input = data.get('message')

    # Tokenize inputs
    inputs = tokenizer(user_input, return_tensors="pt")

    # Generate a response
    outputs = model.generate(**inputs, max_length=500, num_return_sequences=1, do_sample=False)
    
    # Decode the response
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    
    # Save the conversation to MongoDB
    conversation = {
        "user_message": user_input,
        "bot_response": response
    }

    collection.insert_one(conversation)
    
    return jsonify({"response": response})

if __name__ == '__main__':
    app.run(debug=True)
