from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from typing import List
from app.llm.factory import get_llm
from app.graph.state import ResearchState

class SubTask(BaseModel):
    id: int = Field(description="Unique ID for the subtask")
    question: str = Field(description="The specific question to research")
    source: str = Field(description="The required source type: 'web', 'academic', or 'document'")

class ResearchPlan(BaseModel):
    goal: str = Field(description="The overall research goal")
    subtasks: List[SubTask] = Field(description="List of subtasks to execute in parallel")

def plan_research(state: ResearchState) -> ResearchState:
    """Creates a structured research plan for complex queries."""
    llm = get_llm(temperature=0)
    parser = PydanticOutputParser(pydantic_object=ResearchPlan)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an expert AI research planner. Break down the user's complex query into a structured research plan. "
                   "Determine if each subtask requires 'web', 'academic', or 'document' search.\n"
                   "{format_instructions}"),
        ("human", "{query}")
    ])
    
    chain = prompt | llm | parser
    
    try:
        query_to_plan = state.get("rewritten_query") or state["query"]
        plan = chain.invoke({
            "query": query_to_plan, 
            "format_instructions": parser.get_format_instructions()
        })
        state["plan"] = [subtask.model_dump() for subtask in plan.subtasks]
    except Exception as e:
        # Fallback single plan
        state["plan"] = [{"id": 1, "question": state["query"], "source": "web"}]
        
    return state
