"""
Policy Interpretation Agent
What it does: Simulates an LLM analyzing the eligible schemes to provide simple policy insights.
Input: State dict with eligible_schemes.
Output: State dict updated with policy_analysis.
"""
from state import State

def policy_agent(state: State) -> dict:
    eligible_schemes = state.get("eligible_schemes", [])
    
    # Mock LLM interpretation
    analysis = f"Based on the policies analyzed, {len(eligible_schemes)} schemes are highly relevant."
    
    return {"policy_analysis": analysis}
