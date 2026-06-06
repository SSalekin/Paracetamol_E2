from langgraph.graph import END, START, StateGraph

from backend.app.core.graph_nodes import (
    extractor_node,
    agents_node,
    aggregator_node,
)
from backend.app.schemas.graph_state import VideoScoreGraphState


def create_viral_score_graph():
    graph = StateGraph(VideoScoreGraphState)

    graph.add_node("extractor", extractor_node)
    graph.add_node("agents", agents_node)
    graph.add_node("aggregator", aggregator_node)

    graph.add_edge(START, "extractor")
    graph.add_edge("extractor", "agents")
    graph.add_edge("agents", "aggregator")
    graph.add_edge("aggregator", END)

    return graph.compile()


viral_score_graph = create_viral_score_graph()
