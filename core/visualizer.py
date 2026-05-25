import os
import networkx as nx
from pyvis.network import Network
from typing import Dict, Any

class PyVisVisualizer:
    """Generates styled interactive network graphs in HTML format using PyVis with custom Dark Themes."""

    def __init__(self, bg_color: str = "#0f111a", font_color: str = "#e2e8f0"):
        self.bg_color = bg_color
        self.font_color = font_color

    def _get_node_color(self, is_root: bool, is_contemporary: bool, score: float) -> Dict[str, str]:
        """Returns standard visual styling states for a node (Dark-Indigo/Neon Theme)."""
        if is_contemporary:
            # Highlight Input/Contemporary Paper (Vibrant Teal/Cyan)
            return {
                "background": "#00f2fe",
                "border": "#4facfe",
                "highlight": {"background": "#38ef7d", "border": "#11998e"}
            }
        elif is_root:
            # Foundational parent paper (Deep neon orange/red)
            return {
                "background": "#ff0844",
                "border": "#ffb199",
                "highlight": {"background": "#f857a6", "border": "#ff5858"}
            }
        else:
            # Standard intermediate paper (Indigo/Lavender)
            return {
                "background": "#7f5af0",
                "border": "#2cb67d",
                "highlight": {"background": "#9c88ff", "border": "#2cb67d"}
            }

    def _create_html_tooltip(self, meta: Dict[str, Any]) -> str:
        """Constructs an elegant, CSS-styled HTML tooltip card for nodes."""
        title = meta.get("title", "Unknown Paper")
        authors = meta.get("authors", "Unknown Authors")
        journal = meta.get("journal", "Unknown Journal")
        year = meta.get("year", "N/A")
        citations = meta.get("citation_count", 0)
        pop_size = meta.get("population_size", "N/A")
        snippet = meta.get("cohort_extraction_snippet", "")
        rule = meta.get("cohort_matching_rule", "")
        confidence = meta.get("cohort_confidence", "UNKNOWN")

        # Format pop size
        if isinstance(pop_size, (int, float)):
            pop_display = f"{pop_size:,}"
        else:
            pop_display = str(pop_size)

        # Style colors for confidence badge
        badge_colors = {
            "HIGH": "background-color: #2e7d32; color: #ffffff;",
            "MEDIUM": "background-color: #f57f17; color: #ffffff;",
            "LOW": "background-color: #c62828; color: #ffffff;",
            "SIMULATED": "background-color: #1565c0; color: #ffffff;",
            "UNKNOWN": "background-color: #424242; color: #ffffff;"
        }
        badge_style = badge_colors.get(confidence, badge_colors["UNKNOWN"])

        tooltip_html = f"""
        <div style="
            background-color: #1a1e2e;
            color: #e2e8f0;
            border: 2px solid #3b4252;
            border-radius: 8px;
            padding: 12px;
            font-family: 'Inter', sans-serif;
            font-size: 13px;
            width: 280px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.5);
            line-height: 1.4;
        ">
            <h4 style="margin: 0 0 6px 0; color: #00f2fe; font-size: 14px; font-weight: 600;">{title}</h4>
            <div style="font-size: 11px; color: #a0aec0; margin-bottom: 8px;">{authors} ({year})</div>
            
            <div style="border-top: 1px solid #2d3748; padding-top: 6px; margin-top: 6px;">
                <span style="color: #cbd5e0; font-weight: 500;">Journal:</span> <span style="color: #e2e8f0;">{journal}</span>
            </div>
            <div>
                <span style="color: #cbd5e0; font-weight: 500;">Citations:</span> <span style="color: #00f2fe; font-weight: 600;">{citations:,}</span>
            </div>
            <div>
                <span style="color: #cbd5e0; font-weight: 500;">Cohort Size:</span> <span style="color: #38ef7d; font-weight: 600;">{pop_display}</span>
                <span style="font-size: 9px; padding: 2px 5px; border-radius: 4px; font-weight: 700; margin-left: 5px; {badge_style}">{confidence}</span>
            </div>
        """
        
        if snippet and len(snippet) > 10:
            tooltip_html += f"""
            <div style="border-top: 1px dashed #4a5568; padding-top: 6px; margin-top: 6px; font-style: italic; color: #cbd5e0; font-size: 11px;">
                <strong>Cohort Context:</strong> "{snippet[:100]}..."
            </div>
            """
        tooltip_html += "</div>"
        return tooltip_html

    def generate_graph_html(self, graph: nx.DiGraph, output_filename: str = "citation_graph.html"):
        """Compiles a fully-featured, dynamically configured PyVis physics network canvas."""
        # Initialize pyvis Network (directed DAG, dark bg)
        net = Network(height="650px", width="100%", bgcolor=self.bg_color, font_color=self.font_color, directed=True)
        
        # Determine root historical nodes (out-degree = 0) and contemporary papers (in-degree = 0)
        out_degrees = dict(graph.out_degree())
        in_degrees = dict(graph.in_degree())
        
        # Setup Nodes
        for node in graph.nodes():
            meta = graph.nodes[node]
            
            # Is root (cites nobody in local graph) vs contemporary
            is_root = out_degrees.get(node, 0) == 0
            is_contemporary = in_degrees.get(node, 0) == 0
            
            # Calculate dynamic sizing based on citation count (scaled log)
            citations = meta.get("citation_count", 0)
            node_size = 15 + min(25, int(math.log10(max(1, citations)) * 7))
            
            # Label truncation for visual clarity on canvas
            label = node
            if len(label) > 30:
                label = label[:28] + "..."
                
            colors = self._get_node_color(is_root, is_contemporary, meta.get("impact_factor", 1.0))
            tooltip = self._create_html_tooltip(meta)
            
            net.add_node(
                node,
                label=label,
                title=tooltip,
                size=node_size,
                color=colors,
                borderWidth=2,
                shape="dot",
                font={"size": 11, "color": "#e2e8f0"}
            )
            
        # Setup Edges
        # We scale edge thickness based on weight calculations
        for u, v in graph.edges():
            edge_meta = graph[u][v]
            weight = edge_meta.get("weight", 1.0)
            
            # Determine color strength of the edge based on weight
            # High-strength connections get glowing colors
            if weight > 8.0:
                edge_color = {"color": "#38ef7d", "highlight": "#00f2fe"}
                width = 5.0
            elif weight > 4.0:
                edge_color = {"color": "#4facfe", "highlight": "#7f5af0"}
                width = 3.0
            else:
                edge_color = {"color": "#4a5568", "highlight": "#a0aec0"}
                width = 1.5
                
            net.add_edge(
                u,
                v,
                width=width,
                color=edge_color,
                arrowStrikethrough=False,
                smooth={"type": "cubicBezier", "roundness": 0.3}
            )

        # Set physics engine parameters to ensure the graph settles beautifully and doesn't bounce endlessly
        net.set_options("""
        var options = {
          "physics": {
            "forceAtlas2Based": {
              "gravitationalConstant": -50,
              "centralGravity": 0.01,
              "springLength": 100,
              "springStrength": 0.08,
              "damping": 0.4
            },
            "solver": "forceAtlas2Based",
            "stabilization": {
              "enabled": true,
              "iterations": 100
            }
          },
          "interaction": {
            "hover": true,
            "navigationButtons": true,
            "keyboard": true
          }
        }
        """)

        # Save the graph
        net.write_html(output_filename)
