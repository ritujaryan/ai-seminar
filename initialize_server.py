import requests
import time

def initialize():
    demo_deck = {
        "title": "Building Production-Grade RAG Systems",
        "slides": [
            {
                "slide_id": 0,
                "title": "The RAG Architecture",
                "content": "Retrieval-Augmented Generation (RAG) resolves LLM limitations (hallucinations, static knowledge) by injecting relevant facts fetched from external document search engines at query time.",
                "notes": "Welcome everyone to our technical seminar. Explain that LLMs are like smart students with a dictionary but no internet access, and RAG provides them with a search engine. We do not wait for doubts here.",
                "wait_for_doubts": False
            },
            {
                "slide_id": 1,
                "title": "Vector Embeddings & Semantic Search",
                "content": "Documents are split into chunks, transformed into high-dimensional numerical vectors (embeddings), and stored in a Vector Database (like ChromaDB). Semantic search compares vectors using cosine distance.",
                "notes": "Emphasize that keyword searches fail on concepts, whereas embeddings capture meaning (e.g. 'feline' matching 'cat'). Wait for doubts here to address vector dimensions, chunking strategies, or database indexing.",
                "wait_for_doubts": True
            },
            {
                "slide_id": 2,
                "title": "Optimizing RAG Performance",
                "content": "Production challenges require advanced strategies: Parent-Document Retrieval, Sentence-Window retrieval, metadata filtering, and re-ranking models (like Cohere Rerank) to filter out noise.",
                "notes": "Explain that raw chunks often lose context, which is why windowing or parent-child chunks are used. Wait for doubts here so the audience can ask about indexing speeds, cost, or retrieval accuracy.",
                "wait_for_doubts": True
            },
            {
                "slide_id": 3,
                "title": "The Multi-Agent Orchestration Layer",
                "content": "Instead of a single flow, CrewAI uses autonomous agents (Maker, Checker, Reviewer) to collaborate. The RAG output is verified for quality and formatted into professional slide speech.",
                "notes": "Conclude by showing how agents verify the answers to avoid any hallucinations. This Maker-Checker approach ensures maximum accuracy for live events. Do not wait for doubts.",
                "wait_for_doubts": False
            }
        ]
    }
    
    base_url = "http://localhost:8000/api/v1"
    
    try:
        # 1. Start seminar (active slide = 0)
        print("Starting seminar (setting active slide to 0)...")
        r = requests.post(f"{base_url}/seminar/start", json=demo_deck)
        if r.status_code != 200:
            print(f"Failed to start: {r.text}")
            return
            
        # 2. Advance to slide 1
        print("Advancing to Slide 1...")
        r = requests.post(f"{base_url}/seminar/next")
        if r.status_code != 200:
            print(f"Failed to advance to slide 1: {r.text}")
            return
            
        # 3. Submit doubts for Slide 1
        slide_1_doubts = [
            "What embedding model is used by default?",
            "How does Cosine Similarity differ from L2 distance?",
            "Are new slides automatically indexed?"
        ]
        for q in slide_1_doubts:
            print(f"Submitting doubt for Slide 1: '{q}'")
            requests.post(f"{base_url}/doubts/submit", json={"slide_id": 1, "question": q})
            
        # 4. Advance to slide 2
        print("Advancing to Slide 2...")
        r = requests.post(f"{base_url}/seminar/next")
        if r.status_code != 200:
            print(f"Failed to advance to slide 2: {r.text}")
            return
            
        # 5. Submit doubt for Slide 2
        slide_2_doubts = [
            "What is a Re-ranking model?"
        ]
        for q in slide_2_doubts:
            print(f"Submitting doubt for Slide 2: '{q}'")
            requests.post(f"{base_url}/doubts/submit", json={"slide_id": 2, "question": q})
            
        print("\nSuccessfully initialized slides and doubts on running server!")
        
    except Exception as e:
        print(f"Connection error: {e}")

if __name__ == "__main__":
    initialize()
