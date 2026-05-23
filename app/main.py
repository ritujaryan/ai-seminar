from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import os
import uvicorn

from app.core.config import settings
from app.repositories.vector_repository import init_vector_repo
from app.api.v1.endpoints.slides import router as slides_router
from app.api.v1.endpoints.doubts import router as doubts_router
from app.api.v1.endpoints.seminar import router as seminar_router

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="AI Assistant based Seminar System with CrewAI, FastAPI, and RAG",
    version="1.0.0"
)

# Initialize vector db on startup
@app.on_event("startup")
async def startup_event():
    init_vector_repo(settings.CHROMA_PERSIST_DIR)

# Include API Routers
app.include_router(seminar_router, prefix=f"{settings.API_V1_STR}/seminar", tags=["seminar"])
app.include_router(slides_router, prefix=f"{settings.API_V1_STR}/slides", tags=["slides"])
app.include_router(doubts_router, prefix=f"{settings.API_V1_STR}/doubts", tags=["doubts"])

@app.get("/", response_class=HTMLResponse)
async def get_dashboard():
    """
    Renders a stunning modern dashboard for demoing the AI Seminar System.
    Includes glassmorphism UI, transitions, dark mode theme, slide controllers,
    doubt submission form, and live QA viewer.
    """
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>AI Seminar Control Center</title>
        <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=Plus+Jakarta+Sans:wght@300;400;500;600;700&display=swap" rel="stylesheet">
        <style>
            :root {
                --bg-gradient: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%);
                --glass-bg: rgba(30, 41, 59, 0.45);
                --glass-border: rgba(255, 255, 255, 0.08);
                --text-primary: #f8fafc;
                --text-secondary: #94a3b8;
                --accent-blue: #3b82f6;
                --accent-purple: #8b5cf6;
                --accent-gradient: linear-gradient(90deg, #3b82f6 0%, #8b5cf6 100%);
                --card-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
                --success: #10b981;
                --warning: #f59e0b;
            }

            * {
                box-sizing: border-box;
                margin: 0;
                padding: 0;
            }

            body {
                font-family: 'Plus Jakarta Sans', sans-serif;
                background: var(--bg-gradient);
                color: var(--text-primary);
                min-height: 100vh;
                display: flex;
                flex-direction: column;
                overflow-x: hidden;
            }

            header {
                backdrop-filter: blur(12px);
                -webkit-backdrop-filter: blur(12px);
                border-bottom: 1px solid var(--glass-border);
                background: rgba(15, 23, 42, 0.6);
                padding: 1.25rem 2rem;
                display: flex;
                justify-content: space-between;
                align-items: center;
                position: sticky;
                top: 0;
                z-index: 50;
            }

            .logo {
                font-family: 'Outfit', sans-serif;
                font-size: 1.5rem;
                font-weight: 800;
                background: var(--accent-gradient);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                display: flex;
                align-items: center;
                gap: 0.5rem;
            }

            .container {
                max-width: 1400px;
                margin: 2rem auto;
                padding: 0 1.5rem;
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 2rem;
                flex-grow: 1;
            }

            @media (max-width: 1024px) {
                .container {
                    grid-template-columns: 1fr;
                }
            }

            .card {
                background: var(--glass-bg);
                backdrop-filter: blur(16px);
                -webkit-backdrop-filter: blur(16px);
                border: 1px solid var(--glass-border);
                border-radius: 24px;
                padding: 2rem;
                box-shadow: var(--card-shadow);
                display: flex;
                flex-direction: column;
                gap: 1.5rem;
                transition: transform 0.3s ease, box-shadow 0.3s ease;
            }

            .card:hover {
                transform: translateY(-2px);
                box-shadow: 0 12px 40px 0 rgba(139, 92, 246, 0.1);
            }

            h2 {
                font-family: 'Outfit', sans-serif;
                font-size: 1.75rem;
                font-weight: 700;
                display: flex;
                align-items: center;
                gap: 0.75rem;
                border-bottom: 1px solid rgba(255, 255, 255, 0.05);
                padding-bottom: 0.75rem;
            }

            .btn-group {
                display: flex;
                gap: 1rem;
            }

            button, .btn {
                background: var(--accent-gradient);
                color: white;
                border: none;
                padding: 0.8rem 1.5rem;
                border-radius: 12px;
                font-weight: 600;
                cursor: pointer;
                font-family: inherit;
                transition: all 0.2s ease;
                display: inline-flex;
                align-items: center;
                justify-content: center;
                gap: 0.5rem;
                box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
            }

            button:hover, .btn:hover {
                opacity: 0.9;
                transform: translateY(-1px);
                box-shadow: 0 6px 16px rgba(139, 92, 246, 0.4);
            }

            button:active {
                transform: translateY(1px);
            }

            button.secondary {
                background: rgba(255, 255, 255, 0.08);
                color: var(--text-primary);
                border: 1px solid var(--glass-border);
                box-shadow: none;
            }

            button.secondary:hover {
                background: rgba(255, 255, 255, 0.15);
            }

            .slide-view {
                background: rgba(15, 23, 42, 0.4);
                border-radius: 16px;
                padding: 1.5rem;
                border: 1px solid rgba(255, 255, 255, 0.03);
            }

            .slide-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 1rem;
            }

            .badge {
                font-size: 0.75rem;
                text-transform: uppercase;
                padding: 0.35rem 0.75rem;
                border-radius: 50px;
                font-weight: 700;
                letter-spacing: 0.05em;
            }

            .badge-blue {
                background: rgba(59, 130, 246, 0.2);
                color: #60a5fa;
                border: 1px solid rgba(59, 130, 246, 0.3);
            }

            .badge-purple {
                background: rgba(139, 92, 246, 0.2);
                color: #c084fc;
                border: 1px solid rgba(139, 92, 246, 0.3);
            }

            .badge-green {
                background: rgba(16, 185, 129, 0.2);
                color: #34d399;
                border: 1px solid rgba(16, 185, 129, 0.3);
            }

            .slide-title {
                font-size: 1.5rem;
                font-weight: 700;
                color: var(--text-primary);
                margin-bottom: 0.75rem;
            }

            .slide-body {
                line-height: 1.6;
                color: var(--text-secondary);
                font-size: 1rem;
                margin-bottom: 1rem;
            }

            .private-notes {
                border-top: 1px dashed rgba(255, 255, 255, 0.1);
                padding-top: 1rem;
                margin-top: 1rem;
            }

            .private-notes h4 {
                font-size: 0.9rem;
                color: var(--accent-purple);
                text-transform: uppercase;
                letter-spacing: 0.05em;
                margin-bottom: 0.5rem;
                display: flex;
                align-items: center;
                gap: 0.25rem;
            }

            .private-notes p {
                font-style: italic;
                color: #cbd5e1;
                font-size: 0.95rem;
            }

            .speech-area {
                background: linear-gradient(135deg, rgba(59, 130, 246, 0.1) 0%, rgba(139, 92, 246, 0.1) 100%);
                border-radius: 16px;
                padding: 1.5rem;
                border: 1px solid rgba(139, 92, 246, 0.2);
            }

            .speech-area h3 {
                font-size: 1rem;
                color: var(--text-primary);
                margin-bottom: 0.5rem;
                display: flex;
                align-items: center;
                gap: 0.5rem;
            }

            .form-group {
                display: flex;
                flex-direction: column;
                gap: 0.5rem;
            }

            label {
                font-size: 0.875rem;
                font-weight: 600;
                color: var(--text-secondary);
            }

            input, textarea, select {
                background: rgba(15, 23, 42, 0.5);
                border: 1px solid var(--glass-border);
                border-radius: 12px;
                padding: 0.8rem 1rem;
                color: var(--text-primary);
                font-family: inherit;
                font-size: 0.95rem;
                transition: all 0.2s ease;
            }

            input:focus, textarea:focus, select:focus {
                outline: none;
                border-color: var(--accent-blue);
                box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.2);
            }

            .doubts-list {
                display: flex;
                flex-direction: column;
                gap: 1rem;
                max-height: 400px;
                overflow-y: auto;
                padding-right: 0.5rem;
            }

            .doubt-card {
                background: rgba(255, 255, 255, 0.03);
                border-radius: 14px;
                padding: 1rem;
                border: 1px solid rgba(255, 255, 255, 0.05);
                display: flex;
                flex-direction: column;
                gap: 0.5rem;
            }

            .doubt-question {
                font-weight: 600;
                font-size: 0.95rem;
            }

            .doubt-answer {
                background: rgba(16, 185, 129, 0.05);
                border-left: 3px solid var(--success);
                padding: 0.5rem 0.75rem;
                font-size: 0.9rem;
                color: #a7f3d0;
                border-radius: 0 8px 8px 0;
            }

            .doubt-status-pending {
                border-left: 3px solid var(--warning);
            }

            .status-indicator {
                display: inline-block;
                width: 8px;
                height: 8px;
                border-radius: 50%;
                margin-right: 0.5rem;
            }

            .status-active {
                background-color: var(--success);
                box-shadow: 0 0 8px var(--success);
            }

            .status-waiting {
                background-color: var(--warning);
                box-shadow: 0 0 8px var(--warning);
            }

            footer {
                text-align: center;
                padding: 2rem;
                color: var(--text-secondary);
                font-size: 0.875rem;
                border-top: 1px solid var(--glass-border);
                margin-top: auto;
            }
        </style>
    </head>
    <body>
        <header>
            <div class="logo">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M12 2L2 7L12 12L22 7L12 2Z" stroke="url(#logoGrad)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                    <path d="M2 17L12 22L22 17" stroke="url(#logoGrad)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                    <path d="M2 12L12 17L22 12" stroke="url(#logoGrad)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                    <defs>
                        <linearGradient id="logoGrad" x1="2" y1="2" x2="22" y2="22" gradientUnits="userSpaceOnUse">
                            <stop offset="0%" stop-color="#3b82f6"/>
                            <stop offset="100%" stop-color="#8b5cf6"/>
                        </linearGradient>
                    </defs>
                </svg>
                AI Seminar Control Room
            </div>
            <div>
                <span id="session-badge" class="badge badge-purple">No Active Session</span>
            </div>
        </header>

        <div class="container">
            <!-- Left Side: Control & Slide View -->
            <div class="card">
                <h2>
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <rect x="3" y="3" width="18" height="18" rx="2" stroke="currentColor" stroke-width="2"/>
                        <path d="M9 17V7L16 12L9 17Z" fill="currentColor"/>
                    </svg>
                    Presentation Deck
                </h2>
                
                <div class="btn-group">
                    <button onclick="startDemoSeminar()">Initialize Demo Deck</button>
                    <button class="secondary" onclick="advanceSlide()" id="next-btn" disabled>Next Slide</button>
                    <button class="secondary" onclick="resolveDoubtsNow()" id="resolve-btn" disabled>Resolve Doubts</button>
                </div>

                <div class="slide-view" id="slide-viewer">
                    <p style="color: var(--text-secondary); text-align: center; font-style: italic;">
                        Click "Initialize Demo Deck" to start the seminar simulation.
                    </p>
                </div>

                <div class="speech-area" id="speech-viewer" style="display: none;">
                    <h3>
                        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                            <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"></path>
                            <path d="M19 10v2a7 7 0 0 1-14 0v-2"></path>
                            <line x1="12" y1="19" x2="12" y2="23"></line>
                            <line x1="8" y1="23" x2="16" y2="23"></line>
                        </svg>
                        AI Voice Assistant Script
                    </h3>
                    <p id="speech-text" style="line-height: 1.6; font-size: 0.95rem;"></p>
                </div>
            </div>

            <!-- Right Side: QA & Doubt Submission -->
            <div class="card">
                <h2>
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
                    </svg>
                    Audience Q&A
                </h2>

                <div class="form-group" id="doubt-form-area" style="opacity: 0.5; pointer-events: none;">
                    <label for="doubt-input">Post a Doubt (for current slide):</label>
                    <div style="display: flex; gap: 0.5rem;">
                        <input type="text" id="doubt-input" placeholder="Type your doubt here..." style="flex-grow: 1;">
                        <button onclick="submitDoubt()">Submit</button>
                    </div>
                </div>

                <div style="display: flex; flex-direction: column; gap: 0.5rem;">
                    <label>Live Doubts & Answers for Current Slide:</label>
                    <div class="doubts-list" id="doubts-list-container">
                        <p style="color: var(--text-secondary); text-align: center; font-style: italic; margin-top: 1rem;">
                            No doubts submitted yet.
                        </p>
                    </div>
                </div>
            </div>
        </div>

        <footer>
            AI Assistant Based Seminar System • Powered by FastAPI & CrewAI
        </footer>

        <script>
            let currentSlideId = 0;
            let sessionActive = false;
            let isWaitingForDoubts = false;

            async function startDemoSeminar() {
                const demoDeck = {
                    title: "Building Production-Grade RAG Systems",
                    slides: [
                        {
                            slide_id: 0,
                            title: "The RAG Architecture",
                            content: "Retrieval-Augmented Generation (RAG) resolves LLM limitations (hallucinations, static knowledge) by injecting relevant facts fetched from external document search engines at query time.",
                            notes: "Welcome everyone to our technical seminar. Explain that LLMs are like smart students with a dictionary but no internet access, and RAG provides them with a search engine. We do not wait for doubts here.",
                            wait_for_doubts: false
                        },
                        {
                            slide_id: 1,
                            title: "Vector Embeddings & Semantic Search",
                            content: "Documents are split into chunks, transformed into high-dimensional numerical vectors (embeddings), and stored in a Vector Database (like ChromaDB). Semantic search compares vectors using cosine distance.",
                            notes: "Emphasize that keyword searches fail on concepts, whereas embeddings capture meaning (e.g. 'feline' matching 'cat'). Wait for doubts here to address vector dimensions, chunking strategies, or database indexing.",
                            wait_for_doubts: true
                        },
                        {
                            slide_id: 2,
                            title: "Optimizing RAG Performance",
                            content: "Production challenges require advanced strategies: Parent-Document Retrieval, Sentence-Window retrieval, metadata filtering, and re-ranking models (like Cohere Rerank) to filter out noise.",
                            notes: "Explain that raw chunks often lose context, which is why windowing or parent-child chunks are used. Wait for doubts here so the audience can ask about indexing speeds, cost, or retrieval accuracy.",
                            wait_for_doubts: true
                        },
                        {
                            slide_id: 3,
                            title: "The Multi-Agent Orchestration Layer",
                            content: "Instead of a single flow, CrewAI uses autonomous agents (Maker, Checker, Reviewer) to collaborate. The RAG output is verified for quality and formatted into professional slide speech.",
                            notes: "Conclude by showing how agents verify the answers to avoid any hallucinations. This Maker-Checker approach ensures maximum accuracy for live events. Do not wait for doubts.",
                            wait_for_doubts: false
                        }
                    ]
                };

                try {
                    const response = await fetch('/api/v1/seminar/start', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify(demoDeck)
                    });
                    
                    if (response.ok) {
                        sessionActive = true;
                        updateStatus();
                    } else {
                        alert("Error starting seminar");
                    }
                } catch (e) {
                    console.error(e);
                    alert("Failed to connect to API");
                }
            }

            async function updateStatus() {
                if (!sessionActive) return;
                
                try {
                    const response = await fetch('/api/v1/seminar/status');
                    if (response.ok) {
                        const status = await response.json();
                        currentSlideId = status.current_slide_id;
                        isWaitingForDoubts = status.is_waiting_for_doubts;
                        
                        // Update session badge
                        const badge = document.getElementById('session-badge');
                        if (status.is_active) {
                            if (isWaitingForDoubts) {
                                badge.className = "badge badge-green";
                                badge.innerHTML = `<span class="status-indicator status-waiting"></span>Waiting for Doubts (Slide ${currentSlideId})`;
                                document.getElementById('resolve-btn').disabled = false;
                            } else {
                                badge.className = "badge badge-blue";
                                badge.innerHTML = `<span class="status-indicator status-active"></span>Active (Slide ${currentSlideId})`;
                                document.getElementById('resolve-btn').disabled = true;
                            }
                            document.getElementById('next-btn').disabled = false;
                        } else {
                            badge.className = "badge badge-purple";
                            badge.innerHTML = "Seminar Completed";
                            document.getElementById('next-btn').disabled = true;
                            document.getElementById('resolve-btn').disabled = true;
                            sessionActive = false;
                        }

                        // Update Slide details
                        const slideHtml = `
                            <div class="slide-header">
                                <span class="badge badge-purple">Slide ${status.current_slide_id + 1}</span>
                                <span class="badge ${status.wait_for_doubts ? 'badge-green' : 'badge-blue'}">
                                    ${status.wait_for_doubts ? 'Doubts Enabled' : 'Auto Advance'}
                                </span>
                            </div>
                            <div class="slide-title">${status.title}</div>
                            <div class="slide-body">${status.content}</div>
                            <div class="private-notes">
                                <h4>
                                    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                        <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
                                    </svg>
                                    Speaker Notes (Hidden from Audience)
                                </h4>
                                <p>${status.notes}</p>
                            </div>
                        `;
                        document.getElementById('slide-viewer').innerHTML = slideHtml;

                        // Update Speech script
                        if (status.speech_generated) {
                            document.getElementById('speech-viewer').style.display = 'block';
                            document.getElementById('speech-text').innerText = status.speech_generated;
                        } else {
                            document.getElementById('speech-viewer').style.display = 'none';
                        }

                        // Enable/disable doubt form
                        const doubtForm = document.getElementById('doubt-form-area');
                        if (status.is_active && status.wait_for_doubts) {
                            doubtForm.style.opacity = '1';
                            doubtForm.style.pointerEvents = 'auto';
                        } else {
                            doubtForm.style.opacity = '0.5';
                            doubtForm.style.pointerEvents = 'none';
                        }

                        // Update doubts list
                        loadDoubtsList();

                    }
                } catch (e) {
                    console.error("Failed to fetch status: ", e);
                }
            }

            async function loadDoubtsList() {
                try {
                    const response = await fetch(`/api/v1/doubts/slide/${currentSlideId}`);
                    if (response.ok) {
                        const doubts = await response.json();
                        const container = document.getElementById('doubts-list-container');
                        
                        if (doubts.length === 0) {
                            container.innerHTML = `
                                <p style="color: var(--text-secondary); text-align: center; font-style: italic; margin-top: 1rem;">
                                    No doubts submitted yet for this slide.
                                </p>
                            `;
                            return;
                        }

                        let html = '';
                        doubts.forEach(d => {
                            const isPending = d.status === 'pending';
                            html += `
                                <div class="doubt-card ${isPending ? 'doubt-status-pending' : ''}">
                                    <div class="doubt-question">Q: ${d.question}</div>
                                    ${d.answer ? `<div class="doubt-answer"><strong>A (AI Assistant):</strong> ${d.answer}</div>` : 
                                    '<div style="font-size:0.8rem; color:var(--warning);">Pending AI Orchestrator Resolution...</div>'}
                                </div>
                            `;
                        });
                        container.innerHTML = html;
                    }
                } catch (e) {
                    console.error("Failed to load doubts: ", e);
                }
            }

            async function submitDoubt() {
                const doubtInput = document.getElementById('doubt-input');
                const question = doubtInput.value.trim();
                if (!question) return;

                try {
                    const response = await fetch('/api/v1/doubts/submit', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({
                            slide_id: currentSlideId,
                            question: question
                        })
                    });

                    if (response.ok) {
                        doubtInput.value = '';
                        loadDoubtsList();
                    } else {
                        const err = await response.json();
                        alert(`Error submitting doubt: ${err.detail}`);
                    }
                } catch (e) {
                    console.error(e);
                }
            }

            async function advanceSlide() {
                try {
                    const response = await fetch('/api/v1/seminar/next', { method: 'POST' });
                    if (response.ok) {
                        updateStatus();
                    } else {
                        const err = await response.json();
                        alert(`Error: ${err.detail}`);
                    }
                } catch (e) {
                    console.error(e);
                }
            }

            async function resolveDoubtsNow() {
                try {
                    const response = await fetch('/api/v1/seminar/resolve-doubts', { method: 'POST' });
                    if (response.ok) {
                        updateStatus();
                    } else {
                        const err = await response.json();
                        alert(`Error: ${err.detail}`);
                    }
                } catch (e) {
                    console.error(e);
                }
            }

            // Auto-refresh doubts when waiting
            setInterval(() => {
                if (sessionActive && isWaitingForDoubts) {
                    loadDoubtsList();
                }
            }, 3000);
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)
