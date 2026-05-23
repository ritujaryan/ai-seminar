import os
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

# Try to import chromadb and sentence_transformers
CHROMA_AVAILABLE = False
try:
    import chromadb
    from sentence_transformers import SentenceTransformer
    CHROMA_AVAILABLE = True
    logger.info("ChromaDB and SentenceTransformers imported successfully.")
except Exception as e:
    logger.warning(f"ChromaDB or SentenceTransformers not available: {e}. Using in-memory fallback.")

class VectorRepository:
    def __init__(self, persist_dir: str):
        self.persist_dir = persist_dir
        self._fallback_db: List[Dict[str, Any]] = []
        self.client = None
        self.collection = None
        self.doubts_collection = None
        self.model = None

        if CHROMA_AVAILABLE:
            try:
                os.makedirs(persist_dir, exist_ok=True)
                self.client = chromadb.PersistentClient(path=persist_dir)
                self.collection = self.client.get_or_create_collection("slides_context")
                self.doubts_collection = self.client.get_or_create_collection("resolved_doubts")
                
                # Initialize sentence transformer model
                self.model = SentenceTransformer("all-MiniLM-L6-v2")
                logger.info("ChromaDB client and embedding model initialized.")
            except Exception as e:
                logger.error(f"Error initializing ChromaDB client: {e}. Falling back to in-memory store.")
                self.client = None
                self.collection = None
                self.doubts_collection = None
                self.model = None

    def add_documents(self, documents: List[str], metadatas: List[Dict[str, Any]], ids: List[str]):
        """
        Embed and add documents to the slides context collection.
        """
        if self.client and self.collection and self.model:
            try:
                embeddings = self.model.encode(documents).tolist()
                self.collection.add(
                    embeddings=embeddings,
                    documents=documents,
                    metadatas=metadatas,
                    ids=ids
                )
                logger.info(f"Added {len(documents)} slide contexts to ChromaDB.")
                return
            except Exception as e:
                logger.error(f"ChromaDB add failed: {e}. Storing in fallback database.")
        
        # Fallback database
        for doc, meta, doc_id in zip(documents, metadatas, ids):
            existing = next((item for item in self._fallback_db if item["id"] == doc_id), None)
            if existing:
                existing["document"] = doc
                existing["metadata"] = meta
            else:
                self._fallback_db.append({
                    "id": doc_id,
                    "document": doc,
                    "metadata": meta
                })
        logger.info(f"Added {len(documents)} slide documents to in-memory fallback DB.")

    def query(self, query_text: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """
        Query the slides context collection for similar documents.
        """
        if self.client and self.collection and self.model:
            try:
                query_embeddings = self.model.encode([query_text]).tolist()
                results = self.collection.query(
                    query_embeddings=query_embeddings,
                    n_results=n_results
                )
                
                formatted_results = []
                if results and "documents" in results and results["documents"]:
                    docs = results["documents"][0]
                    metas = results["metadatas"][0] if "metadatas" in results else [{}] * len(docs)
                    ids = results["ids"][0]
                    distances = results["distances"][0] if "distances" in results else [0.0] * len(docs)
                    
                    for doc, meta, doc_id, dist in zip(docs, metas, ids, distances):
                        formatted_results.append({
                            "id": doc_id,
                            "document": doc,
                            "metadata": meta,
                            "score": float(dist)
                        })
                return formatted_results
            except Exception as e:
                logger.error(f"ChromaDB query failed: {e}. Querying fallback database.")

        # Fallback search
        logger.info("Executing simple keyword search on fallback in-memory database.")
        query_words = set(query_text.lower().split())
        scored_results = []
        for item in self._fallback_db:
            if item["metadata"].get("type") in ["full_slide", "content", "notes"]:
                doc_words = set(item["document"].lower().split())
                intersection = query_words.intersection(doc_words)
                score = len(intersection) / max(len(query_words.union(doc_words)), 1)
                scored_results.append((item, score))
            
        scored_results.sort(key=lambda x: x[1], reverse=True)
        top_results = []
        for item, score in scored_results[:n_results]:
            top_results.append({
                "id": item["id"],
                "document": item["document"],
                "metadata": item["metadata"],
                "score": score
            })
        return top_results

    # --- Persistent Doubt Storage Logic ---

    def add_doubt(self, doubt_id: str, question: str, slide_id: int, status: str = "pending", answer: Optional[str] = None):
        """
        Store a user doubt in the vector DB.
        """
        doc = f"Question: {question}\nAnswer: {answer or 'Pending'}"
        meta = {
            "slide_id": slide_id,
            "doubt_id": doubt_id,
            "status": status,
            "question": question,
            "answer": answer or "",
            "type": "doubt"
        }
        
        if self.client and self.doubts_collection and self.model:
            try:
                embeddings = self.model.encode([doc]).tolist()
                self.doubts_collection.upsert(
                    embeddings=embeddings,
                    documents=[doc],
                    metadatas=[meta],
                    ids=[f"doubt_{doubt_id}"]
                )
                logger.info(f"Stored doubt {doubt_id} in ChromaDB (status: {status}).")
                return
            except Exception as e:
                logger.error(f"ChromaDB add_doubt failed: {e}. Saving to fallback database.")

        # Fallback
        self._fallback_db = [item for item in self._fallback_db if item["id"] != f"doubt_{doubt_id}"]
        self._fallback_db.append({
            "id": f"doubt_{doubt_id}",
            "document": doc,
            "metadata": meta
        })
        logger.info(f"Stored doubt {doubt_id} in fallback in-memory DB.")

    def get_doubts_for_slide(self, slide_id: int) -> List[Dict[str, Any]]:
        """
        Retrieve all doubts (pending & resolved) for a slide from the vector DB.
        """
        if self.client and self.doubts_collection:
            try:
                results = self.doubts_collection.get(
                    where={"slide_id": slide_id}
                )
                
                doubts = []
                if results and "metadatas" in results and results["metadatas"]:
                    for doc_id, meta in zip(results["ids"], results["metadatas"]):
                        doubts.append({
                            "doubt_id": meta["doubt_id"],
                            "slide_id": int(meta["slide_id"]),
                            "question": meta["question"],
                            "answer": meta.get("answer") or None,
                            "status": meta["status"]
                        })
                return doubts
            except Exception as e:
                logger.error(f"ChromaDB get_doubts failed: {e}. Reading from fallback database.")

        # Fallback
        doubts = []
        for item in self._fallback_db:
            meta = item["metadata"]
            if meta.get("type") == "doubt" and int(meta.get("slide_id")) == slide_id:
                doubts.append({
                    "doubt_id": meta["doubt_id"],
                    "slide_id": int(meta["slide_id"]),
                    "question": meta["question"],
                    "answer": meta.get("answer") or None,
                    "status": meta["status"]
                })
        return doubts

    def update_doubt(self, doubt_id: str, question: str, slide_id: int, status: str, answer: str):
        """
        Update the doubt content and status in the vector DB.
        """
        self.add_doubt(doubt_id, question, slide_id, status, answer)

    def query_doubts(self, query_text: str, slide_id: int, n_results: int = 5) -> List[Dict[str, Any]]:
        """
        Search similarities in previously asked questions to implement a cache-check.
        """
        if self.client and self.doubts_collection and self.model:
            try:
                query_embeddings = self.model.encode([query_text]).tolist()
                results = self.doubts_collection.query(
                    query_embeddings=query_embeddings,
                    n_results=n_results,
                    where={"slide_id": slide_id}
                )
                
                formatted_results = []
                if results and "documents" in results and results["documents"]:
                    docs = results["documents"][0]
                    metas = results["metadatas"][0] if "metadatas" in results else [{}] * len(docs)
                    ids = results["ids"][0]
                    distances = results["distances"][0] if "distances" in results else [0.0] * len(docs)
                    
                    for doc, meta, doc_id, dist in zip(docs, metas, ids, distances):
                        formatted_results.append({
                            "id": doc_id,
                            "document": doc,
                            "metadata": meta,
                            "score": float(dist)
                        })
                return formatted_results
            except Exception as e:
                logger.error(f"ChromaDB query_doubts failed: {e}. Querying fallback database.")

        # Fallback
        logger.info("Executing Jaccard similarity keyword search on fallback doubts database.")
        query_words = set(query_text.lower().split())
        scored_results = []
        for item in self._fallback_db:
            meta = item["metadata"]
            if meta.get("type") == "doubt" and int(meta.get("slide_id")) == slide_id:
                doc_words = set(meta["question"].lower().split())
                intersection = query_words.intersection(doc_words)
                score = len(intersection) / max(len(query_words.union(doc_words)), 1)
                scored_results.append((item, score))
            
        scored_results.sort(key=lambda x: x[1], reverse=True)
        top_results = []
        for item, score in scored_results[:n_results]:
            top_results.append({
                "id": item["id"],
                "document": item["document"],
                "metadata": item["metadata"],
                "score": score
            })
        return top_results

    def clear(self):
        """
        Clear all documents in the database.
        """
        if self.client:
            try:
                self.client.delete_collection("slides_context")
                self.collection = self.client.create_collection("slides_context")
            except Exception as e:
                logger.error(f"ChromaDB clear collection failed: {e}")
            try:
                self.client.delete_collection("resolved_doubts")
                self.doubts_collection = self.client.create_collection("resolved_doubts")
            except Exception as e:
                logger.error(f"ChromaDB clear doubts_collection failed: {e}")
        self._fallback_db.clear()
        logger.info("Fallback in-memory database cleared.")

# Singleton initialization
vector_repo: Optional[VectorRepository] = None

def init_vector_repo(persist_dir: str):
    global vector_repo
    vector_repo = VectorRepository(persist_dir)
    return vector_repo

def get_vector_repo() -> VectorRepository:
    global vector_repo
    if vector_repo is None:
        from app.core.config import settings
        vector_repo = VectorRepository(settings.CHROMA_PERSIST_DIR)
    return vector_repo
