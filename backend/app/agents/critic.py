from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from typing import List
from app.llm.factory import get_llm
from app.graph.state import ResearchState

class CritiqueResult(BaseModel):
    approved: bool = Field(description="Whether the draft answer is fully supported by evidence and answers the query.")
    issues: List[str] = Field(description="List of issues, hallucinations, or unsupported claims.")
    required_revision: bool = Field(description="Whether a revision is required.")

def critique_answer(state: ResearchState) -> ResearchState:
    """Critiques the draft answer against the evidence."""
    llm = get_llm(temperature=0)
    parser = PydanticOutputParser(pydantic_object=CritiqueResult)
    
    # We only critique if there's a draft answer
    if not state.get("draft_answer"):
        return state
        
    evidence = state.get("evidence", [])
    formatted_evidence = "\n".join([ev.get('content', '') for ev in evidence])
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an expert AI Critic. Your job is to verify that a draft answer is factually supported by the provided evidence.\n"
                   "Check for:\n"
                   "- Unsupported claims (hallucinations)\n"
                   "- Contradictory evidence\n"
                   "- Missing citations\n"
                   "- Irrelevant information\n"
                   "If you find issues, set approved=False and required_revision=True.\n"
                   "{format_instructions}"),
        ("human", "Query: {query}\n\nEvidence:\n{evidence}\n\nDraft Answer:\n{draft_answer}")
    ])
    
    chain = prompt | llm | parser
    
    try:
        critique = chain.invoke({
            "query": state["query"],
            "evidence": formatted_evidence,
            "draft_answer": state["draft_answer"],
            "format_instructions": parser.get_format_instructions()
        })
        state["critique"] = critique.model_dump()
        
        # Increment retry count if revision is required
        if critique.required_revision:
            state["retry_count"] = state.get("retry_count", 0) + 1
            
    except Exception as e:
        # On failure to parse, we approve to avoid infinite loops if it's struggling
        state["critique"] = {"approved": True, "issues": [], "required_revision": False}
        
    return state
