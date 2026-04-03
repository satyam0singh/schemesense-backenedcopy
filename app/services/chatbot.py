from app.services.rag import rag_engine
from app.services.eligibility import eligibility_engine
from app.services.recommendation import recommendation_engine
from app.utils.loader import loader
from app.models import SchemeResponse

class ChatbotEngine:
    def chat_pipeline(self, user_query: str, scheme: dict = None, user_profile: dict = None):
        """
        Main entry point for the chatbot.
        Logic: If a specific scheme context is provided, run scheme_chat_agent.
        Otherwise, fallback to a general discovery assistant.
        """
        if not user_query:
            return {"response": "Hi! I'm your AI Scheme Assistant. How can I help you today?", "schemes": []}

        if scheme:
            # 🎯 Context-Aware Mode (Priority)
            return self.scheme_chat_agent(user_query, scheme, user_profile)
        
        # 🌐 General Discovery Mode
        return self.general_chat_agent(user_query, user_profile)

    def scheme_chat_agent(self, query: str, scheme: dict, user_profile: dict = None):
        """
        Processes queries about a specific scheme currently being viewed by the user.
        """
        query_l = query.lower()
        name = scheme.get("scheme_name", "this scheme")
        
        # A. Context Extraction
        benefits_obj = scheme.get("benefits", {})
        benefits_text = benefits_obj.get("description", "Not specified")
        if benefits_obj.get("amount"):
            benefits_text = f"{benefits_obj.get('amount')} - {benefits_text}"
            
        docs = scheme.get("documents_required", [])
        docs_text = ", ".join(docs) if docs else "standard identification documents"
        
        target_group = scheme.get("target_beneficiary", ["citizens"])[0]
        
        # B. Intent Detection (Keyword-based)
        if any(w in query_l for w in ["eligib", "can i", "am i", "fit"]):
            # Eligibility Intent
            if user_profile and any(user_profile.values()):
                is_el, conf, reason, match_type = eligibility_engine.evaluate(user_profile, scheme)
                if is_el:
                    response = f"Based on your profile, you appear to be a **{match_type.lower()} match** for {name}. {reason.split('.')[0]}."
                else:
                    response = f"Reviewing the requirements, you might not be eligible for {name} right now. {reason.split('.')[0]}."
            else:
                response = f"To check your eligibility for {name}, I need to know your age, income, and occupation. Generally, it targets {target_group}."
        
        elif any(w in query_l for w in ["document", "requir", "paper", "need"]):
            # Documents Intent
            response = f"To apply for **{name}**, you will typically need: {docs_text}. Make sure to have your Aadhaar card ready!"
            
        elif any(w in query_l for w in ["benefit", "get", "money", "amount", "help"]):
            # Benefits Intent
            response = f"**{name}** provides the following support: {benefits_text}. It's a great program for {target_group}."
            
        elif any(w in query_l for w in ["apply", "how to", "process", "register"]):
            # Application Intent
            mode = ", ".join(scheme.get("application", {}).get("mode", ["online"]))
            link = scheme.get("application", {}).get("link", "")
            response = f"You can apply for {name} via {mode}. "
            if link:
                response += f"The official link is {link}. I recommend checking the portal for the latest steps."
            else:
                response += "I recommend visiting your nearest CSC center for assistance."
        
        else:
            # General Explanation
            response = f"**{name}** is a {scheme.get('government_level', 'government')} scheme managed by the {scheme.get('ministry', 'relevant ministry')}. It aims to help {target_group} by providing {benefits_text}."

        # C. Related Suggestions
        related = self.suggest_related_schemes(scheme, loader.schemes)
        
        return {
            "response": response,
            "related_schemes": related
        }

    def general_chat_agent(self, query: str, user_profile: dict = None):
        """
        Fallback logic for when no specific scheme is in focus.
        Uses RAG to find relevant schemes.
        """
        query_l = query.lower()
        
        # Basic intent for general mode
        if "suggest" in query_l or "recommend" in query_l or "find" in query_l:
            if user_profile and any(user_profile.values()):
                results = recommendation_engine.get_recommendations(user_profile)
                # Filter out fallback
                valid = [r for r in results if r.scheme_name != "No Match Found"]
                if valid:
                    top = valid[0]
                    return {
                        "response": f"I've found some great schemes for you! My top recommendation is **{top.scheme_name}**. It provides {top.benefits}. Would you like to know more about it?",
                        "schemes": [s.model_dump() for s in valid]
                    }
            
        # Default RAG search
        search_results = rag_engine.search(query, top_k=2)
        if not search_results:
            return {"response": "I'm sorry, I couldn't find any schemes related to your query. Could you try rephrasing? For example, ask about 'schemes for farmers'.", "schemes": []}
            
        found_schemes = []
        for res in search_results:
            s_data = next((s for s in loader.schemes if s.get("scheme_id") == res["id"]), None)
            if s_data: found_schemes.append(s_data)
            
        if found_schemes:
            s1 = found_schemes[0]
            name1 = s1.get("scheme_name")
            return {
                "response": f"I found some information about **{name1}** that might interest you. Would you like to check if you're eligible for it?",
                "schemes": found_schemes
            }
            
        return {"response": "I'm having trouble retrieving details right now. Please try again.", "schemes": []}

    def suggest_related_schemes(self, current_scheme: dict, all_schemes: list):
        """
        Finds schemes in the same category, excluding the current one.
        """
        current_id = current_scheme.get("scheme_id")
        categories = set(current_scheme.get("scheme_category", []))
        
        related = []
        for scheme in all_schemes:
            if scheme.get("scheme_id") == current_id:
                continue
                
            scheme_cats = set(scheme.get("scheme_category", []))
            # Intersection of categories
            if categories & scheme_cats:
                # Store simplified version for UI
                related.append({
                    "scheme_id": scheme.get("scheme_id"),
                    "scheme_name": scheme.get("scheme_name"),
                    "category": list(scheme_cats)[0] if scheme_cats else "General"
                })
                
        # Return top 3 related
        return related[:3]

chatbot_engine = ChatbotEngine()
