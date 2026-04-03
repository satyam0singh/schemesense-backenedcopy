from app.services.rag import rag_engine
from app.services.eligibility import eligibility_engine
from app.utils.loader import loader
from app.models import SchemeResponse

class RecommendationEngine:
    @staticmethod
    def get_recommendations(user_data: dict, raw_user_req: dict = None):
        """
        Intelligent Recommendation Workflow
        """
        # Logging constraint as requested 
        print(f"User input processed: {raw_user_req}")
        
        schemes = loader.schemes
        if not schemes:
            return RecommendationEngine._get_empty_fallback()
            
        # 1. Convert to query string based on user profile
        query_parts = []
        if user_data.get("occupation"):
            query_parts.append(user_data["occupation"])
        if user_data.get("gender"):
            query_parts.append(user_data["gender"])
        if user_data.get("state"):
            query_parts.append(f"{user_data['state']}")
        if user_data.get("startup_stage"):
            query_parts.append(user_data["startup_stage"])
        if user_data.get("startup_recognition"):
            query_parts.append(user_data["startup_recognition"])
        
        query_string = " ".join(query_parts) if query_parts else "general support schemes"
        
        # 2. RAG (FAISS search)
        faiss_results = rag_engine.search(query_string, top_k=20)
        faiss_scheme_ids = {res["id"]: res["distance"] for res in faiss_results}
        
        recommended = []
        
        for scheme in schemes:
            if scheme.get("scheme_id") not in faiss_scheme_ids:
                continue
                
            # 3. Fuzzy Eligibility Filter
            is_eligible, confidence_score, match_reason, match_type = eligibility_engine.evaluate(user_data, scheme)
            
            # Discard anything < 50% match
            if not is_eligible:
                continue
                
            # 4. Final Scoring Equation
            # FAISS L2 Distance (lower = better semantic similarity). 
            distance = faiss_scheme_ids[scheme.get("scheme_id")]
            semantic_score = 1.0 / (1.0 + distance) # Turn distance to a 0.0-1.0 score
            
            # Normalize priority score 0-100 down to 0-1 range
            raw_priority = scheme.get("scoring", {}).get("priority_score", 50)
            priority_score = raw_priority / 100.0
            
            # The Final Intelligence Ranking Math
            final_score = (
                0.5 * confidence_score +
                0.3 * priority_score +
                0.2 * semantic_score
            )
            
            # 5. Extract UI Response attributes statically
            categories = scheme.get("scheme_category", [])
            cat_str = categories[0] if categories else "General"
            
            priority_tag = "High Benefit" if priority_score > 0.85 else "Standard"
            
            recommended.append({
                "scheme": scheme,
                "confidence_score": confidence_score, # Visual raw score
                "final_score": final_score, # Sorting factor
                "match_reason": match_reason,
                "match_type": match_type,
                "category": cat_str,
                "priority_tag": priority_tag,
                "documents_required": scheme.get("documents_required", [])
            })
            
        # Rank sequentially by combined formula descending
        recommended.sort(key=lambda x: x["final_score"], reverse=True)
        top_recommendations = recommended[:5] # Bound result frame
        
        # Guard: No Schemes Matched Post Filter
        if not top_recommendations:
            return RecommendationEngine._get_empty_fallback()
            
        print(f"Matched {len(top_recommendations)} schemes for response payload.")
        
        # Formatting Return JSON Sequence
        final_response = []
        for rec in top_recommendations:
            scheme = rec["scheme"]
            
            benefits_obj = scheme.get("benefits", {})
            benefits_text = benefits_obj.get("description", "No benefits listed")
            if benefits_obj.get("amount"):
                benefits_text = f"{benefits_obj.get('amount')} - {benefits_text}"

            response_obj = SchemeResponse(
                scheme_name=scheme.get("scheme_name", "Unknown Scheme"),
                eligible=True,
                confidence_score=rec["confidence_score"],
                match_reason=rec["match_reason"],
                benefits=benefits_text,
                application_link=scheme.get("application", {}).get("link", ""),
                category=rec["category"],
                documents_required=rec["documents_required"],
                match_type=rec["match_type"],
                priority_tag=rec["priority_tag"]
            )
            final_response.append(response_obj)
            
        return final_response

    @staticmethod
    def _get_empty_fallback():
        """Fallbacks safe response JSON so UI never crashes"""
        print("No schemes matched. Returning fallback.")
        return [
            SchemeResponse(
                scheme_name="No Match Found",
                eligible=False,
                confidence_score=0.0,
                match_reason="No schemes closely matched your profile criteria.",
                benefits="N/A",
                application_link="",
                category="System Alert",
                documents_required=[],
                match_type="None",
                priority_tag="Irrelevant"
            )
        ]

recommendation_engine = RecommendationEngine()
