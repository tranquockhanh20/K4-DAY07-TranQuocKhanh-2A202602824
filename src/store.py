from __future__ import annotations

from typing import Any, Callable

from .chunking import _dot, compute_similarity
from .embeddings import _mock_embed
from .models import Document


class EmbeddingStore:
    """
    A vector store for text chunks.

    Tries to use ChromaDB if available; falls back to an in-memory store.
    The embedding_fn parameter allows injection of mock embeddings for tests.
    """

    def __init__(
        self,
        collection_name: str = "documents",
        embedding_fn: Callable[[str], list[float]] | None = None,
    ) -> None:
        self._embedding_fn = embedding_fn or _mock_embed
        self._collection_name = collection_name
        self._use_chroma = False
        self._store: list[dict[str, Any]] = []
        self._collection = None
        self._next_index = 0

        try:
            import chromadb  # noqa: F401

            # TODO: initialize chromadb client + collection
            client = chromadb.Client()
            self._collection = client.get_or_create_collection(
                name=self._collection_name
            )
            self._use_chroma = True
        except Exception:
            self._use_chroma = False
            self._collection = None

    def _make_record(self, doc: Document) -> dict[str, Any]:
        # TODO: build a normalized stored record for one document
        meta = dict(doc.metadata) if doc.metadata else {}
        if "doc_id" not in meta:
            meta["doc_id"] = doc.id
        return {
            "id": doc.id,
            "content": doc.content,
            "metadata": meta,
            "embedding": self._embedding_fn(doc.content),
        }

    def _search_records(self, query: str, records: list[dict[str, Any]], top_k: int) -> list[dict[str, Any]]:
        # TODO: run in-memory similarity search over provided records
        query_emb = self._embedding_fn(query)
        results = []
        for record in records:
            score = compute_similarity(query_emb, record["embedding"])
            results.append({
                "id": record.get("id"),
                "content": record["content"],
                "metadata": record["metadata"],
                "score": score,
             })
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:top_k]

    def add_documents(self, docs: list[Document]) -> None:
        """
        Embed each document's content and store it.

        For ChromaDB: use collection.add(ids=[...], documents=[...], embeddings=[...])
        For in-memory: append dicts to self._store
        """
        # TODO: embed each doc and add to store
        if self._use_chroma:
            # Prepare data for ChromaDB
            # We assume self._embedding_fn can handle chunks (list of strings)
            # Chroma expects lists of the same length for ids, documents, embeddings
            doc_ids = [f"doc_{self._next_index + i}" for i in range(len(docs))]
            texts = [doc.text for doc in docs]
            embeddings = [self._embedding_fn(doc.text) for doc in docs]
            
            # Metadata needs to include doc_id
            metadata_list = []
            for i, doc in enumerate(docs):
                meta = doc.metadata or {}
                meta['doc_id'] = doc_ids[i]
                metadata_list.append(meta)
            
            self._collection.add(
                ids=doc_ids,
                documents=texts,
                embeddings=embeddings,
                metadatas=metadata_list
            )
            self._next_index += len(docs)
        else:
            # In-memory store
            for doc in docs:
                self._store.append(self._make_record(doc))

    def search(self, query: str, top_k: int = 5) -> list[dict[str, Any]]:
        """
        Find the top_k most similar documents to query.

        For in-memory: compute dot product of query embedding vs all stored embeddings.
        """
        # TODO: embed query, compute similarities, return top_k
        if self._use_chroma:
            results = self._collection.query(
                query_texts=[query],
                n_results=top_k,
                include=['documents', 'metadatas', 'distances']
            )
            output = []
            if results and results.get('documents') and len(results['documents']) > 0:
                doc_list = results['documents'][0]
                meta_list = results.get('metadatas', [{}])[0]
                query_emb = self._embedding_fn(query)
                for i, doc_text in enumerate(doc_list):
                    meta = meta_list[i] if meta_list else {}
                    all_records = self._collection.get(ids=results['ids'][0], include=['documents', 'metadatas', 'embeddings'])
                    pass
            return output
        else:
            # In-memory store
            return self._search_records(query, self._store, top_k)

    def get_collection_size(self) -> int:
        """Return the total number of stored chunks."""
        # TODO
        if self._use_chroma:
            return self._collection.count()
        else:
            return len(self._store)

    def search_with_filter(self, query: str, top_k: int = 3, metadata_filter: dict = None) -> list[dict]:
        """
        Search with optional metadata pre-filtering.

        First filter stored chunks by metadata_filter, then run similarity search.
        """
        # TODO: filter by metadata, then search among filtered chunks
        if metadata_filter:
            filtered = [
                r for r in self._store
                if all(r.get("metadata", {}).get(k) == v for k, v in metadata_filter.items())
            ]
        else:
            filtered = self._store
        return self._search_records(query, filtered, top_k)

    def delete_document(self, doc_id: str) -> bool:
        """
        Remove all chunks belonging to a document.

        Returns True if any chunks were removed, False otherwise.
        """
        # TODO: remove all stored chunks where metadata['doc_id'] == doc_id
        initial_len = len(self._store)
        self._store = [r for r in self._store if r.get("metadata", {}).get("doc_id") != doc_id]
        return len(self._store) < initial_len
