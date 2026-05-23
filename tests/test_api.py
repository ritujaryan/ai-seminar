import os
# Force mock provider to avoid live API token usage during tests
os.environ["LLM_PROVIDER"] = "mock"

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.repositories.slide_repository import slide_repo
from app.repositories.doubt_repository import doubt_repo
from app.repositories.session_repository import session_repo

client = TestClient(app)

@pytest.fixture(autouse=True)
def cleanup_repos():
    # Clean up before and after each test
    slide_repo.clear()
    doubt_repo.clear()
    session_repo.clear()
    yield
    slide_repo.clear()
    doubt_repo.clear()
    session_repo.clear()

def test_start_seminar():
    payload = {
        "title": "Test AI Seminar",
        "slides": [
            {
                "slide_id": 0,
                "title": "Introduction",
                "content": "This is slide 1 content.",
                "notes": "Intro speech notes.",
                "wait_for_doubts": False
            },
            {
                "slide_id": 1,
                "title": "Deep Architecture",
                "content": "This is slide 2 content.",
                "notes": "Deep details. Wait for questions here.",
                "wait_for_doubts": True
            }
        ]
    }
    
    response = client.post("/api/v1/seminar/start", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["session_id"] == "session_active"
    assert data["current_slide_id"] == 0
    assert data["is_active"] is True
    assert data["is_waiting_for_doubts"] is False  # Slide 0 doesn't wait

def test_seminar_status():
    # Ingest seminar
    test_start_seminar()
    
    response = client.get("/api/v1/seminar/status")
    assert response.status_code == 200
    data = response.json()
    assert data["current_slide_id"] == 0
    assert data["title"] == "Introduction"
    assert "Intro speech notes" in data["speech_generated"]

def test_doubt_submission():
    # Start seminar where Slide 0 has wait_for_doubts = False and Slide 1 has wait_for_doubts = True
    test_start_seminar()
    
    # 1. Submit doubt for Slide 0 (should fail because wait_for_doubts is False)
    response = client.post("/api/v1/doubts/submit", json={"slide_id": 0, "question": "What is intro?"})
    assert response.status_code == 400
    assert "not enabled" in response.json()["detail"]
    
    # 2. Advance to slide 1
    response = client.post("/api/v1/seminar/next")
    assert response.status_code == 200
    assert response.json()["current_slide_id"] == 1
    assert response.json()["is_waiting_for_doubts"] is True
    
    # 3. Submit doubt for Slide 1 (should succeed)
    response = client.post("/api/v1/doubts/submit", json={"slide_id": 1, "question": "Explain deep architecture?"})
    assert response.status_code == 200
    data = response.json()
    assert data["slide_id"] == 1
    assert data["question"] == "Explain deep architecture?"
    assert data["status"] == "pending"
    
    # 4. Try submitting doubt for slide 0 while slide 1 is active (should fail)
    response = client.post("/api/v1/doubts/submit", json={"slide_id": 0, "question": "Intro question again?"})
    assert response.status_code == 400
    assert "must match current active slide" in response.json()["detail"]

def test_advance_and_resolve():
    test_start_seminar()
    
    # Move to slide 1
    client.post("/api/v1/seminar/next")
    
    # Submit 2 doubts on slide 1
    client.post("/api/v1/doubts/submit", json={"slide_id": 1, "question": "Question A"})
    client.post("/api/v1/doubts/submit", json={"slide_id": 1, "question": "Question B"})
    
    # Let's verify doubts are pending
    response = client.get("/api/v1/doubts/slide/1")
    assert len(response.json()) == 2
    assert all(d["status"] == "pending" for d in response.json())
    
    # Force resolve doubts manually
    response = client.post("/api/v1/seminar/resolve-doubts")
    assert response.status_code == 200
    assert response.json()["is_waiting_for_doubts"] is False  # Cleared wait flag
    
    # Verify doubts are approved/resolved
    response = client.get("/api/v1/doubts/slide/1/resolved")
    assert len(response.json()) == 2
    assert all(d["status"] == "approved" for d in response.json())
    assert "Resolved during QA" in response.json()[0]["answer"]

def test_rank_doubts():
    test_start_seminar()
    
    # Move to slide 1
    client.post("/api/v1/seminar/next")
    
    # Submit doubts with varying relevance to slide 1
    # 1. Relevant to current slide (Slide 1) - Candidate A
    client.post("/api/v1/doubts/submit", json={"slide_id": 1, "question": "What are the deep details of the architecture?"})
    # 2. Relevant to current slide (Slide 1) - Candidate B
    client.post("/api/v1/doubts/submit", json={"slide_id": 1, "question": "Tell me about the deep architecture features?"})
    # 3. Relevant to past slide (Slide 0)
    client.post("/api/v1/doubts/submit", json={"slide_id": 1, "question": "What is the intro speech about?"})
    # 4. Completely irrelevant
    client.post("/api/v1/doubts/submit", json={"slide_id": 1, "question": "Which apple is the sweetest?"})
    
    # Query ranked doubts
    response = client.get("/api/v1/doubts/slide/1/rank?top_n=1&global_pool=true")
    assert response.status_code == 200
    data = response.json()
    
    assert len(data) == 4
    
    # 1. Top N relevant
    assert data[0]["category"] == "top_n"
    assert ("deep details" in data[0]["question"].lower() or "deep architecture" in data[0]["question"].lower())
    
    # 2. Low priority (relevant but not in top 1)
    assert data[1]["category"] == "low_priority"
    assert ("deep details" in data[1]["question"].lower() or "deep architecture" in data[1]["question"].lower())
    assert data[1]["message"] == "less relevant hence low priority"
    
    # 3. Different slide (covered in slide 0)
    assert data[2]["category"] == "diff_slide"
    assert "intro" in data[2]["question"].lower()
    assert data[2]["message"] == "covered in slide(0)"
    
    # 4. Not relevant to PPT
    assert data[3]["category"] == "not_relevant_to_ppt"
    assert "apple" in data[3]["question"].lower()
    assert data[3]["message"] == "Not relevant to PPT"


def test_two_stage_llm_ranking(monkeypatch):
    # 1. Start Seminar
    test_start_seminar()
    
    # Move to slide 1
    client.post("/api/v1/seminar/next")
    
    # 2. Submit doubts on slide 1
    # Doubt 1: Main question
    res1 = client.post("/api/v1/doubts/submit", json={"slide_id": 1, "question": "What is deep architecture?"})
    doubt_1_id = res1.json()["doubt_id"]
    
    # Doubt 2: Duplicate of Doubt 1
    res2 = client.post("/api/v1/doubts/submit", json={"slide_id": 1, "question": "Explain deep architecture features?"})
    doubt_2_id = res2.json()["doubt_id"]
    
    # Doubt 3: Off-topic question
    res3 = client.post("/api/v1/doubts/submit", json={"slide_id": 1, "question": "What is the capital of France?"})
    doubt_3_id = res3.json()["doubt_id"]

    # 3. Mock the get_llm function to return a mock LLM that resolves with the expected JSON evaluation
    class MockLLMInstance:
        def call(self, messages, **kwargs):
            eval_response = {
                "evaluations": [
                    {
                        "doubt_id": doubt_1_id,
                        "is_relevant": True,
                        "duplicate_of": None,
                        "priority_score": 9
                    },
                    {
                        "doubt_id": doubt_2_id,
                        "is_relevant": True,
                        "duplicate_of": doubt_1_id,
                        "priority_score": 3
                    },
                    {
                        "doubt_id": doubt_3_id,
                        "is_relevant": False,
                        "duplicate_of": None,
                        "priority_score": 1
                    }
                ]
            }
            return f"```json\n{json.dumps(eval_response)}\n```"

    import json
    from app.agents import crew
    monkeypatch.setattr(crew, "get_llm", lambda: MockLLMInstance())

    # 4. Query Ranked doubts
    response = client.get("/api/v1/doubts/slide/1/rank?top_n=1&global_pool=true")
    assert response.status_code == 200
    data = response.json()

    # Map results by doubt_id for easy assertions
    res_map = {d["doubt_id"]: d for d in data}

    # Assertions:
    # Doubt 1 should be Top N
    assert res_map[doubt_1_id]["category"] == "top_n"
    assert res_map[doubt_1_id]["message"] == "Top N relevant"

    # Doubt 2 should be low priority due to duplicate classification
    assert res_map[doubt_2_id]["category"] == "low_priority"
    assert res_map[doubt_2_id]["message"] == "Duplicate of another question"

    # Doubt 3 should be not relevant due to LLM filtering
    assert res_map[doubt_3_id]["category"] == "not_relevant_to_ppt"
    assert res_map[doubt_3_id]["message"] == "Filtered by LLM: Off-topic"


