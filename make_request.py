import json
from fastapi.testclient import TestClient
from app.main import app
from app.repositories.slide_repository import slide_repo
from app.models.slide import Slide

def run_api_request():
    print("=" * 75)
    print("Simulating RAG Seminar System API calls without wiping seeded doubts...")
    print("=" * 75)
    
    # 1. Populate the in-memory SlideRepository directly
    # This avoids calling /seminar/start which would wipe our seeded doubts in ChromaDB.
    demo_slides = [
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
    
    slide_repo.clear()
    slide_repo.deck_title = "Building Production-Grade RAG Systems"
    for slide in demo_slides:
        slide_repo.create(slide)
    
    print("In-memory SlideRepository successfully seeded.")
    
    # 2. Initialize FastAPI TestClient
    client = TestClient(app)
    
    # 3. Retrieve all slides from the deck via API
    print("Retrieving all slides via API (GET /api/v1/slides/)...")
    slides_response = client.get("/api/v1/slides/")
    if slides_response.status_code != 200:
        print(f"Failed to fetch slides: {slides_response.text}")
        return
        
    slides = slides_response.json()
    print(f"Found {len(slides)} slides in the presentation deck.\n")
    
    # 4. Iterate through each slide and fetch Top 2 RAG-ranked questions
    for slide in slides:
        slide_id = slide["slide_id"]
        title = slide["title"]
        print("-" * 75)
        print(f"SLIDE {slide_id}: {title}")
        print(f"Content: {slide['content']}")
        print("-" * 75)
        
        # Query ranked questions from the global pool of doubts (global_pool=true)
        # Fetch top 2 most semantically relevant questions using RAG
        response = client.get(f"/api/v1/doubts/slide/{slide_id}/rank?top_n=2&global_pool=true")
        
        if response.status_code == 200:
            ranked_doubts = response.json()
            if not ranked_doubts:
                print("  No doubts found in database.")
            else:
                print("  RAG-Ranked doubt analysis results:")
                for idx, doubt in enumerate(ranked_doubts):
                    print(f"    [{idx + 1}] Question: \"{doubt['question']}\"")
                    print(f"        Category: {doubt['category']} (Similarity Score: {doubt['similarity_score']:.4f})")
                    if doubt['message']:
                        print(f"        Message: {doubt['message']}")
                    print(f"        Status: {doubt['status']}")
                    print(f"        Answer: {doubt['answer'] or 'Pending'}")
                    print()
        else:
            print(f"  Failed to retrieve ranked questions: Status {response.status_code}")
            print(f"  Detail: {response.text}")
        print()
        
    print("=" * 75)

if __name__ == "__main__":
    run_api_request()
