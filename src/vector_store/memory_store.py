"""In-memory vector store implementation."""

import asyncio
from typing import Dict, List, Optional

import numpy as np

from . import BaseVectorStore, VectorSearchResult


class MemoryVectorStore(BaseVectorStore):
    """In-memory vector store for development and testing."""

    def __init__(self):
        """Initialize the in-memory store."""
        super().__init__()
        self._vectors: Dict[str, Dict] = {}
        self._lock = asyncio.Lock()

    async def store(self, id: str, vector: List[float], metadata: dict = None) -> bool:
        """Store a vector in memory.

        Args:
            id: Unique identifier for the vector
            vector: Vector embedding
            metadata: Additional metadata

        Returns:
            True if successful, False otherwise
        """
        async with self._lock:
            self._vectors[id] = {
                "vector": np.array(vector),
                "metadata": metadata or {},
                "id": id
            }
        return True

    async def search(self, query_vector: List[float], limit: int = 10) -> List[VectorSearchResult]:
        """Search for similar vectors in memory.

        Args:
            query_vector: Query vector
            limit: Maximum number of results

        Returns:
            List of search results
        """
        async with self._lock:
            if not self._vectors:
                return []

            query_array = np.array(query_vector)
            results = []

            for id, data in self._vectors.items():
                vector = data["vector"]
                metadata = data["metadata"]

                # Calculate cosine similarity
                similarity = self._cosine_similarity(query_array, vector)

                results.append(VectorSearchResult(
                    id=id,
                    score=float(similarity),
                    metadata=metadata,
                    content=metadata.get("content")
                ))

            # Sort by similarity (descending) and limit results
            results.sort(key=lambda x: x.score, reverse=True)
            return results[:limit]

    async def delete(self, id: str) -> bool:
        """Delete a vector from memory.

        Args:
            id: Vector ID to delete

        Returns:
            True if successful, False otherwise
        """
        async with self._lock:
            if id in self._vectors:
                del self._vectors[id]
                return True
            return False

    def _cosine_similarity(self, a: np.ndarray, b: np.ndarray) -> float:
        """Calculate cosine similarity between two vectors.

        Args:
            a: First vector
            b: Second vector

        Returns:
            Cosine similarity score
        """
        # Add small epsilon to avoid division by zero
        epsilon = 1e-8
        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)

        if norm_a == 0 or norm_b == 0:
            return 0.0

        return float(np.dot(a, b) / (norm_a * norm_b + epsilon))

    def get_stats(self) -> Dict:
        """Get statistics about the vector store.

        Returns:
            Dictionary with store statistics
        """
        return {
            "total_vectors": len(self._vectors),
            "vector_dimension": self.settings.vector_store.dimension,
            "store_type": "memory"
        }
