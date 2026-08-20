from langgraph.graph import StateGraph, END
from app.graph.state import ResearchState
from app.agents.router import route_query
from app.agents.planner import plan_research
from app.agents.researcher import web_research
from app.agents.academic import academic_research
from app.agents.retriever import document_research
from app.agents.synthesizer import synthesize_answer
from app.agents.critic import critique_answer

def router_node(state: ResearchState):
    return route_query(state)

def plan_node(state: ResearchState):
    return plan_research(state)

def web_research_node(state: ResearchState):
    return web_research(state)

def academic_research_node(state: ResearchState):
    return academic_research(state)

def document_research_node(state: ResearchState):
    return document_research(state)

def synthesize_node(state: ResearchState):
    return synthesize_answer(state)

def should_route(state: ResearchState) -> str:
    """Decide next node based on intent."""
    intent = state.get("intent", "WEB")
    if intent == "SIMPLE":
        return "synthesize"
    elif intent == "WEB":
        return "web_research"
    elif intent == "ACADEMIC":
        return "academic_research"
    elif intent == "DOCUMENT":
        return "document_research"
    elif intent in ["RESEARCH", "MULTI_SOURCE"]:
        return "plan"
    return "web_research"

def execute_plan(state: ResearchState) -> str:
    """In a full implementation, this would spawn parallel tasks based on the plan. 
    For simplicity in this routing function, we just execute web research for now."""
    # A true parallel execution requires mapping nodes or a subgraph.
    # To keep it simple but demonstrate the multi-agent nature, we will 
    # route to web_research which will act as the executor for the plan.
    return "web_research"

def build_graph() -> StateGraph:
    workflow = StateGraph(ResearchState)
    
    # Add nodes
    workflow.add_node("router", router_node)
    workflow.add_node("plan", plan_node)
    workflow.add_node("web_research", web_research_node)
    workflow.add_node("academic_research", academic_research_node)
    workflow.add_node("document_research", document_research_node)
    workflow.add_node("synthesize", synthesize_node)
    
    workflow.add_node("critic", critique_answer)
    
    # Edges
    workflow.set_entry_point("router")
    
    workflow.add_conditional_edges(
        "router",
        should_route,
        {
            "synthesize": "synthesize",
            "web_research": "web_research",
            "academic_research": "academic_research",
            "document_research": "document_research",
            "plan": "plan"
        }
    )
    
    workflow.add_conditional_edges(
        "plan",
        execute_plan,
        {
            "web_research": "web_research"
            # Here we'd map to parallel researchers if we implemented subgraph mapping
        }
    )
    
    workflow.add_edge("web_research", "synthesize")
    workflow.add_edge("academic_research", "synthesize")
    workflow.add_edge("document_research", "synthesize")
    
    # After synthesize, go to critic
    workflow.add_edge("synthesize", "critic")
    
    # From critic, conditionally route
    def check_critique(state: ResearchState) -> str:
        if state.get("retry_count", 0) >= 2:
            return END
        critique = state.get("critique", {})
        if critique.get("required_revision", False):
            return "web_research" # simplistic revision path
        return END
        
    workflow.add_conditional_edges(
        "critic",
        check_critique,
        {
            END: END,
            "web_research": "web_research"
        }
    )
    
    return workflow.compile()
