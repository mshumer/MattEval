import requests
import json


def generate(prompt, temperature=0.7, top_p=1.0):
  url = "http://localhost:5050/reason"

  payload = json.dumps({
      "task": prompt,
      "api_key": "[redacted]",
      # "model": "anthropic/claude-3.5-sonnet",
      # "model": "x-ai/grok-beta",
      "model": "gpt-4o-mini",
      "api_url": "https://openrouter.ai/api/v1/chat/completions",
      "chain_store_api_key": "[redacted]",
      "max_tokens": 3000,
      "temperature": temperature,
      "wolfram_app_id": "[redacted]",
      "verbose": True,
      "max_reasoning_steps": 45,
  })
  headers = {'Content-Type': 'application/json'}

  response = requests.request("POST", url, headers=headers, data=payload)

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


# print(generate("hi"))
