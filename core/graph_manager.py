import math
import networkx as nx
from typing import Dict, Any, List, Tuple
from .interfaces import BaseGraphManager

class GraphManager(BaseGraphManager):
    """NetworkX Graph manager with custom topological sorting and evidence path calculation."""

    def build_networkx_graph(self, traversal_data: Dict[str, Any]) -> nx.DiGraph:
        """Constructs a NetworkX DiGraph from structured node and edge citation dictionaries."""
        g = nx.DiGraph()
        
        # Add Nodes with metadata attributes
        nodes_dict = traversal_data.get("nodes", {})
        for title, metadata in nodes_dict.items():
            g.add_node(title, **metadata)
            
        # Add Edges
        edges = traversal_data.get("edges", [])
        for edge in edges:
            source = edge["source"]
            target = edge["target"]
            # Avoid self loops or double additions
            if g.has_node(source) and g.has_node(target):
                g.add_edge(source, target)
                
        return g

    def update_edge_weights(self, graph: nx.DiGraph, alpha: float, beta: float):
        """Dynamic edge weighting formula: W(u, v) = alpha * log10(Pop_v) + beta * IF_v."""
        for u, v in graph.edges():
            # Get target node metadata (since the evidence flows from parent v to child u or vice versa)
            # In citation graphs, u cites v (u -> v). 
            # The scientific 'strength' is based on the cohort scale & impact factor of the cited paper v.
            node_v = graph.nodes[v]
            
            pop_size = node_v.get("population_size")
            impact_factor = node_v.get("impact_factor", 1.0)
            
            # Normalize population size using log10, default to log10(100) = 2 if missing
            if pop_size and isinstance(pop_size, (int, float)) and pop_size > 0:
                log_pop = math.log10(pop_size)
            else:
                log_pop = 2.0  # Default fallback
                
            weight = (alpha * log_pop) + (beta * impact_factor)
            # Ensure weight is a float and not negative
            weight = max(0.1, round(weight, 3))
            
            # Store calculated weight on the edge
            graph[u][v]["weight"] = weight

    def solve_evidence_paths(self, graph: nx.DiGraph, source_node: str = None) -> List[Dict[str, Any]]:
        """Identifies and ranks the heaviest paths of evidence across the DAG."""
        if len(graph) == 0:
            return []

        # Ensure weights are calculated (if not already present, apply default alpha=1.0, beta=1.0)
        for u, v in graph.edges():
            if "weight" not in graph[u][v]:
                self.update_edge_weights(graph, 1.0, 1.0)

        # In a citation DAG, roots (influencers) have in-degree = 0 (or out-degree = 0 depending on citation direction).
        # In our system: Paper A -> cites -> Paper B.
        # Therefore, the parent paper (source of idea) has in-degree > 0, and out-degree = 0 (it cites nobody).
        # The input paper (current study) has in-degree = 0 (nobody in our local graph cites it yet) and cites others.
        # Sinks (root historical papers) have out-degree = 0.
        # Sources (contemporary papers) have in-degree = 0.
        
        # Let's find all contemporary papers (in_degree = 0) and historical root papers (out_degree = 0)
        contemporary_papers = [n for n, d in graph.in_degree() if d == 0]
        historical_roots = [n for n, d in graph.out_degree() if d == 0]
        
        if not contemporary_papers:
            contemporary_papers = [list(graph.nodes())[0]]
        if not historical_roots:
            historical_roots = [list(graph.nodes())[-1]]

        all_paths = []
        
        # Find all simple paths between contemporary papers and root historical papers
        for start in contemporary_papers:
            for end in historical_roots:
                if start == end:
                    continue
                try:
                    # networkx find_simple_paths
                    paths = list(nx.all_simple_paths(graph, start, end))
                    for path in paths:
                        # Calculate total path weight and gather details
                        total_weight = 0.0
                        path_edges = []
                        for i in range(len(path) - 1):
                            u, v = path[i], path[i+1]
                            edge_w = graph[u][v].get("weight", 1.0)
                            total_weight += edge_w
                            path_edges.append((u, v, edge_w))
                            
                        all_paths.append({
                            "path": path,
                            "edges": path_edges,
                            "total_weight": round(total_weight, 3),
                            "length": len(path) - 1
                        })
                except Exception:
                    pass

        # Sort paths by total weight descending
        all_paths.sort(key=lambda x: x["total_weight"], reverse=True)
        return all_paths

    def compute_network_metrics(self, graph: nx.DiGraph) -> Dict[str, Any]:
        """Calculates PageRank, In-Degree, and Out-Degree to rank papers by overall scientific influence."""
        if len(graph) == 0:
            return {}

        # 1. PageRank (academic importance metric)
        try:
            pagerank = nx.pagerank(graph, weight="weight", alpha=0.85)
        except Exception:
            # Fallback pagerank
            pagerank = {n: 1.0 / len(graph) for n in graph.nodes()}

        # 2. Centrality metrics
        in_degree = dict(graph.in_degree())
        out_degree = dict(graph.out_degree())
        
        # Compile rankings
        rankings = {}
        for node in graph.nodes():
            meta = graph.nodes[node]
            
            # Combine pagerank and population metric to define an "Evidence Score"
            pop = meta.get("population_size", 100)
            if not pop or not isinstance(pop, (int, float)):
                pop = 100
            
            log_pop = math.log10(max(10, pop))
            score = (pagerank[node] * 100) + log_pop
            
            rankings[node] = {
                "title": node,
                "pagerank": round(pagerank[node], 4),
                "in_degree": in_degree[node],
                "out_degree": out_degree[node],
                "year": meta.get("year", "N/A"),
                "population_size": pop,
                "evidence_score": round(score, 2)
            }
            
        return rankings
