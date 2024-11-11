# llm_client.py
import json
import logging
import os
from dotenv import load_dotenv
from ollama import Client

# Load environment variables
load_dotenv()

# Configure the Ollama client
# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Initialize Ollama Client with FP16 precision to reduce memory usage
qc_ollama_model = os.getenv('QC_OLLAMA_MODEL', 'mistral')
qc_ollama_model_keep_alive = os.getenv('OLLAMA_KEEP_ALIVE', '1h')

logging.info(f'Pulling Ollama Model: {qc_ollama_model}')
client = Client(host='http://localhost:11434')
logging.info(f'Model Pull Status: {client.pull(qc_ollama_model)}')
sample = client.generate(model=qc_ollama_model, prompt='Hello! Respond with only Hello.',keep_alive=qc_ollama_model_keep_alive)
logging.info(f'Model Available for {qc_ollama_model_keep_alive}: {sample})')

# Helper function for response parsing
def parse_llm_response(response_text: str) -> dict:
    try:
        print(response_text)
        response_data = json.loads(response_text)
        return response_data
    except Exception as e:
        raise RuntimeError(f"Error parsing LLM response: {str(e)}")

def generate_llm_response(user_input: str, context: str, model_type='flash') -> dict:
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

    Make sure to use camel case for labels and uppercase with underscores for relationship types. Leave properties empty if no properties exist.
    """
    
    try:
        response = client.generate(model=qc_ollama_model, prompt=prompt, keep_alive=qc_ollama_model_keep_alive)
        content = response.get('response', '')
    except Exception as e:
        raise RuntimeError(f"Error calling LLM: {str(e)}")
    
    parsed_response = parse_llm_response(content)

    return parsed_response  # Now the response is guaranteed to be a dictionary


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
        response = client.generate(model=qc_ollama_model, prompt=prompt, keep_alive=qc_ollama_model_keep_alive)
        content = response.get('response', '')
    except Exception as e:
        raise RuntimeError(f"Error calling LLM: {str(e)}")
    
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
                chat_history.append({"role": "model", "content": exchange["assistant"]})
                
        # Add the follow-up prompt as the last user role
        chat_history.append({"role": "user", "content": prompt})

        # Start the chat session with the history
        response = client.chat(model=qc_ollama_model, messages=chat_history, keep_alive=qc_ollama_model_keep_alive)
        
        response = client.generate(model=qc_ollama_model, prompt=prompt, keep_alive=qc_ollama_model_keep_alive)
        content = response.get('response', '')
    except Exception as e:
        raise RuntimeError(f"Error calling LLM: {str(e)}")
    
    parsed_response = parse_llm_response(content)

    return parsed_response  # Now the response is guaranteed to be a dictionary
