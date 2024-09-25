# llm_client.py

import os
import json
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()

# Check if GOOGLE_API_KEY is set
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise ValueError("GOOGLE_API_KEY environment variable not set")

# Configure the Google Generative AI client
genai.configure(api_key=api_key)


# Helper function for response parsing
def parse_llm_response(response_text: str) -> dict:
    try:
        json_start = response_text.find('```json')
        json_end = response_text.find('```', json_start + 7)
        if json_start != -1 and json_end != -1:
            json_content = response_text[json_start + 7:json_end].strip()
            return json.loads(json_content)
        else:
            raise ValueError("Failed to extract JSON from the LLM response.")
    except Exception as e:
        raise RuntimeError(f"Error parsing LLM response: {str(e)}")

def generate_llm_response(user_input: str, context: str, model_type='flash') -> dict:
    model = genai.GenerativeModel(f'gemini-1.5-{model_type}')
    
    # Construct the prompt to guide the LLM in generating the right output
    prompt = f"""
    Based on the provided context and user input, extract relevant entities and relationships. If no context provided, assume you are the first iteration of many LLM calls to answer the initial prompt.

    Context:
    {context}

    User input: "{user_input}"

    Please extract the following information and return the response in the JSON format below:

    {{
        "response": "Your response to the user.",
        "new_entities": [
        {{
            "name": "Entity Name",
            "label": "EntityLabelNoSpaces",
            "properties": {{}}
        }}
        ],
        "new_relationships": [
        {{
            "from": "Entity Name or ID",
            "to": "Entity Name or ID",
            "type": "RELATIONSHIP_TYPE_NO_SPACES",
            "properties": {{}}
        }}
        ]
    }}

    Make sure to use camel case for labels and uppercase with underscores for relationship types. Leave properties empty if no properties exist.
    """
    
    try:
        response = model.generate_content(prompt)
        
    except Exception as e:
        raise RuntimeError(f"Error calling LLM: {str(e)}")
    
    parsed_response = parse_llm_response(response.text)

    return parsed_response  # Now the response is guaranteed to be a dictionary


def extract_entities_and_relationships_from_model(user_input: str, context: str) -> dict:
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        # Construct the prompt to guide the LLM in generating the right output
        prompt = f"""
        Based on the provided context and user input, extract relevant entities and relationships.

        Context:
        {context}

        User input: "{user_input}"

        Please extract the following information and return the response in the JSON format below:

        {{
          "response": "Your response to the user.",
          "new_entities": [
            {{
              "name": "Entity Name",
              "label": "EntityLabelNoSpaces",
              "properties": {{}}
            }}
          ],
          "new_relationships": [
            {{
              "from": "Entity Name or ID",
              "to": "Entity Name or ID",
              "type": "RELATIONSHIP_TYPE_NO_SPACES",
              "properties": {{}}
            }}
          ]
        }}

        Make sure to use camel case for labels and uppercase with underscores for relationship types. Leave properties empty if no properties exist.
        """
        
        # Generate response from the LLM
        response = model.generate_content(prompt)

    except Exception as e:
        raise RuntimeError(f"Failed to get a response from the LLM: {str(e)}")
    
    parsed_response = parse_llm_response(response.text)
    
    return parsed_response

import google.generativeai as genai

def generate_topic_follow_up(graph_context, history: list = None) -> str:
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        
        # Construct the prompt to generate a follow-up question
        prompt = f"""
        Based on the chat history and the current graph context, generate a meaningful follow-up question for further exploration.

        Graph Context:
        {graph_context}

        Please generate a detailed and exploratory follow-up question.
        """

        # Prepare chat history if available
        chat_history = []
        if history:
            for exchange in history:
                chat_history.append({"role": "user", "parts": exchange["user"]})
                chat_history.append({"role": "model", "parts": exchange["assistant"]})

        # Start the chat session with the history
        chat = model.start_chat(history=chat_history)
        
        # Send the follow-up prompt and get the response
        response = chat.send_message(prompt)
        
        # Ensure the response is parsed and returned as plain text
        return response.text.strip()

    except Exception as e:
        raise RuntimeError(f"Failed to get a response from the LLM: {str(e)}")


