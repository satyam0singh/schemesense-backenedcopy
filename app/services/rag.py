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
        # Simple Stop-word Filter
        stop_words = {"tell", "me", "about", "in", "the", "for", "is", "a", "of", "and", "to", "with", "from"}
        query_words = [w for w in query_text.lower().split() if w not in stop_words]
        
        if not query_words:
            query_words = query_text.lower().split()

        results = []
        for scheme in self.schemes:
            ai_fields = scheme.get("ai_fields", {})
            search_text = ai_fields.get("search_text", "").lower()
            keywords = [k.lower() for k in ai_fields.get("keywords", [])]
            
            # 1. Check Search Text (Base Score)
            score = sum(word in search_text for word in query_words)
            
            # 2. Check Primary Keywords (High Weight Bonus)
            keyword_score = sum(word in keywords for word in query_words) * 2
            
            total_score = score + keyword_score
            
            if total_score > 0:
                results.append((total_score, scheme.get("scheme_id")))
        
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
