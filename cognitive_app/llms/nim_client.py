import json
import logging
import os
from dotenv import load_dotenv
from openai import OpenAI  # Assuming you're using NVIDIA's OpenAI client

# Load environment variables
load_dotenv()

# Configure the NVIDIA OpenAI client
api_key = os.getenv('NVIDIA_API_KEY')

client = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key=api_key
)

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

qc_nvidia_model = os.getenv('QC_NVIDIA_MODEL', "nv-mistralai/mistral-nemo-12b-instruct")
nvidia_model_keep_alive = os.getenv('NVIDIA_KEEP_ALIVE', '1h')

logging.info(f'Pulling NVIDIA Model: {qc_nvidia_model}')

# Pull the NVIDIA model to ensure it is available
# (No direct equivalent pull method, but can handle via initial test request)

def generate_test_response():
    try:
        sample = client.chat.completions.create(
            model=qc_nvidia_model,
            messages=[{"role": "user", "content": "Hello! Respond with only Hello."}],
            temperature=0.5,
            max_tokens=50
        )
        logging.info(f'Model Available: {sample}')
    except Exception as e:
        logging.error(f"Error pulling NVIDIA model: {str(e)}")

generate_test_response()

# Helper function for response parsing
def parse_llm_response(response_text) -> dict:
    try:
        if isinstance(response_text, str):
            response_text = response_text.strip('`')
            response_data = json.loads(response_text)
        elif isinstance(response_text, dict):
            response_data = response_text
        else:
            raise ValueError("Unsupported response format")
        return response_data
    except Exception as e:
        raise RuntimeError(f"Error parsing LLM response: {str(e)}")

# Main LLM generation function
def generate_llm_response(user_input: str, context: str) -> dict:
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
            "label": "EntityLabel",
            "properties": {{}}
        }}
        ],
        "new_relationships": [
        {{
            "from": "Entity Name or ID",
            "to": "Entity Name or ID",
            "type": "RELATIONSHIP_TYPE",
            "properties": {{}}
        }}
        ]
    }}

    Make sure to use camel case for labels and uppercase with underscores for relationship types. Leave properties empty if no properties exist. Respond with only valid JSON, avoid any additional text or commentary.
    """
    
    try:
        response = client.chat.completions.create(
            model=qc_nvidia_model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,
            max_tokens=1024
        )
        content = response.choices[0].message.content
    except Exception as e:
        raise RuntimeError(f"Error calling LLM: {str(e)}")
    
    parsed_response = parse_llm_response(content)

    return parsed_response

# You can now use `generate_llm_response` in the same way to call the NVIDIA model
def extract_entities_and_relationships_from_model(user_input: str, context: str) -> dict:
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
          "label": "EntityLabel",
          "properties": {{}}
        }}
      ],
      "new_relationships": [
        {{

          "from": "Entity Name or ID",
          "to": "Entity Name or ID",
          "type": "RELATIONSHIP_TYPE",
          "properties": {{}}
        }}
      ]
    }}

    Make sure to use camel case for labels and uppercase with underscores for relationship types. Leave properties empty if no properties exist.
    """
    
    try:
        # Use NVIDIA OpenAI chat completion API to generate the response
        response = client.chat.completions.create(
            model=qc_nvidia_model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,
            max_tokens=1024
        )
        content = response.choices[0].message.content

    except Exception as e:
        raise RuntimeError(f"Error calling LLM: {str(e)}")

    # Parse the response into JSON format
    parsed_response = parse_llm_response(content)

    return parsed_response  # Now the response is guaranteed to be a dictionary

def generate_topic_follow_up(graph_context, history: list = None) -> str:
    try:
        # Construct the prompt to generate a follow-up question
        prompt = f"""
        Based on the chat history and the current graph context, generate a meaningful follow-up question for further exploration.

        Graph Context:
        {graph_context}

        Please generate a detailed and exploratory follow-up question.
        Respond in JSON format as shown below:
            
        {{
            "response": "Your follow-up question."
        }}
        """

        # Prepare chat history if available
        chat_history = []
        if history:
            for exchange in history:
                chat_history.append({"role": "user", "content": exchange["user"]})
                chat_history.append({"role": "assistant", "content": exchange["assistant"]})
        
        # Add the follow-up prompt as the last user message
        chat_history.append({"role": "user", "content": prompt})

        # Start the chat session with the history using NVIDIA's OpenAI client
        response = client.chat.completions.create(
            model=qc_nvidia_model,
            messages=chat_history,
            temperature=0.5,
            max_tokens=1024
        )
        content = response.choices[0].message.content

    except Exception as e:
        raise RuntimeError(f"Error calling LLM: {str(e)}")
    
    # Parse the response if it's in JSON format
    parsed_response = parse_llm_response(content)

    return parsed_response  # Now the response is guaranteed to be a dictionary


