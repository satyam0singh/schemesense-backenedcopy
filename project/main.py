from graph import app

def main():
    print("Welcome to SchemeSense – AI Government Scheme Navigator")
    print("-" * 50)
    
    sample_user_input = "I am a small business owner looking for a loan"
    print(f"Sample User Input: '{sample_user_input}'\n")
    
    # Initial state
    initial_state = {
        "user_input": sample_user_input,
        "retrieved_schemes": [],
        "eligible_schemes": [],
        "policy_analysis": "",
        "recommendations": []
    }
    
    # Call the graph
    print("Running multi-agent workflow...")
    final_state = app.invoke(initial_state)
    print("-" * 50)
    
    # Print final recommendations
    print("Policy Analysis:")
    print(final_state.get("policy_analysis", ""))
    print("\nFinal Recommendations:")
    recommendations = final_state.get("recommendations", [])
    if not recommendations:
        print("No recommendations found.")
    else:
        for idx, rec in enumerate(recommendations, 1):
            # Try to get 'name' or fallback to a string representation
            name = rec.get("scheme_name") or rec.get("name") if isinstance(rec, dict) else str(rec)
            print(f"{idx}. {name}")

if __name__ == "__main__":
    main()
