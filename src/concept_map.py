import json
from pathlib import Path
import networkx as nx
import plotly.graph_objects as go

DATA_PATH = Path("data/concept_map.json")

def load_concept_map_data(path=DATA_PATH):
    """Load concept map JSON data."""
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def build_graph(data):
    """Build a NetworkX graph from node/edge data."""
    graph = nx.Graph()

    for node in data["nodes"]:
        graph.add_node(
            node["id"],
            label=node["label"],
            category=node["category"],
            description=node["description"],
            related_tools=node.get("related_tools", [])
        )

    for edge in data["edges"]:
        graph.add_edge(
            edge["source"],
            edge["target"],
            relationship=edge.get("relationship", "")
        )

    return graph


def get_node_color(category):
    """Return a colour based on node category."""
    color_map = {
        "core": "#1f77b4",
        "topic": "#2ca02c",
        "subtopic": "#ff7f0e"
    }
    return color_map.get(category, "#7f7f7f")


def create_plotly_figure(graph):
    """Create a Plotly network figure from the graph."""
    pos = nx.spring_layout(
    graph,
    seed=42,
    k=1.8,
    iterations=200,
    center=(0, 0)
    )
    
    for node, attrs in graph.nodes(data=True):
        if attrs.get("category") == "core":
            pos[node] = (0, 0)

    edge_x = []
    edge_y = []

    for source, target in graph.edges():
        x0, y0 = pos[source]
        x1, y1 = pos[target]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])

    edge_trace = go.Scatter(
        x=edge_x,
        y=edge_y,
        mode="lines",
        hoverinfo="none",
        line=dict(width=1.5, color="#B0B0B0")
    )

    node_x = []
    node_y = []
    node_text = []
    node_labels = []
    node_colors = []
    node_sizes = []

    for node_id, attrs in graph.nodes(data=True):
        x, y = pos[node_id]
        node_x.append(x)
        node_y.append(y)
        node_labels.append(attrs["label"])

        hover_text = (
            f"<b>{attrs['label']}</b><br>"
            f"Category: {attrs['category'].title()}<br>"
            f"{attrs['description']}"
        )
        node_text.append(hover_text)

        node_colors.append(get_node_color(attrs["category"]))

        if attrs["category"] == "core":
            node_sizes.append(43)
        elif attrs["category"] == "topic":
            node_sizes.append(31)
        else:
            node_sizes.append(23)

    node_trace = go.Scatter(
        x=node_x,
        y=node_y,
        mode="markers+text",
        text=node_labels,
        textposition="top center",
        hoverinfo="text",
        hovertext=node_text,
        marker=dict(
            size=node_sizes,
            color=node_colors,
            line=dict(width=2, color="white")
        )
    )

    fig = go.Figure(data=[edge_trace, node_trace])

    fig.update_layout(
        title="COMP201 Concept Map",
        title_x=0.5,
        showlegend=False,
        hovermode="closest",
        margin=dict(l=0, r=0, t=60, b=0),
        height=750,
        xaxis=dict(showgrid=False, zeroline=False, visible=False),
        yaxis=dict(showgrid=False, zeroline=False, visible=False),
        plot_bgcolor="white",
        paper_bgcolor="white"
    )

    return fig


def get_topic_lookup(data):
    """Return a dictionary keyed by node id."""
    return {node["id"]: node for node in data["nodes"]}


def get_topic_options(data):
    """Return topic options for Streamlit selectbox."""
    return {
        node["label"]: node["id"]
        for node in data["nodes"]
    }