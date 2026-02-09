import requests
import json
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

URL = "https://ollama-ollama.ginee6.easypanel.host/api/generate"
payload = {
    "model": "llama3.2:1b",
    "prompt": "Respond with a JSON object: {'status': 'ok'}",
    "stream": False
}

try:
    print(f"Testing connection to {URL}...")
    response = requests.post(URL, json=payload, timeout=120, verify=False)
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        print("Response JSON:")
        print(response.json().get("response"))
    else:
        print(f"Error: {response.text}")
except Exception as e:
    print(f"Exception: {e}")
