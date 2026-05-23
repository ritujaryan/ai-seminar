from pydantic import BaseModel
from typing import List, Dict, Optional

class SpeechLog(BaseModel):
    slide_id: int
    content_spoken: str

class SeminarSession(BaseModel):
    session_id: str
    current_slide_id: int = 0
    is_active: bool = True
    is_waiting_for_doubts: bool = False
    speech_history: List[SpeechLog] = []
    resolved_doubts: Dict[int, List[str]] = {}  # slide_id -> list of doubt_ids

class SeminarStatus(BaseModel):
    session_id: str
    current_slide_id: int
    title: str
    content: str
    notes: str
    wait_for_doubts: bool
    is_waiting_for_doubts: bool
    is_active: bool
    speech_generated: Optional[str] = None
