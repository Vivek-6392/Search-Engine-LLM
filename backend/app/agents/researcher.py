from langchain_core.prompts import ChatPromptTemplate
from app.llm.factory import get_llm
from app.tools.tool_registry import get_tool_by_name
from app.graph.state import ResearchState
import json

def web_research(state: ResearchState) -> ResearchState:
    """Executes web research using the web search tool."""
    tool = get_tool_by_name("web_search")
    
    # Simple research flow: just invoke the tool with the query. 
    # For a more advanced agent, we'd use an AgentExecutor, but for this step
    # we just want to retrieve raw evidence and format it.
    
    query = state.get("rewritten_query") or state["query"]
    
    try:
        raw_results = tool.invoke(query)
        # Handle Tavily or DuckDuckGo output formats
        if isinstance(raw_results, list):
            results = raw_results
        elif isinstance(raw_results, str):
            try:
                results = json.loads(raw_results)
            except:
                results = [{"content": raw_results, "url": "", "title": "Web Search"}]
        else:
            results = []
            
        evidence_list = []
        for res in results:
            content = res.get("content", res.get("snippet", ""))
            url = res.get("url", "")
            title = res.get("title", "")
            if content:
                evidence_list.append({
                    "id": str(hash(url + title)),
                    "content": content,
                    "source": url,
                    "title": title,
                    "url": url,
                    "score": 1.0,
                    "source_type": "web"
                })
        
        # We append to evidence using the operator.add defined in State
        return {"evidence": evidence_list}
        
    except Exception as e:
        print(f"Web research error: {e}")
        return {"evidence": []}
