from dotenv import load_dotenv
from flask import Flask, request, jsonify
from pymongo import MongoClient
from transformers import LlamaForCausalLM, LlamaTokenizer

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
    return


if __name__ == '__main__':
    app.run(debug=True)
