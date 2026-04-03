"""
Eligibility Agent
What it does: Filters retrieved schemes based on user eligibility criteria.
Input: State dict with retrieved_schemes and user_input.
Output: State dict updated with eligible_schemes.
"""
from state import State

def eligibility_agent(state: State) -> dict:
    retrieved_schemes = state.get("retrieved_schemes", [])
    
    # Mock eligibility check: accept all retrieved schemes for now
    eligible_schemes = retrieved_schemes
    
    return {"eligible_schemes": eligible_schemes}
