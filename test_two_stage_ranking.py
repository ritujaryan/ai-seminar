import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

def run_verification():
    print("=" * 80)
    print("VERIFYING TWO-STAGE LLM RELEVANCY & DEDUPLICATION PIPELINE")
    print("=" * 80)
    
    # 1. Start Seminar
    slide_deck = {
        "title": "Introduction to Transformers & GenAI",
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
    print("Seminar session started successfully.\n")
    
    # 2. Submit student doubts
    doubts = [
        # Question 1: Relevant
        {"slide_id": 0, "question": "Can you explain why parallel processing makes Transformers faster than LSTMs?"},
        # Question 2: Duplicate of Question 1 (semantically same)
        {"slide_id": 0, "question": "Why are Transformers faster to train than LSTMs?"},
        # Question 3: Relevant & unique
        {"slide_id": 0, "question": "What are Query, Key, and Value vectors in self-attention?"},
        # Question 4: Off-topic but contains matching keyword "transformer"
        {"slide_id": 0, "question": "What is the standard winding ratio of an electrical step-up transformer?"}
    ]
    
    print("Step 2: Submitting student doubts...")
    for doubt in doubts:
        res = requests.post(f"{BASE_URL}/doubts/submit", json=doubt)
        if res.status_code == 200:
            print(f"  [+] Submitted: \"{doubt['question']}\"")
        else:
            print(f"  [-] Failed: \"{doubt['question']}\" - {res.text}")
            
    # 3. Query the rank endpoint
    print("\nStep 3: Querying the Two-Stage Rank API (fetching Top 3)...")
    res = requests.get(f"{BASE_URL}/doubts/slide/0/rank?top_n=3&global_pool=true")
    if res.status_code != 200:
        print("Failed to rank doubts:", res.text)
        return
        
    ranked_results = res.json()
    
    print("\n" + "=" * 80)
    print("TWO-STAGE RANKING RESULTS FROM LLM")
    print("=" * 80)
    for idx, d in enumerate(ranked_results):
        print(f"[{idx+1}] Question: \"{d['question']}\"")
        print(f"    Category: {d['category']}")
        print(f"    Similarity/Priority Score: {d['similarity_score']:.4f}")
        print(f"    Message: {d['message']}")
        print()
    print("=" * 80)

if __name__ == "__main__":
    run_verification()
