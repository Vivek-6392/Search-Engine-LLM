from langchain_core.tools import BaseTool
from langchain_community.tools import ArxivQueryRun
from langchain_community.utilities import ArxivAPIWrapper

def get_arxiv_tool() -> BaseTool:
    return ArxivQueryRun(
        api_wrapper=ArxivAPIWrapper(top_k_results=3, doc_content_chars_max=2000),
        name="arxiv",
        description="Use this tool to search ArXiv for academic papers, research, and scientific literature."
    )
