from typing import TypedDict, List, Dict, Any

class State(TypedDict):
    user_input: str
    retrieved_schemes: List[Dict[str, Any]]
    eligible_schemes: List[Dict[str, Any]]
    policy_analysis: str
    recommendations: List[Dict[str, Any]]
