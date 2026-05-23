import os
import sys
import uuid
from datetime import datetime

# Ensure project root is in python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.config import settings
from app.repositories.vector_repository import init_vector_repo
from app.repositories.slide_repository import slide_repo
from app.repositories.doubt_repository import doubt_repo
from app.repositories.session_repository import session_repo
from app.services.rag_service import rag_service
from app.models.slide import Slide
from app.models.session import SeminarSession
from app.agents.orchestrator import orchestrator

def reset_and_seed():
    print("=" * 60)
    print("Resetting and Seeding AI Seminar Database...")
    print("=" * 60)
    
    # 1. Initialize Vector DB
    print("Initializing Vector DB connection...")
    vector_db = init_vector_repo(settings.CHROMA_PERSIST_DIR)
    
    # 2. Clear old data from memory and Vector DB disk files
    print("Clearing all collections and repository files...")
    slide_repo.clear()
    doubt_repo.clear()
    session_repo.clear()
    vector_db.clear()
    
    # 3. Create a professional dummy slide deck
    print("Seeding new Slide Deck data...")
    dummy_slides = [
        Slide(
            slide_id=0,
            title="The RAG Architecture",
            content="Retrieval-Augmented Generation (RAG) resolves LLM limitations (hallucinations, static knowledge) by injecting relevant facts fetched from external document search engines at query time.",
            notes="Welcome everyone to our technical seminar. Explain that LLMs are like smart students with a dictionary but no internet access, and RAG provides them with a search engine. We do not wait for doubts here.",
            wait_for_doubts=False
        ),
        Slide(
            slide_id=1,
            title="Vector Embeddings & Semantic Search",
            content="Documents are split into chunks, transformed into high-dimensional numerical vectors (embeddings), and stored in a Vector Database (like ChromaDB). Semantic search compares vectors using cosine distance.",
            notes="Emphasize that keyword searches fail on concepts, whereas embeddings capture meaning (e.g. 'feline' matching 'cat'). Wait for doubts here to address vector dimensions, chunking strategies, or database indexing.",
            wait_for_doubts=True
        ),
        Slide(
            slide_id=2,
            title="Optimizing RAG Performance",
            content="Production challenges require advanced strategies: Parent-Document Retrieval, Sentence-Window retrieval, metadata filtering, and re-ranking models (like Cohere Rerank) to filter out noise.",
            notes="Explain that raw chunks often lose context, which is why windowing or parent-child chunks are used. Wait for doubts here so the audience can ask about indexing speeds, cost, or retrieval accuracy.",
            wait_for_doubts=True
        ),
        Slide(
            slide_id=3,
            title="The Multi-Agent Orchestration Layer",
            content="Instead of a single flow, CrewAI uses autonomous agents (Maker, Checker, Reviewer) to collaborate. The RAG output is verified for quality and formatted into professional slide speech.",
            notes="Conclude by showing how agents verify the answers to avoid any hallucinations. This Maker-Checker approach ensures maximum accuracy for live events. Do not wait for doubts.",
            wait_for_doubts=False
        )
    ]
    
    # Save to slide repository
    slide_repo.deck_title = "Building Production-Grade RAG Systems"
    for slide in dummy_slides:
        slide_repo.create(slide)
        
    # Index in Vector DB
    rag_service.index_deck(dummy_slides)
    print(f"Successfully indexed {len(dummy_slides)} slides in the 'slides_context' collection.")
    
    # 4. Pre-seed resolved doubts and answers
    print("Seeding sample doubts and answers...")
    sample_doubts = [
        # Doubts for Slide 1 (Vector Embeddings)
        {
            "slide_id": 1,
            "question": "What embedding model is used by default?",
            "answer": "By default, we use sentence-transformers/all-MiniLM-L6-v2 which runs locally on CPU and maps text to a 384-dimensional vector space, balancing speed and accuracy.",
            "status": "approved"
        },
        {
            "slide_id": 1,
            "question": "How does Cosine Similarity differ from L2 distance?",
            "answer": "Cosine similarity measures the angle between vectors (direction/semantic meaning), ignoring magnitude. L2 distance measures straight-line distance, which is sensitive to text length.",
            "status": "approved"
        },
        {
            "slide_id": 1,
            "question": "Are new slides automatically indexed?",
            "answer": "Yes, our SeminarOrchestrator immediately encodes and indexes new slides and speaker notes into the slides_context collection in ChromaDB upon starting.",
            "status": "pending"  # Show one pending doubt
        },
        # Doubts for Slide 2 (Optimizing RAG)
        {
            "slide_id": 2,
            "question": "What is a Re-ranking model?",
            "answer": "A re-ranker acts as a second-stage filter. It takes the top 20 retrieved chunks from the vector database and runs a high-quality cross-encoder model to sort them by exact semantic relevance to the query, selecting the best 5.",
            "status": "approved"
        }
    ]
    
    for seed in sample_doubts:
        doubt_id = str(uuid.uuid4())
        # Store in Vector DB via get_vector_repo()
        vector_db.add_doubt(
            doubt_id=doubt_id,
            question=seed["question"],
            slide_id=seed["slide_id"],
            status=seed["status"],
            answer=seed["answer"]
        )
        
    print(f"Successfully seeded {len(sample_doubts)} doubts in the 'resolved_doubts' collection.")
    
    # 5. Create default active session
    session = SeminarSession(
        session_id="session_active",
        current_slide_id=0,
        is_active=True,
        is_waiting_for_doubts=False
    )
    session_repo.create(session)
    
    # Process speaker speech for slide 0
    orchestrator.process_slide(session, 0)
    print("Created active seminar session. Speaker speech generated for Slide 1.")
    print("=" * 60)
    print("Reset and seed completed! You can now launch run.py or inspect database.")
    print("=" * 60)

if __name__ == "__main__":
    reset_and_seed()
