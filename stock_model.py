import requests
import json
import os
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

if OPENROUTER_API_KEY is None:
    raise ValueError("OPENROUTER_API_KEY is not set")

def generate(prompt, config):
  url = "https://openrouter.ai/api/v1/chat/completions"

  payload = {
    "model": config['model'],
    "messages": [{"role": "system", "content": "You are a helpful assistant."}, {"role": "user", "content": prompt}],
    "temperature": config['temperature'],
    "top_p": config['top_p'],
    "max_tokens": config['max_tokens']
  }

  headers = {'Content-Type': 'application/json', 'Authorization': f'Bearer {OPENROUTER_API_KEY}'}

  response = requests.request("POST", url, headers=headers, json=payload)
  
  return response.json()['choices'][0]['message']['content']