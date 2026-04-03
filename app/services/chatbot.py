from app.services.rag import rag_engine
from app.services.eligibility import eligibility_engine
from app.services.recommendation import recommendation_engine
from app.utils.loader import loader
from app.models import SchemeResponse
import traceback

class ChatbotEngine:
    def chat_pipeline(self, user_query: str, scheme: dict = None, user_profile: dict = None):
        """
        Main entry point for the chatbot.
        Added robust error handling to prevent 500 errors.
        """
        try:
            # 🪵 Backend Logging for Debugging
            print(f"\n--- DEBUG CHAT PAYLOAD ---")
            print(f"Query: {user_query}")
            print(f"Scheme Context: {'Provided' if scheme else 'None'}")
            print(f"User Profile: {'Provided' if user_profile else 'None'}")
            print(f"---------------------------\n")

            if not user_query:
                return {"response": "Hi! I'm your AI Scheme Assistant. How can I help you today?", "schemes": []}

            # 🛠️ JURY MODE: Platform FAQ Layer (Hardcoded Expert Answers)
            query_l = user_query.lower()
            PLATFORM_FAQ = {
                "what is schemesense": "SchemeSense is an AI-powered platform designed to provide citizens and entrepreneurs with personalized, instant access to government schemes and startup grants. It uses fuzzy-eligibility matching and context-aware chat to bridge the knowledge gap between citizens and government resources.",
                "who built this": "SchemeSense was built by a dedicated team of engineers for the Hacknovate Hackathon. Our goal was to create a production-grade, winner-level solution for simplifying government scheme discovery.",
                "how it works": "Our AI engine uses a three-tier pipeline: (1) Discovery: keyword-based retrieval of relevant schemes, (2) Eligibility: fuzzy evaluation of user profiles against scheme rules, and (3) Chat: a context-aware assistant that answers specific questions about benefits, documents, and application steps.",
                "purpose of this": "The purpose is to simplify access to welfare and innovation programs, ensuring that no eligible citizen misses out on government support due to complex documentation or lack of awareness.",
                "contact": "You can reach the development team via our platform dashboard or GitHub repository for any technical queries.",
                "future": "We plan to expand our dataset, integrate voice commands in vernacular languages, and add a direct portal for application tracking in future versions."
            }

            for trigger, answer in PLATFORM_FAQ.items():
                if trigger in query_l:
                    return {"response": answer, "schemes": []}

            if scheme and isinstance(scheme, dict):
                # 🎯 Context-Aware Mode (Priority)
                return self.scheme_chat_agent(user_query, scheme, user_profile)
            
            # 🌐 General Discovery Mode
            return self.general_chat_agent(user_query, user_profile)

        except Exception as e:
            # 🛡️ Catch-all Error Guard to prevent 500
            error_trace = traceback.format_exc()
            print(f"CRITICAL CHATBOT ERROR: {str(e)}\n{error_trace}")
            return {
                "response": f"I encountered an internal error while processing your request: {str(e)}. Please try again or rephrase your question.",
                "schemes": [],
                "related_schemes": []
            }

    def scheme_chat_agent(self, query: str, scheme: dict, user_profile: dict = None):
        """
        Processes queries about a specific scheme with full null-safety guards.
        """
        query_l = query.lower()
        name = scheme.get("scheme_name", "this scheme")
        
        # A. Context Extraction with Null Safety
        benefits_obj = scheme.get("benefits")
        if not isinstance(benefits_obj, dict):
            benefits_obj = {}
        
        benefits_text = benefits_obj.get("description", "Not specified")
        if benefits_obj.get("amount"):
            benefits_text = f"{benefits_obj.get('amount')} - {benefits_text}"
            
        docs = scheme.get("documents_required", [])
        if not isinstance(docs, list):
            docs = []
        docs_text = ", ".join(docs) if docs else "standard identification documents"
        
        # Guard against empty target_beneficiary list
        target_list = scheme.get("target_beneficiary", ["citizens"])
        if not isinstance(target_list, list) or len(target_list) == 0:
            target_list = ["citizens"]
        target_group = target_list[0]
        
        # B. Intent Detection (Keyword-based)
        if any(w in query_l for w in ["eligib", "can i", "am i", "fit"]):
            # Eligibility Intent
            if user_profile and isinstance(user_profile, dict) and any(user_profile.values()):
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
            app_obj = scheme.get("application")
            if not isinstance(app_obj, dict):
                app_obj = {}
            modes = app_obj.get("mode", ["online"])
            mode_text = ", ".join(modes) if isinstance(modes, list) else "online"
            link = app_obj.get("link", "")
            response = f"You can apply for {name} via {mode_text}. "
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
        Uses RAG to find relevant schemes with strict confidence thresholds (Jury Mode).
        """
        query_l = query.lower()
        
        # 🟢 A. Direct Intent for Recommendations
        if any(w in query_l for w in ["suggest", "recommend", "find", "startup"]):
            if user_profile and isinstance(user_profile, dict) and any(user_profile.values()):
                results = recommendation_engine.get_recommendations(user_profile)
                valid = [r for r in results if r.scheme_name != "No Match Found"]
                if valid:
                    top = valid[0]
                    return {
                        "response": f"I've found some great schemes for you! My top recommendation is **{top.scheme_name}**. It provides {top.benefits}. Would you like to know more about it?",
                        "schemes": [s.model_dump() for s in valid]
                    }

        # 🟠 B. General Search with Hallucination Guard
        search_results = rag_engine.search(query, top_k=3)
        
        # JURY MODE: Only display results if they have a decent keyword match
        # Distance of 0.5 means a score of at least 1 keyword. Distance of 1.0 means score of 0.
        high_confidence = [r for r in search_results if r["distance"] < 0.6] 
        
        if not high_confidence:
             return {
                "response": "I apologize, but I don't have verified data on that specific query yet. My current knowledge base is focused on Indian government welfare schemes and startup grants. Please try asking about things like 'business loans' or 'scholarships'!",
                "schemes": []
            }
            
        found_schemes = []
        for res in high_confidence:
            s_data = next((s for s in loader.schemes if s.get("scheme_id") == res["id"]), None)
            if s_data: found_schemes.append(s_data)
            
        if found_schemes:
            s1 = found_schemes[0]
            name1 = s1.get("scheme_name")
            return {
                "response": f"I found some verified information about **{name1}** that might be relevant to you. Would you like to check the full details or your eligibility?",
                "schemes": found_schemes
            }
            
        return {
            "response": "I'm sorry, I couldn't find a high-confidence match for that right now. Please try rephrasing your question or search for a specific category like 'Education' or 'Finance'.",
            "schemes": []
        }

    def suggest_related_schemes(self, current_scheme: dict, all_schemes: list):
        """
        Finds schemes in the same category, excluding the current one with full null-safety.
        """
        if not isinstance(current_scheme, dict) or not isinstance(all_schemes, list):
            return []

        current_id = current_scheme.get("scheme_id")
        current_cats = current_scheme.get("scheme_category")
        if not isinstance(current_cats, list):
            current_cats = []
        categories = set(current_cats)
        
        related = []
        for scheme in all_schemes:
            if not isinstance(scheme, dict) or scheme.get("scheme_id") == current_id:
                continue
                
            scheme_cats_list = scheme.get("scheme_category")
            if not isinstance(scheme_cats_list, list):
                scheme_cats_list = []
            scheme_cats_set = set(scheme_cats_list)
            
            # Intersection of categories
            if categories & scheme_cats_set:
                # Store simplified version for UI
                related.append({
                    "scheme_id": scheme.get("scheme_id"),
                    "scheme_name": scheme.get("scheme_name"),
                    "category": list(scheme_cats_set)[0] if scheme_cats_set else "General"
                })
                
        # Return top 3 related
        return related[:3]

chatbot_engine = ChatbotEngine()
