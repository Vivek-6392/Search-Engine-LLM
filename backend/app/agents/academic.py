from app.tools.tool_registry import get_tool_by_name
from app.graph.state import ResearchState
import json

def academic_research(state: ResearchState) -> ResearchState:
    """Executes academic research using the ArXiv tool."""
    tool = get_tool_by_name("arxiv")
    
    import time
    
    query = state.get("rewritten_query") or state["query"]
    
    for attempt in range(3):
        try:
            raw_results = tool.invoke(query)
            # ArXiv tool returns a string formatted with papers
            
            # We do a basic parsing of the ArXiv output string
            # Typically looks like: "Published: ...\nTitle: ...\nAuthors: ...\nSummary: ..."
            papers = raw_results.split("\n\n")
            
            evidence_list = []
            for paper in papers:
                if "Title:" in paper and "Summary:" in paper:
                    try:
                        title_line = [line for line in paper.split("\n") if line.startswith("Title:")][0]
                        title = title_line.replace("Title: ", "")
                        evidence_list.append({
                            "id": str(hash(title)),
                            "content": paper,
                            "source": "ArXiv",
                            "title": title,
                            "url": "",
                            "score": 1.0,
                            "source_type": "academic"
                        })
                    except Exception:
                        continue
                        
            return {"evidence": evidence_list}
            
        except Exception as e:
            print(f"Academic research error (attempt {attempt + 1}): {e}")
            if attempt < 2:
                time.sleep(1) # simple backoff
            else:
                return {"evidence": [{"id": "error", "content": f"Academic research failed after 3 attempts due to an internal error: {e}", "source": "System", "title": "Error Retrieving Evidence", "score": 0.0, "source_type": "error"}]}
                
    return {"evidence": []}
