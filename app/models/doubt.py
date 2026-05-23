from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class DoubtBase(BaseModel):
    slide_id: int
    question: str

class DoubtCreate(DoubtBase):
    pass

class Doubt(DoubtBase):
    doubt_id: str
    answer: Optional[str] = None
    status: str = "pending"  # "pending", "drafted", "approved"
    created_at: datetime

    class Config:
        from_attributes = True

class DoubtAnalysis(Doubt):
    similarity_score: float
    best_matching_slide_id: Optional[int] = None
    category: str  # "top_n", "not_relevant_to_ppt", "diff_slide", "low_priority"
    message: str

