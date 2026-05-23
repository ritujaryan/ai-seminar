from fastapi import APIRouter, HTTPException
from app.models.slide import SlideDeck
from app.models.session import SeminarSession, SeminarStatus
from app.agents.orchestrator import orchestrator
from app.repositories.session_repository import session_repo

router = APIRouter()

@router.post("/start", response_model=SeminarSession)
def start_seminar(deck: SlideDeck):
    """
    Start a new seminar session.
    Ingests the slides and initializes Vector DB for RAG.
    """
    try:
        session = orchestrator.start_seminar(deck)
        return session
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start seminar: {str(e)}")

@router.get("/status", response_model=SeminarStatus)
def get_seminar_status():
    """
    Get current active seminar slide information, including spoken script content.
    """
    status = orchestrator.get_status()
    if not status:
        raise HTTPException(status_code=404, detail="No active seminar session found.")
    return status

@router.post("/next", response_model=SeminarStatus)
def advance_seminar():
    """
    Advance to the next slide.
    If the current slide has pending doubts and is set to wait, doubts will be automatically
    retrieved, ranked, answered via RAG + Maker-Checker-Reviewer agents, and then advanced.
    """
    status = orchestrator.next_slide()
    if not status:
        raise HTTPException(
            status_code=400, 
            detail="Cannot advance slide. No active seminar session exists or seminar has completed."
        )
    return status

@router.post("/resolve-doubts", response_model=SeminarStatus)
def force_resolve_doubts():
    """
    Manually force resolve doubts on the current slide without advancing yet.
    """
    session = session_repo.get_active()
    if not session or not session.is_active:
        raise HTTPException(status_code=400, detail="No active seminar session.")
        
    orchestrator.resolve_pending_doubts(session, session.current_slide_id)
    return orchestrator.get_status()
