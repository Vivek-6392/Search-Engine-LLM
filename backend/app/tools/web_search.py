from langchain_core.tools import BaseTool
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_community.tools import DuckDuckGoSearchResults
from app.config import settings

def get_web_search_tool() -> BaseTool:
    if settings.TAVILY_API_KEY:
        return TavilySearchResults(
            tavily_api_key=settings.TAVILY_API_KEY,
            max_results=3,
            name="web_search",
            description="Use this tool to search the web for current events, facts, or general knowledge."
        )
    else:
        # Fallback to DuckDuckGo
        return DuckDuckGoSearchResults(
            num_results=3,
            name="web_search",
            description="Use this tool to search the web for current events, facts, or general knowledge."
        )
