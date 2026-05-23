from typing import List, Optional, Dict
from app.models.slide import Slide
from app.repositories.base import BaseRepository

class SlideRepository(BaseRepository[Slide]):
    def __init__(self):
        self._slides: Dict[int, Slide] = {}
        self._deck_title: str = "Default Presentation"

    def get(self, slide_id: int) -> Optional[Slide]:
        return self._slides.get(slide_id)

    def get_all(self) -> List[Slide]:
        return sorted(list(self._slides.values()), key=lambda x: x.slide_id)

    def create(self, item: Slide) -> Slide:
        self._slides[item.slide_id] = item
        return item

    def update(self, slide_id: int, item: Slide) -> Slide:
        if slide_id in self._slides:
            self._slides[slide_id] = item
            return item
        raise ValueError(f"Slide with ID {slide_id} not found")

    def delete(self, slide_id: int) -> bool:
        if slide_id in self._slides:
            del self._slides[slide_id]
            return True
        return False

    def clear(self):
        self._slides.clear()

    @property
    def deck_title(self) -> str:
        return self._deck_title

    @deck_title.setter
    def deck_title(self, title: str):
        self._deck_title = title

# Singleton instance
slide_repo = SlideRepository()
