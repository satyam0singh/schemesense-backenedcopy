from langgraph.graph import StateGraph, END
from state import State
from agents.retrieval_agent import retrieval_agent
from agents.eligibility_agent import eligibility_agent
from agents.policy_agent import policy_agent
from agents.recommendation_agent import recommendation_agent

def create_graph():
    # Define StateGraph
    workflow = StateGraph(State)
    
    # Add nodes (agents)
    workflow.add_node("retrieval", retrieval_agent)
    workflow.add_node("eligibility", eligibility_agent)
    workflow.add_node("policy", policy_agent)
    workflow.add_node("recommendation", recommendation_agent)
    
    # Connect nodes in correct order
    workflow.set_entry_point("retrieval")
    workflow.add_edge("retrieval", "eligibility")
    workflow.add_edge("eligibility", "policy")
    workflow.add_edge("policy", "recommendation")
    workflow.add_edge("recommendation", END)
    
    # Compile and expose the graph
    app = workflow.compile()
    return app

app = create_graph()
