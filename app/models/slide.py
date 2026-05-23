from pydantic import BaseModel
from typing import List, Optional

class SlideBase(BaseModel):
    slide_id: int
    title: str
    content: str
    notes: str
    wait_for_doubts: bool = False

class SlideCreate(SlideBase):
    pass

class Slide(SlideBase):
    class Config:
        from_attributes = True

class SlideDeck(BaseModel):
    title: str
    slides: List[Slide]
