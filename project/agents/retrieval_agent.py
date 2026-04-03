"""
Retrieval Agent
What it does: Searches the dataset for schemes relevant to the user_input.
Input: State dict with user_input.
Output: State dict updated with retrieved_schemes.
"""
from state import State
from dataset import load_schemes

def retrieval_agent(state: State) -> dict:
    user_input = state.get("user_input", "").lower()
    schemes = load_schemes()
    
    # Mock retrieval logic: keeping it simple
    retrieved_schemes = schemes[:5] # Just take the first 5 for the demo
    
    return {"retrieved_schemes": retrieved_schemes}
