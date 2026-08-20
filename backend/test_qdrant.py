import asyncio
from app.retrieval.vector_store import get_vector_store
from qdrant_client.http import models as rest

async def test_search():
    try:
        vs = get_vector_store("deepsearch_documents")
        
        # Search with models.Filter
        print("Searching with models.Filter...")
        
        filter_obj = rest.Filter(
            must=[
                rest.FieldCondition(
                    key="metadata.user_id",
                    match=rest.MatchValue(value="123")
                )
            ]
        )
        
        try:
            results = vs.similarity_search("test", k=1, filter=filter_obj)
            print(f"Results Filter: {len(results)}")
        except Exception as e:
            print(f"Filter error: {e}")
            
    except Exception as e:
        print(f"General error: {e}")

if __name__ == "__main__":
    asyncio.run(test_search())
