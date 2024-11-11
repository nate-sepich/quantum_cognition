# main.py
## RECALL
from neo4j import GraphDatabase
import os
from dotenv import load_dotenv
from llms.ollama_client import extract_entities_and_relationships_from_model
# from llms.nim_client import extract_entities_and_relationships_from_model
from utils import get_context_from_graph, process_llm_response

# Load environment variables
load_dotenv()

# Configure Neo4j connection
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "your_secure_password")  # Replace with your actual password or set in .env

# Initialize Neo4j driver
driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

def main():
    print("Assistant is ready. Type 'exit' to quit.")
    while True:
        user_input = input("User: ")
        if user_input.lower() in ['exit', 'quit']:
            break

        # Get context from the graph database
        context = get_context_from_graph(user_input, driver)

        try:
            # Generate response using the LLM
            response_data = extract_entities_and_relationships_from_model(user_input, context)
            # Process the LLM response and update the database
            assistant_response = process_llm_response(response_data, driver)
            print(f"Assistant: {assistant_response}")
        except Exception as e:
            print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
