import asyncio
import httpx
import json

BASE_URL = "http://localhost:8000/api/v1"

async def main():
    async with httpx.AsyncClient() as client:
        print("1. Registering/Logging in...")
        # Try to login first
        response = await client.post(f"{BASE_URL}/auth/login", data={"username": "testuser2@example.com", "password": "password123"})
        
        if response.status_code == 401:
            print("User doesn't exist, registering...")
            response = await client.post(f"{BASE_URL}/auth/register", json={"email": "testuser2@example.com", "password": "password123"})
            response = await client.post(f"{BASE_URL}/auth/login", data={"username": "testuser2@example.com", "password": "password123"})
            
        token = response.json().get("access_token")
        headers = {"Authorization": f"Bearer {token}"}
        
        questions = [
            "What is the capital of France?",
            "Who won the 2022 FIFA World Cup?",
            "Explain quantum computing simply.",
            "What is the current stock price of Apple?",
            "How does photosynthesis work?"
        ]
        
        for i, q in enumerate(questions):
            print(f"\n--- Question {i+1}: {q} ---")
            
            # Start streaming chat
            async with client.stream("POST", f"{BASE_URL}/chat", json={"query": q, "stream": True}, headers=headers, timeout=60.0) as stream:
                async for line in stream.aiter_lines():
                    if line.startswith("data: "):
                        data_str = line[6:]
                        if data_str == "[DONE]":
                            break
                        try:
                            data = json.loads(data_str)
                            if data.get("event") == "final_answer":
                                print(f"Answer: {data.get('content')[:100]}...")
                            elif data.get("event") == "error":
                                print(f"ERROR: {data.get('content')}")
                        except Exception as e:
                            print(f"Failed to parse line: {line} - {e}")

if __name__ == "__main__":
    asyncio.run(main())
