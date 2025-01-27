import requests
import json

# Function to make a test call to Ollama API
def test_ollama_call():
    ollama_url = "http://localhost:11434/api/generate"  # Replace with your actual Ollama API URL
    model = "llama3.2:3b"  # Replace with your desired model name

    # Sample prompt for testing Ollama
    payload = {
        "model": model,
        "prompt": "Provide a brief description of a 4-bedroom house with 2 bathrooms and 1875 square feet."
    }

    # Make the POST request to Ollama
    try:
        response = requests.post(ollama_url, json=payload)

        # Check if the response is ndjson
        if response.headers.get('Content-Type') == 'application/x-ndjson':
            # Process the ndjson response line by line
            for line in response.iter_lines():
                if line:
                    result = json.loads(line.decode('utf-8'))
                    print(result.get('response', ''))
        else:
            print(f"Unexpected Content-Type: {response.headers.get('Content-Type')}")
            print(f"Response content: {response.text}")

    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")

# Call the function to test Ollama
if __name__ == "__main__":
    test_ollama_call()
