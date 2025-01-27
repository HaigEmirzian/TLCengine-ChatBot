import json

# Load Postman collection
with open("postman_collection.json", "r") as f:
    postman_data = json.load(f)

api_endpoints = {}

def extract_endpoints(items):
    for item in items:
        if "item" in item:
            # Recursive call for nested folders
            extract_endpoints(item["item"])
        elif "request" in item:
            # Check if the request method is GET
            if item["request"]["method"] == "GET":
                # Extract the endpoint name and URL for GET requests
                name = item["name"]
                url = item["request"]["url"]["raw"]
                
                # Replace path variables with placeholders if needed
                url = url.replace("{{baseUrl}}", "https://uat-api.tlcengine.com")
                
                # Store only the GET request URL
                api_endpoints[name] = url

# Start extracting from the root item
extract_endpoints(postman_data["item"])

# Save only the GET API endpoints to a new file
with open("get_api_endpoints.json", "w") as f:
    json.dump(api_endpoints, f, indent=4)

print("GET API endpoints saved to get_api_endpoints.json")
