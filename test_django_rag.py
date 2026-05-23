import json
from fastapi.testclient import TestClient
from app.main import app
from app.repositories.slide_repository import slide_repo
from app.repositories.doubt_repository import doubt_repo
from app.repositories.session_repository import session_repo
from app.repositories.vector_repository import get_vector_repo
from app.services.rag_service import rag_service
from app.models.slide import Slide

def run_django_test():
    print("=" * 80)
    print("DEMO: Loading Django Web Framework Slide Deck & Testing RAG Categorization")
    print("=" * 80)

    # 1. Reset database state
    print("Clearing database repositories and vector collection...")
    slide_repo.clear()
    doubt_repo.clear()
    session_repo.clear()
    vector_db = get_vector_repo()
    vector_db.clear()

    # 2. Ingest 5 Django-related slides
    django_slides = [
        Slide(
            slide_id=0,
            title="Django MVT Architecture",
            content="Django is a high-level Python web framework that follows the Model-View-Template (MVT) pattern. The Model handles data, the Template handles UI, and the View bridges them by processing HTTP requests.",
            notes="Discuss MVT structure, comparison to MVC, request-response cycle, and lightweight settings.",
            wait_for_doubts=False
        ),
        Slide(
            slide_id=1,
            title="Django Models & ORM",
            content="Django ORM maps Python classes to database tables. It handles transactions, complex QuerySets, relational fields (ForeignKey, ManyToMany), and automatic migrations.",
            notes="Emphasize migrations (makemigrations/migrate), lazy loading, QuerySet filtering, and optimization with select_related.",
            wait_for_doubts=True
        ),
        Slide(
            slide_id=2,
            title="Django Views & URL Routing",
            content="Views process HTTP requests and return HTTP responses. Django supports both function-based views (FBVs) and class-based views (CBVs). URLconf routes URLs to specific views.",
            notes="Explain FBVs vs CBVs, routing patterns, path/re_path converters, and view decorators. Wait for doubts here.",
            wait_for_doubts=True
        ),
        Slide(
            slide_id=3,
            title="Django Forms & Validation",
            content="Django Forms validate and sanitize incoming user data. The clean() method checks field criteria, defends against CSRF attacks, and maps form inputs back to ORM model instances.",
            notes="Cover standard Forms, ModelForms, field validation hooks, clean() overrides, and form rendering in HTML templates.",
            wait_for_doubts=True
        ),
        Slide(
            slide_id=4,
            title="Django REST Framework (DRF)",
            content="DRF extends Django to build Web APIs. It provides Serializers to translate ORM models to JSON, ViewSets for resource routes, and built-in Token/JWT Authentication.",
            notes="Talk about REST API principles, Serializers vs ModelSerializers, routers, ViewSets, and API view decorators.",
            wait_for_doubts=False
        )
    ]

    slide_repo.deck_title = "Building Robust Web Apps with Django"
    for slide in django_slides:
        slide_repo.create(slide)

    rag_service.index_deck(django_slides)
    print("Django slide deck ingested and indexed successfully.")

    # 3. Setup FastAPI TestClient
    client = TestClient(app)

    # 4. Submit specific doubts for testing
    # Active slide is Slide 2 (Views and URL Routing)
    from app.models.session import SeminarSession
    session = SeminarSession(
        session_id="session_active",
        current_slide_id=2,
        is_active=True,
        is_waiting_for_doubts=True
    )
    session_repo.create(session)

    test_doubts = [
        # Slide 2 Match (Current Slide)
        {"slide_id": 2, "question": "Explain the difference between class-based views and function-based views."},
        # Slide 1 Matches (Past Slide)
        {"slide_id": 2, "question": "How do database migrations work in Django?"},
        {"slide_id": 2, "question": "Can we use raw SQL queries instead of Django ORM QuerySets?"},
        # Slide 3 Match (Future Slide)
        {"slide_id": 2, "question": "How does the clean() method validate fields in Django forms?"},
        # Slide 4 Match (Future Slide)
        {"slide_id": 2, "question": "What are serializers in Django REST Framework used for?"},
        # Irrelevant (Completely unrelated topic)
        {"slide_id": 2, "question": "Which apple is the sweetest fruit?"},
        # Irrelevant (RAG-related, but irrelevant to a Django PPT)
        {"slide_id": 2, "question": "What embedding model is used by default in RAG?"}
    ]

    print("Submitting Django-themed doubts to active Slide 2...")
    for doubt in test_doubts:
        response = client.post("/api/v1/doubts/submit", json=doubt)
        if response.status_code != 200:
            print(f"Failed to submit doubt: {response.text}")
            return

    print("Doubts successfully submitted.")

    # 5. Retrieve Top 1 ranked doubt for Slide 2
    print("\n" + "=" * 80)
    print("RANKING DOUBTS FOR SLIDE 2 (top_n = 1, global_pool = true)")
    print("=" * 80)

    response = client.get("/api/v1/doubts/slide/2/rank?top_n=1&global_pool=true")
    if response.status_code == 200:
        ranked_doubts = response.json()
        print(json.dumps(ranked_doubts, indent=2))
    else:
        print(f"Failed: {response.text}")
    print("=" * 80)

if __name__ == "__main__":
    run_django_test()
