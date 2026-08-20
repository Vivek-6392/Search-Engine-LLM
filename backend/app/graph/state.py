from typing import TypedDict, List, Dict, Any, Optional
import operator
from typing_extensions import Annotated

class ResearchState(TypedDict):
    """
    Represents the state of the multi-agent research workflow.
    """
    query: str
    rewritten_query: Optional[str]
    intent: Optional[str] # SIMPLE, WEB, ACADEMIC, DOCUMENT, RESEARCH, MULTI_SOURCE, FOLLOW_UP
    plan: Optional[List[Dict[str, Any]]] # List of subtasks
    
    # Using Annotated with operator.add to append items instead of overwriting
    search_results: Annotated[List[Dict[str, Any]], operator.add]
    evidence: Annotated[List[Dict[str, Any]], operator.add]
    retrieved_chunks: Annotated[List[Dict[str, Any]], operator.add]
    
    draft_answer: Optional[str]
    citations: Optional[List[Dict[str, Any]]]
    critique: Optional[Dict[str, Any]]
    final_answer: Optional[str]
    
    retry_count: int
    user_id: Optional[str]
    conversation_id: Optional[str]
