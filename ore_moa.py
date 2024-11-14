# import requests
# import json


# def generate(prompt, temperature=0.7, top_p=1.0):
#     url = "http://localhost:5050/ensemble"

#     # Test payload
#     payload = {
#         "task": prompt,
#         "agents": [
#             {
#                 "model": "gpt-4o-mini",
#                 "api_key": "[redacted]",
#                 "api_url": "https://openrouter.ai/api/v1/chat/completions"
#             },
#             {
#                 "model": "gpt-4o-mini",
#                 "api_key": "[redacted]",
#                 "api_url": "https://openrouter.ai/api/v1/chat/completions"
#             }
#         ],
#         "coordinator": {
#             "model": "gpt-4o-mini",
#             "api_key": "[redacted]",
#             "api_url": "https://openrouter.ai/api/v1/chat/completions"
#         },
#         # "chain_store_api_key": "[redacted]",
#         # "max_tokens": 3000,
#         # "temperature": temperature,
#         # "top_p": top_p,
#         # "verbose": True,
#         # "return_reasoning": True,
#         # "max_workers": 2,
#         # "max_reasoning_steps": 5,
#         # "wolfram_app_id": "[redacted]",

#     }

#     headers = {'Content-Type': 'application/json'}

#     response = requests.request("POST", url, headers=headers, json=payload)
#     print(response.json())

#     try:
#         response_data = response.json()['response']
#         if response_data is None:
#             raise ValueError("Response is None")
#         return response_data
#     except:
#         try:
#             print('Response not found, trying again.')
#             response = requests.request("POST", url, headers=headers, json=payload)
#             response_data = response.json()['response']
#             if response_data is None:
#                 raise ValueError("Response is None")
#             return response_data
#         except:
#             print('Response not found, trying again x2.')
#             response = requests.request("POST", url, headers=headers, json=payload)
#             response_data = response.json()['response']
#             if response_data is None:
#                 raise ValueError("Response is None")
#             return response_data


# print(generate("hi"))


import requests
import json

def generate(prompt, temperature=0.7, top_p=1.0):
    url = "http://localhost:5050/ensemble"
    
    payload = {
        "task": prompt,
        "agents": [
            {
                "model": "gpt-4o-mini",
                "api_key": "[redacted]",
                "api_url": "https://openrouter.ai/api/v1/chat/completions",
                "temperature": .9,
            },
            {
                "model": "gpt-4o-mini",
                "api_key": "[redacted]",
                "api_url": "https://openrouter.ai/api/v1/chat/completions",
                "temperature": .1,
            },
            {
                "model": "gpt-4o-mini",
                "api_key": "[redacted]",
                "api_url": "https://openrouter.ai/api/v1/chat/completions",
                "temperature": .5,
            }
        ],
        "coordinator": {
            "model": "gpt-4o-mini",
            "api_key": "[redacted]",
            "api_url": "https://openrouter.ai/api/v1/chat/completions",
            "temperature": .3,
        },
        "max_tokens": 3000,
        "temperature": temperature,
        "top_p": top_p,
        "verbose": True,
        "max_workers": 3,
        "return_reasoning": True,
        "max_reasoning_steps": 40,
        "wolfram_app_id": "[redacted]",
    }

    headers = {'Content-Type': 'application/json'}

    # Using json parameter instead of data
    response = requests.request("POST", url, headers=headers, json=payload)
    print(response.json())

    try:
        response_data = response.json()['response']
        if response_data is None:
            raise ValueError("Response is None")
        return response_data
    except:
        try:
            print('Response not found, trying again.')
            response = requests.request("POST", url, headers=headers, json=payload)
            response_data = response.json()['response']
            if response_data is None:
                raise ValueError("Response is None")
            return response_data
        except:
            print('Response not found, trying again x2.')
            response = requests.request("POST", url, headers=headers, json=payload)
            response_data = response.json()['response']
            if response_data is None:
                raise ValueError("Response is None")
            return response_data
        
# print(generate("Every morning Aya goes for a 9-kilometer-long walk and stops at a coffee shop afterwards. When she walks at a constant speed of s kilometers per hour, the walk takes her 4 hours, including t minutes spent in the coffee shop. When she walks s + 2 kilometers per hour, the walk takes her 2 hours and 24 minutes, including t minutes spent in the coffee shop. Suppose Aya walks at s + 1/2 kilometers per hour. Find the number of minutes the walk takes her, including the t minutes spent in the coffee shop."))