import requests
import json
import time

def load_data():
    base_url = "http://localhost:8000/api/v1"
    
    # 1. Define the Docker & K8s presentation deck
    container_deck = {
        "title": "Modern Containerization & Kubernetes Orchestration",
        "slides": [
            {
                "slide_id": 0,
                "title": "Introduction to Containerization & Docker",
                "content": "Containers package code and dependencies together, sharing the host OS kernel. Docker provides the tooling to build, ship, and run these containers using simple Dockerfiles.",
                "notes": "Welcome the audience. Contrast containerization with traditional virtualization (VMs). Emphasize that VMs require a guest OS while containers do not, leading to lower overhead.",
                "wait_for_doubts": False
            },
            {
                "slide_id": 1,
                "title": "Writing Optimized Dockerfiles",
                "content": "Docker images are built using layered instructions. Optimization involves reducing layer counts, using multi-stage builds, pinning base image versions, and running as non-root users.",
                "notes": "Show multi-stage build benefits. Explain layer caching behavior and how ordering instructions matters (e.g., COPY package.json before COPY source code).",
                "wait_for_doubts": True
            },
            {
                "slide_id": 2,
                "title": "Kubernetes Core Concepts & Pods",
                "content": "Kubernetes (K8s) is an orchestration platform. The smallest deployable unit is a Pod, which hosts one or more tightly coupled containers sharing networking and storage.",
                "notes": "Define orchestrator duties. Discuss Pod lifecycle, shared namespaces within a Pod, and why single-container pods are the most common pattern. Wait for doubts.",
                "wait_for_doubts": True
            },
            {
                "slide_id": 3,
                "title": "Managing State: Volumes & Persistent Volumes",
                "content": "Pods are ephemeral. Persistent Volume Claims (PVCs) decouple pod specifications from underlying storage systems (NFS, AWS EBS, local disk) to persist data across pod restarts.",
                "notes": "Explain the PV/PVC handshake. Discuss AccessModes (ReadWriteOnce, ReadOnlyMany, ReadWriteMany) and StorageClasses for dynamic provisioning.",
                "wait_for_doubts": True
            },
            {
                "slide_id": 4,
                "title": "Kubernetes Networking: Services & Ingress",
                "content": "Services expose Pods to the network via stable IPs. ClusterIP (internal), NodePort (external port), and LoadBalancer routes. Ingress manages external HTTP/HTTPS routing.",
                "notes": "Detail how Kube-Proxy configures iptables/IPVS. Discuss Ingress controllers (Nginx, Traefik) and routing rules based on path or hostname.",
                "wait_for_doubts": True
            },
            {
                "slide_id": 5,
                "title": "Scaling & Self-Healing: Deployments & HPA",
                "content": "Deployments manage ReplicaSets for declarative updates. Horizontal Pod Autoscaler (HPA) automatically adjusts replica counts based on CPU/memory usage or custom metrics.",
                "notes": "Show rolling update and rollback behavior. Explain readiness and liveness probes for self-healing (restarting dead or unresponsive pods).",
                "wait_for_doubts": False
            }
        ]
    }
    
    print("=" * 70)
    print("Seeding running FastAPI server with Docker & Kubernetes deck...")
    print("=" * 70)
    
    try:
        # Start seminar (active slide becomes 0)
        print("1. Starting seminar on running server...")
        r = requests.post(f"{base_url}/seminar/start", json=container_deck)
        if r.status_code != 200:
            print(f"Failed to start seminar: {r.text}")
            return
        print("   Seminar started successfully.")
        
        # Advance to Slide 2 (Core Concepts & Pods)
        print("\n2. Advancing active slide to Slide 1...")
        requests.post(f"{base_url}/seminar/next")
        print("   Advancing active slide to Slide 2...")
        requests.post(f"{base_url}/seminar/next")
        
        # Check active status
        status_r = requests.get(f"{base_url}/seminar/status")
        if status_r.status_code == 200:
            print(f"   Active slide is now: {status_r.json()['current_slide_id']} ({status_r.json()['title']})")
        
        # Submit realistic doubts to slide 2
        realistic_doubts = [
            # Slide 0 related
            "How do Docker containers compare to Virtual Machines in terms of overhead and startup time?",
            # Slide 1 related
            "Why should we use multi-stage builds instead of simple single-stage Dockerfiles?",
            "How does Docker caching handle package installs when package.json hasn't changed?",
            "What is the best way to secure Docker images against root access exploits?",
            # Slide 2 related (Current)
            "Can two containers inside the same Kubernetes Pod communicate via localhost?",
            "What happens to a Pod when the Node hosting it crashes?",
            "Is it possible to share environment variables between containers in a single Pod?",
            # Slide 3 related
            "How does a Persistent Volume Claim dynamic provisioning work with AWS or GCP?",
            "Can multiple pods write to the same Persistent Volume simultaneously using ReadWriteOnce?",
            # Slide 4 related
            "What is the difference between NodePort and LoadBalancer services in Kubernetes?",
            "How does an Ingress Controller route traffic compared to a standard Service?",
            # Slide 5 related
            "What is the difference between Liveness and Readiness probes in Kubernetes Deployments?",
            # Irrelevant
            "How do you bake a sourdough bread step-by-step?",
            "What is the syntax for defining a class-based view in Django?",
            "Is Python or JavaScript better for web development?"
        ]
        
        print("\n3. Submitting 15 realistic questions...")
        for doubt in realistic_doubts:
            requests.post(f"{base_url}/doubts/submit", json={"slide_id": 2, "question": doubt})
            
        print("   All doubts submitted successfully.")
        
        # Test Query
        print("\n4. Testing GET /api/v1/doubts/slide/2/rank?top_n=2&global_pool=true...")
        rank_r = requests.get(f"{base_url}/doubts/slide/2/rank?top_n=2&global_pool=true")
        if rank_r.status_code == 200:
            ranked = rank_r.json()
            print(f"   Success! Found {len(ranked)} doubts classified.")
            print(f"   Top 1 doubt: \"{ranked[0]['question']}\"")
            print(f"       Category: {ranked[0]['category']}")
            print(f"       Message: {ranked[0]['message']}")
            print(f"   Irrelevant doubt (Sourdough):")
            sourdough = next((d for d in ranked if "sourdough" in d["question"]), None)
            if sourdough:
                print(f"       Question: \"{sourdough['question']}\"")
                print(f"       Category: {sourdough['category']}")
                print(f"       Message: {sourdough['message']}")
        else:
            print(f"Failed to query rank endpoint: {rank_r.text}")
            
        print("\n" + "=" * 70)
        print("Database and memory updated successfully. Visit http://localhost:8000/ to view.")
        print("=" * 70)
        
    except Exception as e:
        print(f"Connection error: {e}. Is the server running?")

if __name__ == "__main__":
    load_data()
