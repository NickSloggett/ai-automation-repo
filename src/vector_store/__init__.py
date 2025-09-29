"""Vector store integration for embeddings and similarity search."""

from typing import List, Optional

import numpy as np
from pydantic import BaseModel

from ..config import get_settings

settings = get_settings()


class VectorSearchResult(BaseModel):
    """Result from a vector search."""

    id: str
    score: float
    metadata: dict = {}
    content: Optional[str] = None


class BaseVectorStore:
    """Base class for vector store implementations."""

    def __init__(self):
        """Initialize the vector store."""
        self.settings = settings

    async def store(self, id: str, vector: List[float], metadata: dict = None) -> bool:
        """Store a vector with metadata.

        Args:
            id: Unique identifier for the vector
            vector: Vector embedding
            metadata: Additional metadata

        Returns:
            True if successful, False otherwise
        """
        raise NotImplementedError

    async def search(self, query_vector: List[float], limit: int = 10) -> List[VectorSearchResult]:
        """Search for similar vectors.

        Args:
            query_vector: Query vector
            limit: Maximum number of results

        Returns:
            List of search results
        """
        raise NotImplementedError

    async def delete(self, id: str) -> bool:
        """Delete a vector by ID.

        Args:
            id: Vector ID to delete

        Returns:
            True if successful, False otherwise
        """
        raise NotImplementedError


class VectorStoreManager:
    """Manager for vector store operations."""

    def __init__(self):
        """Initialize the vector store manager."""
        self.store: Optional[BaseVectorStore] = None
        self._initialize_store()

    def _initialize_store(self) -> None:
        """Initialize the appropriate vector store based on configuration."""
        provider = settings.vector_store.provider.lower()

        if provider == "pinecone":
            try:
                from .pinecone_store import PineconeVectorStore
                self.store = PineconeVectorStore()
            except ImportError:
                print("Pinecone not available, falling back to in-memory store")
                from .memory_store import MemoryVectorStore
                self.store = MemoryVectorStore()

        elif provider == "weaviate":
            try:
                from .weaviate_store import WeaviateVectorStore
                self.store = WeaviateVectorStore()
            except ImportError:
                print("Weaviate not available, falling back to in-memory store")
                from .memory_store import MemoryVectorStore
                self.store = MemoryVectorStore()

        else:
            # Default to in-memory store
            from .memory_store import MemoryVectorStore
            self.store = MemoryVectorStore()

    async def store_document(self, id: str, content: str, metadata: dict = None) -> bool:
        """Store a document with its embedding.

        Args:
            id: Document ID
            content: Document content
            metadata: Document metadata

        Returns:
            True if successful, False otherwise
        """
        if not self.store:
            return False

        # Generate embedding (placeholder - would use actual embedding model)
        vector = await self._generate_embedding(content)

        return await self.store.store(id, vector, metadata or {})

    async def search_similar(self, query: str, limit: int = 10) -> List[VectorSearchResult]:
        """Search for similar documents.

        Args:
            query: Search query
            limit: Maximum results

        Returns:
            List of similar documents
        """
        if not self.store:
            return []

        # Generate embedding for query
        query_vector = await self._generate_embedding(query)

        return await self.store.search(query_vector, limit)

    async def _generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for text.

        Args:
            text: Text to embed

        Returns:
            Vector embedding
        """
        # Placeholder implementation
        # In production, this would use a proper embedding model
        import hashlib
        import numpy as np

        # Simple hash-based embedding for demo purposes
        hash_obj = hashlib.md5(text.encode())
        hash_bytes = hash_obj.digest()

        # Convert to float array and normalize
        vector = np.frombuffer(hash_bytes, dtype=np.float32)
        # Pad or truncate to match expected dimension
        target_dim = settings.vector_store.dimension
        if len(vector) < target_dim:
            # Pad with zeros
            vector = np.pad(vector, (0, target_dim - len(vector)))
        elif len(vector) > target_dim:
            # Truncate
            vector = vector[:target_dim]

        return vector.tolist()


# Global vector store instance
_vector_store_manager: Optional[VectorStoreManager] = None


def get_vector_store() -> VectorStoreManager:
    """Get the global vector store manager instance."""
    global _vector_store_manager
    if _vector_store_manager is None:
        _vector_store_manager = VectorStoreManager()
    return _vector_store_manager
