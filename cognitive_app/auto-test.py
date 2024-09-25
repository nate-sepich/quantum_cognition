# auto-test.py
import time
from llm_client import generate_llm_response, generate_topic_follow_up, extract_entities_and_relationships_from_model
from utils import process_llm_response, get_context_from_graph
from neo4j import GraphDatabase

# Function to query the database and return relevant context for the LLM
# def get_graph_context(driver):
#     with driver.session() as session:
#         query = """
#         MATCH (n)-[r]->(m)
#         RETURN n, r, m LIMIT 100
#         """
#         result = session.run(query)
#         context = []
#         for record in result:
#             node_n = record['n']
#             node_m = record['m']
#             relationship = record['r']
#             context.append(f"{node_n['name']} -[{relationship.type}]-> {node_m['name']}")
#         return '\n'.join(context)

# Function to dynamically generate a follow-up question using LLM
def generate_follow_up_with_llm(history, graph_context):
    # Make an LLM call to generate the follow-up prompt based on history and context
    llm_response = generate_topic_follow_up(graph_context, history=history)
    
    # Return the follow-up question for the next iteration
    return llm_response

def run_automated_test(driver, initial_prompt, iterations=10, delay=4, refinement_interval=5):
    prompt = initial_prompt
    context_history = []  # History in the form of user/assistant exchanges
    exploration_count = 0

    for i in range(iterations):
        print(f"Iteration {i+1}: Prompt - {prompt}")
        
        # Get the current graph context to pass to the LLM
        graph_context = get_context_from_graph(prompt, driver)
        
        # Determine if it's exploration (Flash) or refinement (Pro) phase
        if exploration_count < refinement_interval:
            model_type = 'flash'  # Use Flash for exploration
            exploration_count += 1
        else:
            model_type = 'pro'  # Switch to Pro for refinement
            exploration_count = 0
        
        # Call the LLM to generate a response based on the model type
        response_data = generate_llm_response(prompt, graph_context, model_type)
        
        # Process the LLM's response (basic parsing and database updates)
        process_llm_response(response_data, driver)
        
        # Add the user/assistant exchange to the history
        context_history.append({
            "user": prompt,
            "assistant": response_data['response']
        })
        
        # Generate the next prompt dynamically using the LLM
        prompt = generate_follow_up_with_llm(context_history, graph_context)
        
        # Wait for a bit to avoid hitting rate limits
        time.sleep(delay)
    
    print("Automated test completed.")


# # Function to run the automated conversation test
# def run_automated_test(driver, initial_prompt, iterations=10, delay=4):
#     prompt = initial_prompt
#     context_history = []  # Used to build up a conversation history

#     for i in range(iterations):
#         print(f"Iteration {i+1}: Prompt - {prompt}")
        
#         # Get the current graph context to pass to the LLM
#         graph_context = get_graph_context(driver)
        
#         # Add conversation history to the context
#         full_context = '\n'.join([msg["user"] for msg in context_history]) + '\n' + graph_context

#         # Send the prompt to the LLM and get the response
#         response_data = extract_entities_and_relationships_from_model(prompt, full_context)
        
#         # Process the LLM's response and update the graph
#         process_llm_response(response_data, driver)
        
#         # Store the current user input and assistant response in history
#         context_history.append({
#             "user": prompt,
#             "assistant": response_data['response']
#         })
        
#         # Generate the next prompt dynamically using the LLM with history
#         prompt = generate_follow_up_with_llm(context_history, graph_context)
        
#         # Wait to avoid hitting rate limits
#         time.sleep(delay)
    
#     print("Automated test completed.")

# Function to initialize and run the test
def main():
    # Initialize Neo4j driver
    uri = "bolt://localhost:7687"  # Update as necessary
    driver = GraphDatabase.driver(uri, auth=("neo4j", "your_secure_password"))
    
    # Set the initial prompt
    initial_prompt = "Tell me about the python software development. With a clear focus on what it inherits from previous languages and where it seperates itself."
    
    # Run the automated test with the agent for 10 iterations
    run_automated_test(driver, initial_prompt, iterations=15, delay=4)

    driver.close()

if __name__ == "__main__":
    main()
