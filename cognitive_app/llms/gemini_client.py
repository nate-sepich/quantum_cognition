import json
import os
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

def generate_response_from_model(user_input: str, context: str) -> str:
    try:
        # Initialize the model
        model = genai.GenerativeModel('gemini-1.5-flash')

        # Construct the prompt within this function
        # Construct the prompt
        prompt = f"""
    You are an assistant that provides information based on the context provided.

    Context:
    {context}

    User: {user_input}

    Assistant:
    Please provide your response to the user using the information from the context above, if the provided context doesn't answer the question use your default knowledge to answer.

    Then, extract any new concepts, entities, or relationships mentioned in your response or the user's input. If there are existing nodes provided by the context, you should add to them with your extraction.

    Present ONLY the extracted data in the following JSON format:

    ```json
    {{
    "response": "Your response to the user.",
    "new_entities": [ ... ],
    "new_relationships": [ ... ]
    }} Ensure the JSON is valid and correctly formatted. Do not include any text outside the JSON block. """
        
        # Generate content from LLM
        response = model.generate_content(prompt, max_tokens=350, temperature=0.7)

        # Extract the content from the response object
        if hasattr(response, 'text'):
            content = response.text
        else:
            content = str(response)

        # Clean up the response content
        # Assuming the LLM outputs the JSON within triple backticks
        json_start = content.find('```json')
        json_end = content.find('```', json_start + 1)
        if json_start != -1 and json_end != -1:
            json_content = content[json_start + 7:json_end].strip()
        else:
            raise ValueError("Failed to extract JSON from the LLM response.")

        # Parse the JSON content
        parsed_response = json.loads(json_content)

    except Exception as e:
        raise RuntimeError(f"Failed to get a response from the LLM: {str(e)}")

    return parsed_response

