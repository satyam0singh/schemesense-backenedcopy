from sentence_transformers import SentenceTransformer

class EmbeddingsModel:
    def __init__(self, model_name="all-MiniLM-L6-v2"):
        # Load the pre-trained embedding model
        # The first time this is run, it will download the model weights
        self.model = SentenceTransformer(model_name)

    def encode(self, texts):
        """
        Convert text into a numeric vector representation (embeddings)
        """
        # Convert the list of texts or a single string to embeddings
        return self.model.encode(texts)

# We create a singleton instance to be shared across the system
embedding_model = EmbeddingsModel()
