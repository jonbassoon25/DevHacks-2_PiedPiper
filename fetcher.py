from supermemory import Supermemory
import requests
import json

GEMINI_API_KEY = "AIzaSyAkvDsC5hBAWi_-7d-jb1Pdkz7u8_lO0eE"


client = Supermemory(api_key="sm_7v34ad1Mm5XeKoiM2gNd2V_IZMERieGyPMWxXBJEeoiTNLeVyBKFznTiBielvymJErPcdiCrXTlXDevMqWYKirP")

query = "Kiwanis recreation center features what?"

results = client.search.memories(q=query, limit=3)

list_of_result_objects = results.results

extracted_memories = [item.memory for item in list_of_result_objects]

def get_gemini_response(user_query, context_memories):
    # The API endpoint for the specified model
    api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"
    
    # Format the context memories into a single string for the model
    context_string = "\n".join(context_memories)
    
    # Construct the full prompt, including both the context and the user's query
    full_prompt = (
        f"CONTEXT:\n{context_string}\n\n"
        f"USER_QUERY:\n{user_query}\n\n"
        f"Based on the CONTEXT, answer the USER_QUERY. If the context is not relevant, "
        f"use your general knowledge to provide a helpful response."
    )
    
    # The payload for the API request
    payload = {
        "contents": [
            {
                "parts": [
                    {"text": full_prompt}
                ]
            }
        ]
    }
    
    headers = {
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(api_url, headers=headers, data=json.dumps(payload))
        response.raise_for_status() # Raises an HTTPError for bad responses (4xx or 5xx)
        
        # Parse the JSON response
        response_json = response.json()
        
        # Extract the generated text from the response
        generated_text = response_json['candidates'][0]['content']['parts'][0]['text']
        return generated_text
        
    except requests.exceptions.HTTPError as errh:
        return f"HTTP Error: {errh}"
    except requests.exceptions.ConnectionError as errc:
        return f"Error Connecting: {errc}"
    except requests.exceptions.Timeout as errt:
        return f"Timeout Error: {errt}"
    except requests.exceptions.RequestException as err:
        return f"An unexpected error occurred: {err}"
    except (KeyError, IndexError) as e:
        return f"Could not parse the API response. Error: {e}"

print(extracted_memories)
extracted_memories = ", ".join(extracted_memories)
print(get_gemini_response(query, extracted_memories))