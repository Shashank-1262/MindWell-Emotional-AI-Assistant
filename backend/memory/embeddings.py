from sentence_transformers import SentenceTransformer

class EmbeddingModel:
    """Singleton wrapper for the sentence-transformers model."""
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            print("Loading Embedding Model (MiniLM)...")
            cls._instance = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
        return cls._instance

    @classmethod
    def get_model(cls):
        return cls()

def get_embeddings(text):
    """Utility function to get embeddings for a single text or list of texts."""
    model = EmbeddingModel.get_model()
    return model.encode(text)
