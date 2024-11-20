"""
For testing OpenReasoningEngine. Adjust the settings in the payload as necessary. Different benchmarks tend to benefit from different settings, so feel free to try a few to find what works best.
"""

import requests
import json


def generate(prompt, temperature=0.7, top_p=1.0):
  url = "http://localhost:5050/reason"

  payload = json.dumps({
      "task": prompt,
      "api_key": "[redacted]", # add your OpenRouter API key here
      "model": "gpt-4o-mini",
      "api_url": "https://openrouter.ai/api/v1/chat/completions",
      "max_tokens": 3000,
      "temperature": temperature,
      "verbose": True, # Allows you to audit the ORE system behavior
      "max_reasoning_steps": 100,
  })
  headers = {'Content-Type': 'application/json'}

  response = requests.request("POST", url, headers=headers, data=payload)

  # Try up to 3x, as the ORE still sometimes errors out
  try:
    response_data = response.json()['response']
    if response_data is None:
      raise ValueError("Response is None")
    return response_data
  except:
    try:
      print('Response not found, trying again.')
      response = requests.request("POST", url, headers=headers, data=payload)
      response_data = response.json()['response']
      if response_data is None:
        raise ValueError("Response is None")
      return response_data
    except:
      print('Response not found, trying again x2.')
      response = requests.request("POST", url, headers=headers, data=payload)
      response_data = response.json()['response']
      if response_data is None:
        raise ValueError("Response is None") 
      return response_data