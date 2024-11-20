import requests
import json

def generate(prompt, temperature=0.7, top_p=1.0):
  url = "https://openrouter.ai/api/v1/chat/completions"

  payload = {
    "model": "openai/gpt-4o-mini",
    "messages": [{"role": "system", "content": "You are a helpful assistant."}, {"role": "user", "content": prompt}],
    "temperature": temperature,
    "top_p": top_p,
    "max_tokens": 4096
  }

  headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer [redacted]'} # Place your OpenRouter API key here

  response = requests.request("POST", url, headers=headers, json=payload)
  
  return response.json()['choices'][0]['message']['content']