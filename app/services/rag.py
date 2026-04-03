class RAGService:
    def __init__(self):
        self.schemes = []

    def build_index(self, schemes):
        """
        Store schemes in memory for keyword search.
        No FAISS index needed anymore to save RAM on Render Free Tier.
        """
        self.schemes = schemes
        print("Loaded schemes for keyword search (FAISS removed).")

    def search(self, query_text, top_k=20):
        """
        Keyword based search to replace semantic/FAISS search and fit free tier.
        Returns: [{"id": scheme_id, "distance": simulated_distance}, ...]
        """
        if not self.schemes:
            return []

        results = []
        for scheme in self.schemes:
            # Safely grab search text
            ai_fields = scheme.get("ai_fields", {})
            search_text = ai_fields.get("search_text", "").lower()
            
            # Simple keyword matching as requested
            score = sum(word in search_text for word in query_text.lower().split())
            if score > 0:
                results.append((score, scheme.get("scheme_id")))
        
        # Sort by best match (highest score first)
        sorted_results = sorted(results, reverse=True)
        
        # Format explicitly to maintain compatibility with recommendation.py equations
        final_results = []
        for rank, (score, scheme_id) in enumerate(sorted_results[:top_k]):
            # distance: 0 is best match, higher is worse. 1/(score+1) gives exactly this.
            distance = 1.0 / (score + 1.0) 
            final_results.append({"id": scheme_id, "distance": distance})
            
        return final_results

rag_engine = RAGService()
