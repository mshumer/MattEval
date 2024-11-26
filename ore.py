"""
For testing OpenReasoningEngine. Adjust the settings in the payload as necessary. Different benchmarks tend to benefit from different settings, so feel free to try a few to find what works best.
"""

import requests
import json
import os

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

if OPENROUTER_API_KEY is None:
    raise ValueError("OPENROUTER_API_KEY is not set")

def generate(prompt, config):
  url = "http://localhost:5050/reason"

  payload = json.dumps({
      "task": prompt,
      "api_key": OPENROUTER_API_KEY,
      "model": config['model'],
      "api_url": "https://openrouter.ai/api/v1/chat/completions",
      "max_tokens": config['max_tokens'],
      "temperature": config['temperature'],
      "verbose": config['verbose'],
      "max_reasoning_steps": config['max_reasoning_steps'],
      "use_jeremy_planning": config['use_jeremy_planning'],
      "use_planning": config['use_planning'],
      "reflection_mode": config['reflection_mode'],
  })
  headers = {'Content-Type': 'application/json'}

  response = requests.request("POST", url, headers=headers, data=payload)

  # Try up to 3x, as the ORE still sometimes errors out
  try:
    response_data = response.json()['response']['content']
    if response_data is None:
      raise ValueError("Response is None")
    return response_data
  except:
    try:
      print('Response not found, trying again.')
      response = requests.request("POST", url, headers=headers, data=payload)
      response_data = response.json()['response']['content']
      if response_data is None:
        raise ValueError("Response is None")
      return response_data
    except:
      print('Response not found, trying again x2.')
      response = requests.request("POST", url, headers=headers, data=payload)
      response_data = response.json()['response']['content']
      if response_data is None:
        raise ValueError("Response is None") 
      return response_data