import requests

url = "http://127.0.0.1:5000/"
payload = {
    "url": "https://krishnam-uat.tlcengine.com/propertydetail/6570389/100-John-T-O-Leary-Boulevard-#225_South-Amboy_NJ_08879",
    "prompt": "Tell me about this property."
}

response = requests.post(url, json=payload)
print(response.json())
