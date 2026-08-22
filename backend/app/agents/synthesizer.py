from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from app.llm.factory import get_llm
from app.graph.state import ResearchState
import json

def synthesize_answer(state: ResearchState) -> ResearchState:
    """Synthesizes the final answer using retrieved evidence and generates citations."""
    llm = get_llm(temperature=0.2, streaming=True)
    parser = StrOutputParser()
    
    query = state["query"]
    evidence = state.get("evidence", [])
    
    # Format evidence for the prompt, truncate to avoid context limits
    formatted_evidence = ""
    if evidence:
        for i, ev in enumerate(evidence, start=1):
            formatted_evidence += f"[{i}] Source: {ev.get('title', ev.get('source', 'Unknown'))}\n"
            formatted_evidence += f"Content: {ev.get('content', '')}\n\n"
        # Truncate evidence string to around 4000 chars to avoid 413 Payload Too Large on Groq Qwen
        formatted_evidence = formatted_evidence[:4000]
        
        system_msg = ("You are an expert AI researcher. Answer the user's question based ONLY on the provided evidence.\n"
                      "You MUST cite your sources using inline brackets, e.g., [1], [2].\n"
                      "At the end of your answer, provide a 'Sources' section listing the references used.\n"
                      "If the evidence does not contain the answer, state that you do not have enough information.\n\n"
                      "EVIDENCE:\n{evidence}")
    else:
        formatted_evidence = "No evidence retrieved."
        system_msg = ("You are a helpful AI assistant. Answer the user's question to the best of your ability "
                      "using your general knowledge since no specific research evidence was required or retrieved.")
        
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_msg),
        ("human", "{query}")
    ])
    
    chain = prompt | llm | parser
    
    try:
        final_answer = chain.invoke({
            "query": query,
            "evidence": formatted_evidence
        })
        
        # Clean up output if it contains <think> tags from reasoning models
        import re
        if isinstance(final_answer, str):
            final_answer = re.sub(r'<think>.*?(?:</think>|$)', '', final_answer, flags=re.DOTALL).strip()
            
        return {"final_answer": final_answer, "citations": evidence}
    except Exception as e:
        import traceback
        traceback.print_exc()  # This will appear in docker compose logs
        return {"final_answer": f"Error in synthesizer: {type(e).__name__}: {str(e)}"}
