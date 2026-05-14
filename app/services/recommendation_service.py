import json
from pathlib import Path

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

from app.schemas.chat import ProductSuggestion
from app.services.product_service import product_service


class RecommendationService:
    def __init__(self):
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        self.products = product_service.products
        self.index = None
        self.embeddings = None
        self._build_index()

    def _build_index(self):
        texts = []

        for product in self.products:
            title = product.get("title") or ""
            description = product.get("description") or ""

            texts.append(f"{title}. {description}")

        if not texts:
            return

        embeddings = self.model.encode(texts)
        embeddings = np.array(embeddings).astype("float32")

        dimension = embeddings.shape[1]

        self.index = faiss.IndexFlatL2(dimension)
        self.index.add(embeddings)

    def recommend_products(self, query: str, limit: int = 3):
        if self.index is None:
            return []

        query_embedding = self.model.encode([query])
        query_embedding = np.array(query_embedding).astype("float32")

        _, indices = self.index.search(query_embedding, limit)

        recommendations = []

        for idx in indices[0]:
            if idx < 0 or idx >= len(self.products):
                continue

            product = self.products[idx]

            title = product.get("title") or ""
            description = product.get("description") or ""

            if not title:
                continue

            detailed_products = product_service.search_products(title, limit=1)

            if detailed_products:
                recommendations.extend(detailed_products)

        return recommendations[:limit]


recommendation_service = RecommendationService()