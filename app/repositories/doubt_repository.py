from typing import List, Optional
import uuid
from datetime import datetime
from app.models.doubt import Doubt
from app.repositories.base import BaseRepository
from app.repositories.vector_repository import get_vector_repo

class DoubtRepository(BaseRepository[Doubt]):
    def __init__(self):
        pass

    def get(self, doubt_id: str) -> Optional[Doubt]:
        vector_db = get_vector_repo()
        if vector_db.client and vector_db.doubts_collection:
            try:
                res = vector_db.doubts_collection.get(ids=[f"doubt_{doubt_id}"])
                if res and "metadatas" in res and res["metadatas"]:
                    meta = res["metadatas"][0]
                    return Doubt(
                        doubt_id=meta["doubt_id"],
                        slide_id=int(meta["slide_id"]),
                        question=meta["question"],
                        answer=meta.get("answer") or None,
                        status=meta["status"],
                        created_at=datetime.utcnow()
                    )
            except Exception:
                pass
        
        # Fallback
        for item in vector_db._fallback_db:
            meta = item["metadata"]
            if meta.get("type") == "doubt" and meta.get("doubt_id") == doubt_id:
                return Doubt(
                    doubt_id=meta["doubt_id"],
                    slide_id=int(meta["slide_id"]),
                    question=meta["question"],
                    answer=meta.get("answer") or None,
                    status=meta["status"],
                    created_at=datetime.utcnow()
                )
        return None

    def get_all(self) -> List[Doubt]:
        vector_db = get_vector_repo()
        if vector_db.client and vector_db.doubts_collection:
            try:
                res = vector_db.doubts_collection.get()
                doubts = []
                if res and "metadatas" in res and res["metadatas"]:
                    for meta in res["metadatas"]:
                        doubts.append(Doubt(
                            doubt_id=meta["doubt_id"],
                            slide_id=int(meta["slide_id"]),
                            question=meta["question"],
                            answer=meta.get("answer") or None,
                            status=meta["status"],
                            created_at=datetime.utcnow()
                        ))
                return doubts
            except Exception:
                pass
        
        # Fallback
        doubts = []
        for item in vector_db._fallback_db:
            meta = item["metadata"]
            if meta.get("type") == "doubt":
                doubts.append(Doubt(
                    doubt_id=meta["doubt_id"],
                    slide_id=int(meta["slide_id"]),
                    question=meta["question"],
                    answer=meta.get("answer") or None,
                    status=meta["status"],
                    created_at=datetime.utcnow()
                ))
        return doubts

    def create(self, item: Doubt) -> Doubt:
        vector_db = get_vector_repo()
        vector_db.add_doubt(
            doubt_id=item.doubt_id,
            question=item.question,
            slide_id=item.slide_id,
            status=item.status,
            answer=item.answer
        )
        return item

    def update(self, doubt_id: str, item: Doubt) -> Doubt:
        vector_db = get_vector_repo()
        vector_db.update_doubt(
            doubt_id=doubt_id,
            question=item.question,
            slide_id=item.slide_id,
            status=item.status,
            answer=item.answer
        )
        return item

    def delete(self, doubt_id: str) -> bool:
        vector_db = get_vector_repo()
        if vector_db.client and vector_db.doubts_collection:
            try:
                vector_db.doubts_collection.delete(ids=[f"doubt_{doubt_id}"])
                return True
            except Exception:
                pass
        vector_db._fallback_db = [item for item in vector_db._fallback_db if item["id"] != f"doubt_{doubt_id}"]
        return True

    def get_by_slide(self, slide_id: int) -> List[Doubt]:
        vector_db = get_vector_repo()
        doubts_data = vector_db.get_doubts_for_slide(slide_id)
        return [
            Doubt(
                doubt_id=d["doubt_id"],
                slide_id=d["slide_id"],
                question=d["question"],
                answer=d["answer"],
                status=d["status"],
                created_at=datetime.utcnow()
            )
            for d in doubts_data
        ]

    def get_pending_by_slide(self, slide_id: int) -> List[Doubt]:
        doubts = self.get_by_slide(slide_id)
        return [d for d in doubts if d.status == "pending"]

    def create_doubt(self, slide_id: int, question: str) -> Doubt:
        doubt_id = str(uuid.uuid4())
        new_doubt = Doubt(
            doubt_id=doubt_id,
            slide_id=slide_id,
            question=question,
            status="pending",
            created_at=datetime.utcnow()
        )
        return self.create(new_doubt)

    def clear(self):
        pass

# Singleton instance
doubt_repo = DoubtRepository()
