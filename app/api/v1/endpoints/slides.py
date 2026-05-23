from fastapi import APIRouter, HTTPException
from typing import List
from app.models.slide import Slide
from app.repositories.slide_repository import slide_repo

router = APIRouter()

@router.get("/", response_model=List[Slide])
def get_all_slides():
    """
    Get all slides in the current presentation deck.
    """
    return slide_repo.get_all()

@router.get("/{slide_id}", response_model=Slide)
def get_slide_by_id(slide_id: int):
    """
    Get details of a specific slide.
    """
    slide = slide_repo.get(slide_id)
    if not slide:
        raise HTTPException(status_code=404, detail="Slide not found")
    return slide
