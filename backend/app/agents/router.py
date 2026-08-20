from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from app.llm.factory import get_llm
from app.graph.state import ResearchState
import json

class RouteDecision(BaseModel):
    intent: str = Field(description="The classified intent of the user query. Must be one of: SIMPLE, WEB, ACADEMIC, DOCUMENT, RESEARCH, MULTI_SOURCE, FOLLOW_UP")
    rewritten_query: str = Field(description="The query rewritten for optimal search and processing.")

def route_query(state: ResearchState) -> ResearchState:
    """Classifies the query intent and rewrites it."""
    llm = get_llm(temperature=0)
    parser = PydanticOutputParser(pydantic_object=RouteDecision)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an expert query router. Classify the user query into one of the following intents:\n"
                   "- SIMPLE: Factual questions that can be answered without tools.\n"
                   "- WEB: Questions requiring current web search.\n"
                   "- ACADEMIC: Questions requiring academic papers (ArXiv).\n"
                   "- DOCUMENT: Questions specifically about user's uploaded documents.\n"
                   "- RESEARCH: Complex questions requiring multi-step planning.\n"
                   "- MULTI_SOURCE: Questions requiring a mix of web and academic sources.\n"
                   "- FOLLOW_UP: A conversational follow-up to previous context.\n\n"
                   "Also, rewrite the query to make it a standalone search query if necessary.\n"
                   "{format_instructions}"),
        ("human", "{query}")
    ])
    
    chain = prompt | llm | parser
    
    try:
        raw_response = chain.invoke({
            "query": state["query"], 
            "format_instructions": parser.get_format_instructions()
        })
        
        # If the model is an open-source reasoning model (like Qwen), it might output <think>...</think>
        # Let's extract only the JSON part from raw_response (assuming chain output is string or object)
        import re
        if isinstance(raw_response, str):
            # Try to strip <think> blocks
            text = re.sub(r'<think>.*?</think>', '', raw_response, flags=re.DOTALL).strip()
            # Try to extract JSON from markdown blocks
            json_match = re.search(r'```(?:json)?(.*?)```', text, re.DOTALL)
            if json_match:
                text = json_match.group(1).strip()
            parsed_data = json.loads(text)
            state["intent"] = parsed_data.get("intent", "WEB")
            state["rewritten_query"] = parsed_data.get("rewritten_query", state["query"])
        else:
            state["intent"] = getattr(raw_response, 'intent', "WEB")
            state["rewritten_query"] = getattr(raw_response, 'rewritten_query', state["query"])
    except Exception as e:
        # Fallback
        state["intent"] = "WEB"
        state["rewritten_query"] = state["query"]
        
    return state
