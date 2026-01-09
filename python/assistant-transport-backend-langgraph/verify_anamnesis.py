
import asyncio
import sys
import os

# Add the directory to the path so we can import the module
sys.path.append("/home/zath/Documents/GitHub/Tilly-assist-UI/python/assistant-transport-backend-langgraph")

from anamnesis.engine import AnamnesisEngine

async def test_engine():
    print("Testing Anamnesis Engine...")
    engine = AnamnesisEngine() 
    
    # Initialize (should log warning about missing transformers but continue)
    await engine.initialize()
    
    # Test unforgetting
    query = "Who are you?"
    print(f"Querying: {query}")
    response = await engine.unforget(query)
    print(f"Response: {response}")
    
    if "Resonance Simulation" in response or "Truth" in response:
        print("✅ Anamnesis Engine responding correctly.")
    else:
        print("❌ Unexpected response format.")

if __name__ == "__main__":
    asyncio.run(test_engine())
