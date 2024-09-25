from neo4j import GraphDatabase
import datetime
import os

# Neo4j connection
uri = "bolt://localhost:7687"  # Update if necessary
driver = GraphDatabase.driver(uri, auth=("neo4j", "your_secure_password"))

def generate_report():
    with driver.session() as session:
        report = {}

        # Metric 1: Node Duplication Rate
        dup_query = """
        MATCH (n)
        WITH n.name AS nodeName, count(*) AS count
        WHERE count > 1
        RETURN nodeName, count
        """
        duplicates = session.run(dup_query)
        dup_count = duplicates.data()
        report['Node Duplication'] = len(dup_count)

        # Metric 2: Relationship Density
        rel_density_query = """
        MATCH (n)-[r]->(m)
        RETURN COUNT(r) / COUNT(DISTINCT n) AS avg_relationships_per_node
        """
        rel_density = session.run(rel_density_query).single()
        report['Relationship Density'] = rel_density["avg_relationships_per_node"]

        # Metric 3: Isolated Nodes
        isolated_nodes_query = """
        MATCH (n)
        WHERE NOT (n)--()
        RETURN COUNT(n) AS isolatedNodeCount
        """
        isolated_nodes = session.run(isolated_nodes_query).single()
        report['Isolated Nodes'] = isolated_nodes["isolatedNodeCount"]

        # Metric 4: Relationship Coverage
        rel_types_query = """
        MATCH ()-[r]->()
        RETURN DISTINCT type(r) AS relationshipTypes, COUNT(r) AS count
        """
        rel_types = session.run(rel_types_query)
        relationship_type_count = rel_types.data()
        report['Relationship Coverage'] = len(relationship_type_count)

        # Metric 5: Node Type Distribution
        node_type_query = """
        MATCH (n)
        RETURN labels(n) AS nodeTypes, COUNT(n) AS count
        """
        node_types = session.run(node_type_query).data()
        report['Node Type Distribution'] = {tuple(record['nodeTypes']): record['count'] for record in node_types}

        # Metric 6: Redundant Relationships
        redundant_rel_query = """
        MATCH (a)-[r]->(b)
        WITH a, b, type(r) AS relType, COUNT(*) AS relCount
        WHERE relCount > 1
        RETURN a.name, b.name, relType, relCount
        """
        redundant_rels = session.run(redundant_rel_query)
        redundant_rel_count = redundant_rels.data()
        report['Redundant Relationships'] = len(redundant_rel_count)

        # Metric 7: Node Creation Time Relative to Neighbors
        time_diff_query = """
        MATCH (n)-[r]->(m)
        WHERE exists(n.timestamp) AND exists(m.timestamp)
        WITH n, m, abs(duration.between(n.timestamp, m.timestamp).days) AS time_diff
        RETURN avg(time_diff) AS avg_time_diff
        """
        time_diff_result = session.run(time_diff_query).single()
        report['Node Creation Time Difference (Relative)'] = time_diff_result["avg_time_diff"]

        # Generate the overall graph score based on the report
        report_content = calculate_graph_score(report)

        # Save report to file
        save_report(report_content)

def calculate_graph_score(report):
    total_nodes = sum(report['Node Type Distribution'].values())
    total_relationships = report.get('Relationship Coverage', 0)

    # Node Duplication Score
    node_duplication_score = max(0, 100 - ((report['Node Duplication'] / total_nodes) * 100))
    
    # Isolated Nodes Score
    isolated_node_score = max(0, 100 - ((report['Isolated Nodes'] / total_nodes) * 100))
    
    # Relationship Density Score (scale from 2 to 5 relationships per node is optimal)
    avg_relationships = report['Relationship Density']
    relationship_density_score = min(avg_relationships / 5, 1) * 100 if avg_relationships >= 2 else max(0, (avg_relationships / 2) * 100)
    
    # Relationship Coverage Score (optimal coverage up to 15 distinct types)
    relationship_coverage_score = min(report['Relationship Coverage'] / 15, 1) * 100
    
    # Redundant Relationship Score
    redundant_relationship_score = max(0, 100 - ((report['Redundant Relationships'] / total_relationships) * 100)) if total_relationships > 0 else 100

    # Example for the new metric:
    node_creation_time_score = 100 - (min(report['Node Creation Time Difference (Relative)'], 100))  # Scale based on avg time difference

    # Final Score (weighted)
    final_score = (
        (0.25 * node_duplication_score) +
        (0.20 * isolated_node_score) +
        (0.15 * relationship_density_score) +
        (0.10 * relationship_coverage_score) +
        (0.15 * redundant_relationship_score) +
        (0.15 * node_creation_time_score)
    )

    # Build report content
    report_content = f"""
=== Graph Health Score ===
Node Duplication Score: {node_duplication_score:.2f}
Isolated Node Score: {isolated_node_score:.2f}
Relationship Density Score: {relationship_density_score:.2f}
Relationship Coverage Score: {relationship_coverage_score:.2f}
Redundant Relationship Score: {redundant_relationship_score:.2f}
Node Creation Time Difference Score: {node_creation_time_score:.2f}
Overall Graph Score: {final_score:.2f}/100

=== Neo4j Graph Metrics Report ===
Generated on: {datetime.datetime.now()}

--- Node Metrics ---
Node Duplication Rate: {report['Node Duplication']} duplicate nodes
Isolated Nodes: {report['Isolated Nodes']} nodes with no relationships
Node Creation Time Difference (Relative): {report['Node Creation Time Difference (Relative)']} days average time difference

--- Relationship Metrics ---
Average Relationship Density: {report['Relationship Density']} relationships per node
Relationship Coverage: {report['Relationship Coverage']} distinct relationship types
Redundant Relationships: {report['Redundant Relationships']} redundant relationships found

--- Node Type Distribution ---
"""
    for node_type, count in report['Node Type Distribution'].items():
        report_content += f"{node_type}: {count} nodes\n"

    return report_content

def save_report(report_content):
    # Ensure the reports directory exists
    os.makedirs("reports", exist_ok=True)

    # Generate a timestamped filename
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"reports/graph_metrics_report_{timestamp}.txt"

    # Write the report content to the file
    with open(filename, "w") as file:
        file.write(report_content)

    print(f"Report saved to: {filename}")

if __name__ == "__main__":
    generate_report()
