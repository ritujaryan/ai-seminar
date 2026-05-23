from fastapi import APIRouter, HTTPException
from typing import List
from app.models.doubt import Doubt, DoubtCreate, DoubtAnalysis
from app.repositories.doubt_repository import doubt_repo
from app.repositories.session_repository import session_repo
from app.repositories.slide_repository import slide_repo

router = APIRouter()

@router.post("/submit", response_model=Doubt)
def submit_doubt(doubt_in: DoubtCreate):
    """
    Submit a doubt for the current active slide.
    Checks if active session exists, and validates slide ID matches.
    """
    session = session_repo.get_active()
    if not session or not session.is_active:
        raise HTTPException(status_code=400, detail="No active seminar session.")
        
    if session.current_slide_id != doubt_in.slide_id:
        raise HTTPException(
            status_code=400, 
            detail=f"Doubt slide ID ({doubt_in.slide_id}) must match current active slide ID ({session.current_slide_id})."
        )
        
    slide = slide_repo.get(doubt_in.slide_id)
    if not slide:
        raise HTTPException(status_code=404, detail="Slide not found.")
        
    if not slide.wait_for_doubts:
        raise HTTPException(
            status_code=400,
            detail="Doubts are not enabled/allowed for this slide."
        )
        
    # Create and save doubt
    doubt = doubt_repo.create_doubt(doubt_in.slide_id, doubt_in.question)
    return doubt

@router.get("/slide/{slide_id}", response_model=List[Doubt])
def get_doubts_for_slide(slide_id: int):
    """
    Get all doubts submitted for a specific slide.
    """
    return doubt_repo.get_by_slide(slide_id)

@router.get("/slide/{slide_id}/resolved", response_model=List[Doubt])
def get_resolved_doubts_for_slide(slide_id: int):
    """
    Get all resolved/approved doubts for a slide.
    """
    doubts = doubt_repo.get_by_slide(slide_id)
    return [d for d in doubts if d.status == "approved"]

@router.get("/slide/{slide_id}/rank", response_model=List[DoubtAnalysis])
def rank_doubts_for_slide(slide_id: int, top_n: int = 5, global_pool: bool = True):
    """
    Get top N doubts for a slide ranked by semantic relevance to slide content/notes.
    If global_pool is True, ranks from all doubts in the database.
    If global_pool is False, only ranks doubts submitted for this specific slide.
    """
    slide = slide_repo.get(slide_id)
    if not slide:
        raise HTTPException(status_code=404, detail="Slide not found")
        
    if global_pool:
        doubts = doubt_repo.get_all()
    else:
        doubts = doubt_repo.get_by_slide(slide_id)
        
    if not doubts:
        return []
        
    from app.services.rag_service import rag_service
    ranked = rag_service.rank_doubts_for_slide(slide, doubts, top_n=top_n)
    return ranked
