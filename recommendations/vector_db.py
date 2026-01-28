import lancedb
from sentence_transformers import SentenceTransformer
import os
import pandas as pd

# Settings
LANCEDB_URI = "data/lancedb_store"
MODEL_NAME = 'all-distilroberta-v1'  # Optimized RoBERTa version for sentence embeddings


class VectorService:
    _instance = None

    def __new__(cls):
        # Singleton pattern to load model only once
        if cls._instance is None:
            cls._instance = super(VectorService, cls).__new__(cls)
            print("Loading RoBERTa model...")
            cls._instance.model = SentenceTransformer(MODEL_NAME)

            # Initialize LanceDB
            os.makedirs(LANCEDB_URI, exist_ok=True)
            cls._instance.db = lancedb.connect(LANCEDB_URI)

        return cls._instance

    def get_embedding(self, text):
        """Generates a vector embedding for a given text."""
        return self.model.encode(text).tolist()

    def get_or_create_table(self, table_name="items"):
        """Gets the LanceDB table."""
        # Check if table exists, if not create a dummy schema or handle in ingestion
        try:
            return self.db.open_table(table_name)
        except:
            return None

    def upsert_data(self, data_list, table_name="items"):
        """
        data_list: List of dicts [{'id': 1, 'vector': [...], 'text': '...'}, ...]
        """
        try:
            tbl = self.db.open_table(table_name)
            tbl.add(data_list)
        except:
            # If table doesn't exist, create it from data
            self.db.create_table(table_name, data=data_list)

    def search_similar(self, query_vector, table_name="items", top_k=5):
        tbl = self.get_or_create_table(table_name)
        if not tbl:
            return []

        # LanceDB search API
        results = tbl.search(query_vector).limit(top_k).to_list()
        return results