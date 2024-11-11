
# utils.py

import spacy
from typing import List
from models import NodeModel, RelationshipModel
from db_utils import  sanitize_identifier, create_or_update_node, create_or_update_relationship
# import logging


# Load spaCy model for keyword extraction
nlp = spacy.load('en_core_web_sm')
# logging.basicConfig(level=logging.DEBUG)

def extract_keywords(text: str) -> List[str]:
    doc = nlp(text)
    keywords = [token.lemma_.lower() for token in doc if not token.is_stop and not token.is_punct]
    # Include noun chunks and named entities
    keywords.extend([chunk.text.lower() for chunk in doc.noun_chunks])
    keywords.extend([ent.text.lower() for ent in doc.ents])
    return list(set(keywords))


def get_context_from_graph(user_input: str, driver) -> str:
    keywords = extract_keywords(user_input)
    with driver.session() as session:
        query = """
        MATCH (n)
        WHERE any(word IN $keywords WHERE toLower(n.name) CONTAINS word)
        OPTIONAL MATCH (n)-[r*1..3]-(m)
        RETURN n, labels(n) AS n_labels, collect(r) AS relationships, collect(m) AS related_nodes, collect(labels(m)) AS related_labels LIMIT 100
        """

        result = session.run(query, keywords=keywords)
        records = result.data()
        context_pieces = []

        for record in records:
            node = record['n']
            n_labels = record.get('n_labels', [])
            node_labels = ':'.join(n_labels)
            
            # Log the node information
            # logging.debug(f"Node Labels: {n_labels}")
            
            node_info = f"{node_labels} {node.get('name', '')}: {node.get('description', '')}"
            context_pieces.append(node_info)

            related_nodes = record.get('related_nodes', [])
            related_labels_list = record.get('related_labels', [])

            for idx, related_node in enumerate(related_nodes):
                related_labels = ':'.join(related_labels_list[idx]) if idx < len(related_labels_list) else ''
                related_info = f"{related_labels} {related_node.get('name', '')}: {related_node.get('description', '')}"
                context_pieces.append(related_info)
        context = '\n'.join(set(context_pieces))
        return context



def process_llm_response(response_data: dict, driver):
    # Extract the assistant's response
    assistant_response = response_data.get('response', '')

    # Get new entities and relationships
    new_entities = response_data.get('new_entities', [])
    new_relationships = response_data.get('new_relationships', [])

    # Update the Neo4j database
    with driver.session() as session:
        # Create or update new nodes
        for entity in new_entities:
            node_data = NodeModel(
                name=entity['name'],
                label=sanitize_identifier(entity['label']),
                properties=entity.get('properties', {})
            )
            session.write_transaction(create_or_update_node, node_data)

        # Create or update relationships
        for rel in new_relationships:
            rel_data = RelationshipModel(
                from_node=rel['from'],
                to_node=rel['to'],
                type=sanitize_identifier(rel['type']),
                properties=rel.get('properties', {})
            )
            session.write_transaction(create_or_update_relationship, rel_data)

    return assistant_response

