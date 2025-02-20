from flask import Flask, request, jsonify
import requests
import json
from dotenv import load_dotenv
import os
from pymongo import MongoClient
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain.schema import Document

app = Flask(__name__)

# Load environment variables
load_dotenv()
BEARER_TOKEN = os.getenv("API_BEARER_TOKEN")
OLLAMA_API_URL = "http://localhost:11434/api/generate"  # Ensure Ollama is running locally
MONGO_URI = os.getenv("MONGO_URI")

client = MongoClient(MONGO_URI)
db = client['poi']
collection = db['amenities']

embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# Function to load MongoDB data into FAISS index
def create_faiss_index():
    documents = []
    for doc in collection.find():
        doc['_id'] = str(doc['_id'])  # Convert ObjectId to string
        text = json.dumps(doc)  # Convert entire document to text
        documents.append(Document(page_content=text))

    text_splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    split_docs = text_splitter.split_documents(documents)

    faiss_index = FAISS.from_documents(split_docs, embedding_model)
    return faiss_index

@app.route('/propertydetails', methods=['GET'])
def property_details():
    # Get the URL and prompt from query parameters
    current_url = request.args.get('url', '')
    user_prompt = request.args.get('prompt', '')

    #Debug print lines
    print("User prompt recieved: " + str(user_prompt))
    print("Current URL: " + str(current_url))

    if not current_url or not user_prompt:
        return jsonify({"error": "Both 'url' and 'prompt' query parameters are required."}), 400

    property_data = retrieve_property_data(current_url)

    ''' Retrieves POI data, needs to be property data'''
    # for doc in collection.find().limit(1):
    #     print(doc)


    #Debug print lines
    print("Retrieved property data: " + str(property_data))

    if not property_data:
        # Create FAISS index from MongoDB data
        faiss_index = create_faiss_index()
        results = faiss_index.similarity_search(user_prompt)
        augmented_data = " ".join([res.page_content for res in results])
    else:
        augmented_data = augment_with_langchain(property_data, user_prompt)

    ollama_response = call_ollama(augmented_data, user_prompt)

    return ollama_response, 200

def retrieve_property_data(current_url):
    query = {"url": current_url}
    property_document = collection.find_one(query)
    
    if property_document:
        return property_document
    else:
        return None

def augment_with_langchain(property_data, user_prompt):
    # Convert property data to Document format
    property_text = json.dumps(property_data)
    document = Document(page_content=property_text)

    # Split the document into smaller chunks
    text_splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    split_docs = text_splitter.split_documents([document])

    # Create FAISS index from the split documents
    faiss_index = FAISS.from_documents(split_docs, embedding_model)

    # Query the FAISS index with the user prompt
    results = faiss_index.similarity_search(user_prompt)

    # Combine the results into a single response
    augmented_data = " ".join([res.page_content for res in results])
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
