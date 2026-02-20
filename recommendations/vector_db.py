import lancedb
from sentence_transformers import SentenceTransformer
import os
import pandas as pd

# Settings
LANCEDB_URI = "data/lancedb_store"
# MODEL_NAME = 'all-distilroberta-v1'  # Optimized RoBERTa version for sentence embeddings
MODEL_NAME = 'all-MiniLM-L6-v2'  # Optimized RoBERTa version for sentence embeddings



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

    def update_article(self, article):
        """
        Updates or Inserts a single article into LanceDB.
        """
        tbl = self.get_or_create_table()

        # 1. Generate new embedding
        text_to_embed = f"{article.title}. {article.content}"
        vector = self.get_embedding(text_to_embed)

        # 2. Prepare payload
        new_data = [{
            "id": article.id,
            "vector": vector,
            "title": article.title,
            "text": text_to_embed[:100]
        }]

        # 3. Perform Merge (Upsert)
        # This looks for an existing row with this 'id'.
        # If found, it updates it. If not, it inserts it.
        try:
            tbl.merge(new_data, on="id")
            print(f"Synced Article {article.id} to LanceDB.")
        except Exception as e:
            # Fallback for older LanceDB versions or empty tables:
            # Delete and Re-add
            tbl.delete(f"id = {article.id}")
            tbl.add(new_data)
            print(f"Synced (Fallback) Article {article.id} to LanceDB.")

    def delete_article(self, article_id):
        """
        Removes an article from LanceDB when deleted from SQL.
        """
        tbl = self.get_or_create_table()
        if tbl:
            tbl.delete(f"id = {article_id}")
            print(f"Deleted Article {article_id} from LanceDB.")