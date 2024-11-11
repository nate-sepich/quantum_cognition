# auto-test.py
import time
import json
from llms.ollama_client import generate_llm_response, generate_topic_follow_up
# from llms.nim_client import generate_llm_response, generate_topic_follow_up
from utils import process_llm_response, get_context_from_graph
from neo4j import GraphDatabase

# Function to dynamically generate a follow-up question using LLM
def generate_follow_up_with_llm(history, graph_context):
    # Make an LLM call to generate the follow-up prompt based on history and context
    llm_response = generate_topic_follow_up(graph_context, history=history)
    
    # Return the follow-up question for the next iteration
    return llm_response

def run_automated_test(driver, initial_prompt, iterations=10, delay=4, refinement_interval=5, max_retries=3):
    prompt = initial_prompt
    context_history = []  # History in the form of user/assistant exchanges

    for i in range(iterations):
        print(f"Iteration {i+1}: Prompt - {prompt}")
        prompt = prompt['response'] if isinstance(prompt, dict) else prompt
        # Get the current graph context to pass to the LLM
        graph_context = get_context_from_graph(prompt, driver)
        
        # Retry logic for LLM response
        for attempt in range(max_retries):
            try:
                # Call the LLM to generate a response based on the model type
                response_data = generate_llm_response(prompt, graph_context)
                
                # Process the LLM's response (basic parsing and database updates)
                process_llm_response(response_data, driver)
                
                # Add the user/assistant exchange to the history
                context_history.append({
                    "user": prompt,
                    "assistant": response_data['response']
                })
                
                # Generate the next prompt dynamically using the LLM
                prompt = generate_follow_up_with_llm(context_history, graph_context)
                
                # Break out of the retry loop if successful
                break
            except (json.JSONDecodeError, KeyError) as e:
                print(f"Attempt {attempt + 1} failed: {e}")
                if attempt == max_retries - 1:
                    print("Max retries reached. Skipping to next iteration.")
                    prompt = "Sorry, I couldn't process the response. Let's try something else."
        
        # Wait for a bit to avoid hitting rate limits
        time.sleep(delay)
    
    print("Automated test completed.")

# Function to initialize and run the test
def main():
    # Initialize Neo4j driver
    uri = "bolt://localhost:7687"  # Update as necessary
    driver = GraphDatabase.driver(uri, auth=("neo4j", "your_secure_password"))
    
    # Set the initial prompt
    initial_prompt = "What is computing? How did computers become so prevalent in human's lives?"
    
    # Run the automated test with the agent for 10 iterations
    run_automated_test(driver, initial_prompt, iterations=5, delay=1)

    driver.close()

if __name__ == "__main__":
    main()
