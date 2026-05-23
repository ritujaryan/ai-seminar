import requests
import json
import time

BASE_URL = "http://localhost:8000/api/v1"

def test_flow():
    print("=" * 70)
    print("TESTING LIVE GEMINI AGENT WORKFLOW VIA FASTAPI")
    print("=" * 70)
    
    # 1. Start Seminar
    slide_deck = {
        "title": "Introduction to AI & Large Language Models",
        "slides": [
            {
                "slide_id": 0,
                "title": "What is a Transformer model?",
                "content": "The Transformer architecture uses self-attention mechanisms to process sequence input in parallel, replacing sequential LSTM structures.",
                "notes": "Explain self-attention, query-key-value vectors, and parallel training speeds. We wait for student doubts on this slide.",
                "wait_for_doubts": True
            }
        ]
    }
    
    print("Step 1: Starting seminar session...")
    res = requests.post(f"{BASE_URL}/seminar/start", json=slide_deck)
    if res.status_code != 200:
        print("Failed to start seminar:", res.text)
        return
    print("Seminar session started successfully:", res.json()["session_id"])
    
    # 2. Submit Doubts
    print("\nStep 2: Submitting student doubts...")
    doubt_1 = {
        "slide_id": 0,
        "question": "Can you explain why parallel processing makes Transformers faster than LSTMs?"
    }
    doubt_2 = {
        "slide_id": 0,
        "question": "What are Query, Key, and Value vectors in self-attention?"
    }
    
    for doubt in [doubt_1, doubt_2]:
        res = requests.post(f"{BASE_URL}/doubts/submit", json=doubt)
        if res.status_code == 200:
            print(f"  - Submitted: '{doubt['question']}'")
        else:
            print(f"  - Failed to submit '{doubt['question']}':", res.text)
            
    # 3. Force Resolve Doubts (Triggering Gemini agents)
    print("\nStep 3: Triggering Maker-Checker-Reviewer Agents to resolve doubts...")
    print("(This will take a few seconds as Gemini processes the QA)...")
    t0 = time.time()
    res = requests.post(f"{BASE_URL}/seminar/resolve-doubts")
    duration = time.time() - t0
    if res.status_code != 200:
        print("Failed to resolve doubts:", res.text)
        return
        
    print(f"Agentic resolution completed in {duration:.2f} seconds.")
    
    # 4. Fetch Resolved Doubts
    print("\nStep 4: Fetching resolved doubts from the API...")
    res = requests.get(f"{BASE_URL}/doubts/slide/0/resolved")
    if res.status_code != 200:
        print("Failed to fetch resolved doubts:", res.text)
        return
        
    resolved_doubts = res.json()
    print("-" * 70)
    print(f"RESOLVED DOUBTS ({len(resolved_doubts)}):")
    print("-" * 70)
    for idx, d in enumerate(resolved_doubts):
        print(f"[{idx+1}] Question: {d['question']}")
        print(f"    Status: {d['status']}")
        print(f"    Answer: {d['answer']}")
        print()
    print("=" * 70)

if __name__ == "__main__":
    test_flow()
