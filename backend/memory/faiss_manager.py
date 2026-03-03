import faiss
import numpy as np
import os

class FAISSManager:
    def __init__(self, index_path="memory/faiss_index.bin", dimension=384):
        self.index_path = index_path
        self.dimension = dimension
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(index_path), exist_ok=True)
        
        if os.path.exists(index_path):
            self.index = faiss.read_index(index_path)
        else:
            self.index = faiss.IndexFlatL2(dimension)

    def add_vector(self, vector):
        vector = np.array([vector]).astype('float32')
        self.index.add(vector)
        self.save()

    def search(self, query_vector, k=5):
        query_vector = np.array([query_vector]).astype('float32')
        distances, indices = self.index.search(query_vector, k)
        return indices[0], distances[0]

    def save(self):
        faiss.write_index(self.index, self.index_path)

    def get_total_count(self):
        return self.index.ntotal
