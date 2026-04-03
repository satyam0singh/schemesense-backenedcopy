import faiss
import numpy as np
from app.utils.embeddings import embedding_model

class RAGService:
    def __init__(self):
        self.index = None
        self.scheme_ids = []

    def build_index(self, schemes):
        """
        Build a FAISS vector index of the schemes based on ai_fields.search_text 
        """
        self.scheme_ids = []
        texts = []

        for scheme in schemes:
            self.scheme_ids.append(scheme.get("scheme_id"))
            ai_fields = scheme.get("ai_fields", {})
            search_text = ai_fields.get("search_text", "")
            summary = ai_fields.get("summary", "")
            keywords = " ".join(ai_fields.get("keywords", []))
            
            # Combine to create a rich semantic block
            text = f"{search_text} {summary} {keywords}".strip()
            if not text:
                text = scheme.get("scheme_name", "")
            texts.append(text)

        if not texts:
            return

        # Encode all search texts
        embeddings = embedding_model.encode(texts)
        
        # Dimensions is the size of each vector
        dimension = embeddings.shape[1]
        
        # We use an L2 distance (Euclidean distance) index for FAISS
        self.index = faiss.IndexFlatL2(dimension)
        
        # FAISS expects numpy arrays as float32
        self.index.add(np.array(embeddings).astype("float32"))
        print(f"Added {len(texts)} scheme embeddings to FAISS index.")

    def search(self, query_text, top_k=5):
        """
        Search the scheme FAISS index for relevant documents
        """
        if self.index is None or not self.scheme_ids:
            return []

        # Convert query to vector
        query_vector = embedding_model.encode([query_text]).astype("float32")
        
        # Conduct similarity search
        distances, indices = self.index.search(query_vector, top_k)
        
        results = []
        for i, idx in enumerate(indices[0]):
            if idx != -1: # -1 implies empty index or no match
                results.append({
                    "id": self.scheme_ids[idx],
                    "distance": distances[0][i]
                })

        return results

rag_engine = RAGService()
