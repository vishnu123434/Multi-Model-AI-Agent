from typing import TypedDict, Optional

from langgraph.graph import StateGraph, END

# -------------------------------
# Import Agents
# -------------------------------

from agents.query_normalizer import query_normalizer
from agents.planner import planner
from agents.router import router
from agents.web_agent import web_agent
from agents.currency_agent import currency_agent
from agents.ocr_agent import ocr_agent
from agents.image_agent import image_agent
from agents.response_agent import response_agent
from agents.image_analysis_agent import image_analysis_agent

# -------------------------------
# Workflow State
# -------------------------------

class AgentState(TypedDict):

    query: str

    intent: str

    tool: str

    amount: Optional[float]

    from_currency: Optional[str]

    to_currency: Optional[str]

    file_path: Optional[str]

    forced_tool: Optional[str]

    tool_output: Optional[str]

    response: Optional[str]

    success: bool

    error: Optional[str]

    history: list


# -------------------------------
# Create Graph
# -------------------------------

workflow = StateGraph(AgentState)


# -------------------------------
# Nodes
# -------------------------------

workflow.add_node("query_normalizer", query_normalizer)

workflow.add_node("planner", planner)

workflow.add_node("router", router)

workflow.add_node("web_agent", web_agent)

workflow.add_node("currency_agent", currency_agent)

workflow.add_node("ocr_agent", ocr_agent)

workflow.add_node("image_agent", image_agent)

workflow.add_node("image_analysis_agent", image_analysis_agent)

workflow.add_node("response_agent", response_agent)


# -------------------------------
# Router Function
# -------------------------------

def route_tool(state):
    return state["tool"]


# -------------------------------
# Edges
# -------------------------------

workflow.set_entry_point("query_normalizer")

workflow.add_edge("query_normalizer", "planner")

workflow.add_edge("planner", "router")

workflow.add_conditional_edges(
    "router",
    route_tool,
    {
    "web": "web_agent",
    "currency": "currency_agent",
    "ocr": "ocr_agent",
    "image": "image_agent",
    "image_analysis": "image_analysis_agent",
}
)

workflow.add_edge("web_agent", "response_agent")

workflow.add_edge("currency_agent", "response_agent")

workflow.add_edge("ocr_agent", "response_agent")

workflow.add_edge("image_agent", "response_agent")

workflow.add_edge("image_analysis_agent", "response_agent")

workflow.add_edge("response_agent", END)


# -------------------------------
# Compile
# -------------------------------

app = workflow.compile()