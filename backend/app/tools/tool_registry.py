from typing import List
from langchain_core.tools import BaseTool
from app.config import settings

# Import wrapped tools
from app.tools.web_search import get_web_search_tool
from app.tools.wikipedia import get_wikipedia_tool
from app.tools.arxiv import get_arxiv_tool

def get_all_tools() -> List[BaseTool]:
    """Returns all available tools based on configuration."""
    tools = []
    
    # Web search tool (Tavily if key exists, else DuckDuckGo)
    tools.append(get_web_search_tool())
    
    # Wikipedia
    tools.append(get_wikipedia_tool())
    
    # ArXiv
    tools.append(get_arxiv_tool())
    
    return tools

def get_tool_by_name(name: str) -> BaseTool:
    tools = get_all_tools()
    for tool in tools:
        if tool.name == name:
            return tool
    raise ValueError(f"Tool {name} not found")
