from langchain_core.tools import BaseTool
from langchain_community.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper

def get_wikipedia_tool() -> BaseTool:
    return WikipediaQueryRun(
        api_wrapper=WikipediaAPIWrapper(top_k_results=3, doc_content_chars_max=1000),
        name="wikipedia",
        description="Use this tool to search Wikipedia for established facts, historical events, and general knowledge."
    )
