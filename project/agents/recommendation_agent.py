"""
Recommendation Agent
What it does: Formats the final recommendations based on eligible schemes and policy analysis.
Input: State dict with eligible_schemes and policy_analysis.
Output: State dict updated with recommendations.
"""
from state import State

def recommendation_agent(state: State) -> dict:
    eligible_schemes = state.get("eligible_schemes", [])
    
    # Create final recommendation structure
    recommendations = eligible_schemes
    
    return {"recommendations": recommendations}
