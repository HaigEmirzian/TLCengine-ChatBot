import requests
import json

class PropertyDetailsFetcher:
    def __init__(self, property_id, api_url, token):
        self.property_id = property_id
        self.api_url = api_url
        self.headers = {
            "Authorization": f"bearer {token}",
            "Content-Type": "application/json"
        }

    def get_property_data(self):
        # Construct the full URL
        url = f"{self.api_url}/v3/api/cjmls/ListingsData/{self.property_id}"
        
        # Make the GET request
        response = requests.get(url, headers=self.headers)
        
        # Check if the request was successful
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Failed to retrieve property data. Status code: {response.status_code}")
            print(f"Response content: {response.text}")
            return None

    def extract_property_details(self, property_data):
        # Extract relevant details from the property data
        if property_data:
            listing = property_data.get("ListingDetail", {}).get("Listing", {})
            
            address = listing.get("UNPARSEDADDRESS", "N/A")
            price = listing.get("LISTPRICE", "N/A")
            beds = listing.get("BEDROOMSTOTAL", "N/A")
            baths = listing.get("BATHROOMSTOTALDECIMAL", "N/A")
            sqft = listing.get("LIVINGAREA", "N/A")

            # Return the extracted details
            return {
                "Address": address,
                "Price": price,
                "Bedrooms": beds,
                "Bathrooms": baths,
                "Square Footage": sqft
            }
        else:
            return {}

    def call_ollama(self, details):
        ollama_url = "http://localhost:11434/api/generate"  # Replace with actual Ollama API URL

        # Create a payload with the property details for Ollama
        payload = {
            "model": "llama3.2:3b",
            "prompt": f"Address: {details['Address']}, Price: {details['Price']}, Bedrooms: {details['Bedrooms']}, Bathrooms: {details['Bathrooms']}, Square Footage: {details['Square Footage']}. How much sq ft is this house?. Only answer the question"
        }

        # Send the request to Ollama
        response = requests.post(ollama_url, json=payload)

        combined_response = ""

        # Check if the content type is ndjson
        if response.headers.get('Content-Type') == 'application/x-ndjson':
            try:
                # Process the ndjson response line by line and concatenate responses
                for line in response.iter_lines():
                    if line:
                        result = json.loads(line.decode('utf-8'))
                        combined_response += result.get('response', '')
                return combined_response
            except ValueError:
                print("Failed to decode JSON from response.")
        else:
            print(f"Unexpected Content-Type: {response.headers.get('Content-Type')}")
            print(f"Response content: {response.text}")

    def Ollama_response_from_propertyid(self):
        # Fetch property data
        property_data = self.get_property_data()
        
        # Extract property details
        details = self.extract_property_details(property_data)
        
        # Call Ollama with the extracted property details and return the response
        return self.call_ollama(details)

#Usage
if __name__ == "__main__":
    property_id = "6570342"
    api_url = "https://uat-api.tlcengine.com/v3/api/cjmls/ListingsData/6570389"
    token = "5147FACE-1211-444E-A563-F0B85B3C12D1"
    
    fetcher = PropertyDetailsFetcher(property_id, api_url, token)
    
    # Call Ollama with the property details and print the response
    print(fetcher.Ollama_response_from_propertyid())
