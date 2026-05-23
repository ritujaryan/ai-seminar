import json
from fastapi.testclient import TestClient
from app.main import app
from app.repositories.slide_repository import slide_repo
from app.repositories.doubt_repository import doubt_repo
from app.repositories.session_repository import session_repo
from app.repositories.vector_repository import get_vector_repo
from app.services.rag_service import rag_service
from app.models.slide import Slide

def run_manual_verification():
    print("=" * 80)
    # 1. Reset database state
    print("Resetting all repositories and vector database...")
    slide_repo.clear()
    doubt_repo.clear()
    session_repo.clear()
    vector_db = get_vector_repo()
    vector_db.clear()

    # 2. Ingest 4 slides
    print("Ingesting slide deck...")
    demo_slides = [
        Slide(
            slide_id=0,
            title="The RAG Architecture",
            content="Retrieval-Augmented Generation (RAG) resolves LLM limitations (hallucinations, static knowledge) by injecting relevant facts fetched from external document search engines at query time.",
            notes="Welcome everyone. Intro to RAG.",
            wait_for_doubts=False
        ),
        Slide(
            slide_id=1,
            title="Vector Embeddings & Semantic Search",
            content="Documents are split into chunks, transformed into high-dimensional numerical vectors (embeddings), and stored in a Vector Database (like ChromaDB). Semantic search compares vectors using cosine distance.",
            notes="Details of vector spaces, cosine similarity, and database indexing.",
            wait_for_doubts=True
        ),
        Slide(
            slide_id=2,
            title="Optimizing RAG Performance",
            content="Production challenges require advanced strategies: Parent-Document Retrieval, Sentence-Window retrieval, metadata filtering, and re-ranking models (like Cohere Rerank) to filter out noise.",
            notes="Details on re-ranking, cross-encoders, and context windows.",
            wait_for_doubts=True
        ),
        Slide(
            slide_id=3,
            title="The Multi-Agent Orchestration Layer",
            content="Instead of a single flow, CrewAI uses autonomous agents to collaborate. The RAG output is verified for quality.",
            notes="Agent validation and speech generation.",
            wait_for_doubts=False
        )
    ]
    
    slide_repo.deck_title = "Building Production-Grade RAG Systems"
    for slide in demo_slides:
        slide_repo.create(slide)
    
    rag_service.index_deck(demo_slides)
    print("Slide deck ingested and indexed successfully.")

    # 3. Create FastAPI client
    client = TestClient(app)

    # 4. Submit specific doubts to setup cases
    # We want:
    # - 3 doubts matching Slide 1 best
    # - 1 doubt matching Slide 2 best
    # - 1 completely irrelevant doubt
    test_questions = [
        {"slide_id": 1, "question": "What embedding model is used for generating high-dimensional vectors?"}, # Slide 1 Match 1
        {"slide_id": 1, "question": "How does Cosine Similarity compare vectors in semantic search?"},      # Slide 1 Match 2
        {"slide_id": 1, "question": "Are documents split into chunks before vector embeddings?"},          # Slide 1 Match 3
        {"slide_id": 1, "question": "What is a Re-ranking model to filter out noise?"},                    # Slide 2 Match
        {"slide_id": 1, "question": "Which apple is the sweetest fruit?"}                                  # Irrelevant Match
    ]

    print("Submitting test questions...")
    for q_data in test_questions:
        # Since active slide in session must match, let's create active session at slide 1
        from app.models.session import SeminarSession
        session = SeminarSession(
            session_id="session_active",
            current_slide_id=1,
            is_active=True,
            is_waiting_for_doubts=True
        )
        session_repo.create(session)
        
        response = client.post("/api/v1/doubts/submit", json=q_data)
        if response.status_code != 200:
            print(f"Failed to submit: {response.text}")
            return
            
    print("Test questions submitted successfully.")

    # 5. Query Rank Endpoint for Slide 1 with top_n = 2
    print("\n" + "=" * 80)
    print("CASE STUDY 1: Ranking doubts for SLIDE 1 (top_n = 2, global_pool = true)")
    print("=" * 80)
    
    resp_slide_1 = client.get("/api/v1/doubts/slide/1/rank?top_n=2&global_pool=true")
    assert resp_slide_1.status_code == 200
    data_1 = resp_slide_1.json()

    print(json.dumps(data_1, indent=2))

    # 6. Query Rank Endpoint for Slide 2 with top_n = 2
    print("\n" + "=" * 80)
    print("CASE STUDY 2: Ranking doubts for SLIDE 2 (top_n = 2, global_pool = true)")
    print("=" * 80)
    
    resp_slide_2 = client.get("/api/v1/doubts/slide/2/rank?top_n=2&global_pool=true")
    assert resp_slide_2.status_code == 200
    data_2 = resp_slide_2.json()

    print(json.dumps(data_2, indent=2))
    print("=" * 80)

if __name__ == "__main__":
    run_manual_verification()
