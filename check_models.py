import os

import requests
from dotenv import load_dotenv

load_dotenv()

api_key = os.environ["GROQ_API_KEY"]
url = "https://api.groq.com/openai/v1/models"
headers = {"Authorization": f"Bearer {api_key}"}

response = requests.get(url, headers=headers)
models = response.json()

for m in models["data"]:
    print(m["id"])
