import json
from fastapi.testclient import TestClient
from app.main import app
from app.repositories.slide_repository import slide_repo
from app.repositories.doubt_repository import doubt_repo
from app.repositories.session_repository import session_repo
from app.repositories.vector_repository import get_vector_repo
from app.services.rag_service import rag_service
from app.models.slide import Slide

def run_container_seminar():
    print("=" * 80)
    print("DEMO: Loading Docker & Kubernetes Containerization Seminar Deck")
    print("=" * 80)

    # 1. Reset database state
    print("Clearing database repositories and vector collection...")
    slide_repo.clear()
    doubt_repo.clear()
    session_repo.clear()
    vector_db = get_vector_repo()
    vector_db.clear()

    # 2. Ingest 6 Docker & K8s slides
    container_slides = [
        Slide(
            slide_id=0,
            title="Introduction to Containerization & Docker",
            content="Containers package code and dependencies together, sharing the host OS kernel. Docker provides the tooling to build, ship, and run these containers using simple Dockerfiles.",
            notes="Welcome the audience. Contrast containerization with traditional virtualization (VMs). Emphasize that VMs require a guest OS while containers do not, leading to lower overhead.",
            wait_for_doubts=False
        ),
        Slide(
            slide_id=1,
            title="Writing Optimized Dockerfiles",
            content="Docker images are built using layered instructions. Optimization involves reducing layer counts, using multi-stage builds, pinning base image versions, and running as non-root users.",
            notes="Show multi-stage build benefits. Explain layer caching behavior and how ordering instructions matters (e.g., COPY package.json before COPY source code).",
            wait_for_doubts=True
        ),
        Slide(
            slide_id=2,
            title="Kubernetes Core Concepts & Pods",
            content="Kubernetes (K8s) is an orchestration platform. The smallest deployable unit is a Pod, which hosts one or more tightly coupled containers sharing networking and storage.",
            notes="Define orchestrator duties. Discuss Pod lifecycle, shared namespaces within a Pod, and why single-container pods are the most common pattern. Wait for doubts.",
            wait_for_doubts=True
        ),
        Slide(
            slide_id=3,
            title="Managing State: Volumes & Persistent Volumes",
            content="Pods are ephemeral. Persistent Volume Claims (PVCs) decouple pod specifications from underlying storage systems (NFS, AWS EBS, local disk) to persist data across pod restarts.",
            notes="Explain the PV/PVC handshake. Discuss AccessModes (ReadWriteOnce, ReadOnlyMany, ReadWriteMany) and StorageClasses for dynamic provisioning.",
            wait_for_doubts=True
        ),
        Slide(
            slide_id=4,
            title="Kubernetes Networking: Services & Ingress",
            content="Services expose Pods to the network via stable IPs. ClusterIP (internal), NodePort (external port), and LoadBalancer routes. Ingress manages external HTTP/HTTPS routing.",
            notes="Detail how Kube-Proxy configures iptables/IPVS. Discuss Ingress controllers (Nginx, Traefik) and routing rules based on path or hostname.",
            wait_for_doubts=True
        ),
        Slide(
            slide_id=5,
            title="Scaling & Self-Healing: Deployments & HPA",
            content="Deployments manage ReplicaSets for declarative updates. Horizontal Pod Autoscaler (HPA) automatically adjusts replica counts based on CPU/memory usage or custom metrics.",
            notes="Show rolling update and rollback behavior. Explain readiness and liveness probes for self-healing (restarting dead or unresponsive pods).",
            wait_for_doubts=False
        )
    ]

    slide_repo.deck_title = "Modern Containerization & Kubernetes Orchestration"
    for slide in container_slides:
        slide_repo.create(slide)

    rag_service.index_deck(container_slides)
    print("Docker & K8s slide deck ingested and indexed successfully.")

    # 3. Setup FastAPI TestClient
    client = TestClient(app)

    # 4. Set current active session to Slide 2 (Pods)
    from app.models.session import SeminarSession
    session = SeminarSession(
        session_id="session_active",
        current_slide_id=2,
        is_active=True,
        is_waiting_for_doubts=True
    )
    session_repo.create(session)

    # 5. Seed realistic doubts
    realistic_doubts = [
        # Questions for Slide 0 (Introduction - Past)
        {"slide_id": 2, "question": "How do Docker containers compare to Virtual Machines in terms of overhead and startup time?"},
        
        # Questions for Slide 1 (Dockerfiles - Past)
        {"slide_id": 2, "question": "Why should we use multi-stage builds instead of simple single-stage Dockerfiles?"},
        {"slide_id": 2, "question": "How does Docker caching handle package installs when package.json hasn't changed?"},
        {"slide_id": 2, "question": "What is the best way to secure Docker images against root access exploits?"},
        
        # Questions for Slide 2 (Pods - Current)
        {"slide_id": 2, "question": "Can two containers inside the same Kubernetes Pod communicate via localhost?"},
        {"slide_id": 2, "question": "What happens to a Pod when the Node hosting it crashes?"},
        {"slide_id": 2, "question": "Is it possible to share environment variables between containers in a single Pod?"},
        
        # Questions for Slide 3 (Volumes - Future)
        {"slide_id": 2, "question": "How does a Persistent Volume Claim dynamic provisioning work with AWS or GCP?"},
        {"slide_id": 2, "question": "Can multiple pods write to the same Persistent Volume simultaneously using ReadWriteOnce?"},
        
        # Questions for Slide 4 (Networking - Future)
        {"slide_id": 2, "question": "What is the difference between NodePort and LoadBalancer services in Kubernetes?"},
        {"slide_id": 2, "question": "How does an Ingress Controller route traffic compared to a standard Service?"},
        
        # Questions for Slide 5 (Scaling/Healing - Future)
        {"slide_id": 2, "question": "What is the difference between Liveness and Readiness probes in Kubernetes Deployments?"},
        
        # Irrelevant / Out of Scope questions
        {"slide_id": 2, "question": "How do you bake a sourdough bread step-by-step?"},
        {"slide_id": 2, "question": "What is the syntax for defining a class-based view in Django?"},
        {"slide_id": 2, "question": "Is Python or JavaScript better for web development?"}
    ]

    print("Submitting realistic container-related doubts...")
    for doubt in realistic_doubts:
        response = client.post("/api/v1/doubts/submit", json=doubt)
        if response.status_code != 200:
            print(f"Failed to submit doubt: {response.text}")
            return
    print("Doubts successfully submitted.")

    # 6. Retrieve ranked doubts for Slide 2 (Pods) with top_n = 2
    # This should yield:
    # - 2 doubts in top_n (representing Pods/localhost and Pod/node-crashes)
    # - 1 doubt in low_priority (environment variables sharing, since top_n is limited to 2)
    # - Many doubts in diff_slide (covered in slide 0, covered in slide 1, will be covered in next slide)
    # - 3 doubts in not_relevant_to_ppt (sourdough, django, python vs js)
    print("\n" + "=" * 80)
    print("RANKING DOUBTS FOR SLIDE 2: Pods (top_n = 2, global_pool = true)")
    print("=" * 80)

    response = client.get("/api/v1/doubts/slide/2/rank?top_n=2&global_pool=true")
    if response.status_code == 200:
        ranked_doubts = response.json()
        print(json.dumps(ranked_doubts, indent=2))
    else:
        print(f"Failed: {response.text}")
    print("=" * 80)

if __name__ == "__main__":
    run_container_seminar()
