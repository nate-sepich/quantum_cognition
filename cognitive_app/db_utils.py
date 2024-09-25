from neo4j import GraphDatabase
from typing import Any, Dict
from models import NodeModel, RelationshipModel

def sanitize_identifier(identifier: str) -> str:
    # Remove invalid characters and replace spaces with underscores
    sanitized = ''.join(char if char.isalnum() else '_' for char in identifier)
    sanitized = sanitized.lstrip('0123456789')  # Remove leading digits
    if not sanitized:
        raise ValueError(f"Identifier '{identifier}' cannot be converted to a valid label or relationship type.")
    return sanitized

def sanitize_property_key(key: str) -> str:
    # Replace spaces and invalid characters with underscores
    sanitized = ''.join(char if char.isalnum() else '_' for char in key)
    sanitized = sanitized.lstrip('0123456789')
    if not sanitized:
        raise ValueError(f"Property key '{key}' cannot be converted to a valid property key.")
    return sanitized

def create_or_update_node(tx, node_data: NodeModel):
    # First, check if a node with the same name and label already exists
    query = f"""
    MATCH (n:{sanitize_identifier(node_data.label)} {{name: $name}})
    RETURN n
    """
    result = tx.run(query, name=node_data.name).single()
    
    if result is None:
        # Node does not exist, so create it
        properties = {sanitize_property_key(k): v for k, v in node_data.properties.items()}
        properties.update({
            'name': node_data.name,
            # 'importance': node_data.importance,
            # 'novelty': node_data.novelty,
            # 'confidence': node_data.confidence,
            'timestamp': node_data.timestamp,
        })
        
        # Prepare the properties for the Cypher query
        props = ", ".join(f"{sanitize_property_key(key)}: ${key}" for key in properties.keys())
        query = f"""
        CREATE (n:{sanitize_identifier(node_data.label)} {{name: $name}})
        SET n += {{{props}}}
        RETURN n
        """
        tx.run(query, **properties)
    else:
        # Node exists, so update its properties and avoid duplication
        properties = {sanitize_property_key(k): v for k, v in node_data.properties.items()}
        query = f"""
        MATCH (n:{sanitize_identifier(node_data.label)} {{name: $name}})
        SET n += $properties
        RETURN n
        """
        tx.run(query, name=node_data.name, properties=properties)

def create_or_update_relationship(tx, rel_data: RelationshipModel):
    # First, check if the relationship already exists between the two nodes
    query = f"""
    MATCH (a {{name: $from_node}})-[r:{sanitize_identifier(rel_data.type)}]->(b {{name: $to_node}})
    RETURN r
    """
    result = tx.run(query, from_node=rel_data.from_node, to_node=rel_data.to_node).single()
    
    if result is None:
        # Relationship does not exist, create it
        query = f"""
        MATCH (a {{name: $from_node}})
        MATCH (b {{name: $to_node}})
        MERGE (a)-[r:{sanitize_identifier(rel_data.type)}]->(b)
        SET r += $properties
        RETURN r
        """
        tx.run(
            query,
            from_node=rel_data.from_node,
            to_node=rel_data.to_node,
            properties=rel_data.properties
        )
    else:
        # Relationship exists, so update its properties
        query = f"""
        MATCH (a {{name: $from_node}})-[r:{sanitize_identifier(rel_data.type)}]->(b {{name: $to_node}})
        SET r += $properties
        RETURN r
        """
        tx.run(
            query,
            from_node=rel_data.from_node,
            to_node=rel_data.to_node,
            properties=rel_data.properties
        )

def create_node(tx, node_data: NodeModel):
    # Same logic as create_or_update_node but only for new nodes
    properties = {}
    for key, value in node_data.properties.items():
        sanitized_key = sanitize_property_key(key)
        properties[sanitized_key] = value
    # Add standard properties
    properties.update({
        'name': node_data.name,
        'importance': node_data.importance,
        'novelty': node_data.novelty,
        'confidence': node_data.confidence,
        'timestamp': node_data.timestamp,
    })
    # Prepare the properties for the Cypher query
    props = ", ".join(f"{sanitize_property_key(key)}: ${key}" for key in properties.keys())
    query = f"""
    MERGE (n:{sanitize_identifier(node_data.label)} {{name: $name}})
    SET n += {{{props}}}
    RETURN n
    """
    tx.run(query, **properties)

def create_relationship(tx, rel_data: RelationshipModel):
    query = f"""
    MATCH (a {{name: $from_node}})
    MERGE (a)-[r:{sanitize_identifier(rel_data.type)}]->(b {{name: $to_node}})
    ON CREATE SET b.name = $to_node
    SET r += $properties
    """
    tx.run(
        query,
        from_node=rel_data.from_node,
        to_node=rel_data.to_node,
        properties=rel_data.properties
    )
