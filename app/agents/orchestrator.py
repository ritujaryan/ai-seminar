import logging
from typing import List, Dict, Any, Optional
from app.models.slide import Slide, SlideDeck
from app.models.doubt import Doubt
from app.models.session import SeminarSession, SpeechLog, SeminarStatus
from app.repositories.slide_repository import slide_repo
from app.repositories.doubt_repository import doubt_repo
from app.repositories.session_repository import session_repo
from app.repositories.vector_repository import get_vector_repo
from app.services.rag_service import rag_service
from app.agents.crew import run_agent_workflow

logger = logging.getLogger(__name__)

class SeminarOrchestrator:
    def __init__(self):
        pass

    def start_seminar(self, deck: SlideDeck) -> SeminarSession:
        """
        Initialize the seminar by:
        1. Clearing any existing repositories.
        2. Populating the SlideRepository.
        3. Indexing slide content and notes in the Vector DB.
        4. Creating a new active Session.
        """
        # Reset state
        slide_repo.clear()
        doubt_repo.clear()
        session_repo.clear()
        
        # Ingest slides
        slide_repo.deck_title = deck.title
        for slide in deck.slides:
            slide_repo.create(slide)
            
        # Index in Vector DB for RAG
        rag_service.index_deck(deck.slides)
        
        # Create session
        session_id = "session_active"
        session = SeminarSession(
            session_id=session_id,
            current_slide_id=0,
            is_active=True,
            is_waiting_for_doubts=False
        )
        session_repo.create(session)
        
        # Automatically generate speech for the first slide (slide_id = 0)
        self.process_slide(session, 0)
        
        return session

    def process_slide(self, session: SeminarSession, slide_id: int):
        """
        Generate public speaker speech content based on private notes for the given slide.
        Uses Maker-Checker-Reviewer agent workflow.
        """
        slide = slide_repo.get(slide_id)
        if not slide:
            logger.error(f"Slide {slide_id} not found in repository.")
            return

        logger.info(f"Generating speaker speech for slide {slide_id}...")
        
        # Agent inputs
        inputs = {
            "title": slide.title,
            "content": slide.content,
            "notes": slide.notes
        }
        
        # Run CrewAI (Maker-Checker-Reviewer)
        speech_text = run_agent_workflow("generate_speech", inputs)
        
        # Store in session speech history
        speech_log = SpeechLog(slide_id=slide_id, content_spoken=speech_text)
        session.speech_history.append(speech_log)
        
        # Determine if we should wait for doubts
        session.is_waiting_for_doubts = slide.wait_for_doubts
        session_repo.update(session.session_id, session)

    def next_slide(self) -> Optional[SeminarStatus]:
        """
        Advance the seminar to the next slide.
        If the current slide requires waiting for doubts, we first resolve the doubts
        before transitioning.
        """
        session = session_repo.get_active()
        if not session or not session.is_active:
            return None
            
        current_slide_id = session.current_slide_id
        current_slide = slide_repo.get(current_slide_id)
        
        # If waiting for doubts and doubts exist, resolve them first!
        if session.is_waiting_for_doubts:
            # Resolve doubts
            self.resolve_pending_doubts(session, current_slide_id)
            
        # Move to next slide
        next_slide_id = current_slide_id + 1
        next_slide = slide_repo.get(next_slide_id)
        
        if next_slide:
            session.current_slide_id = next_slide_id
            session.is_waiting_for_doubts = next_slide.wait_for_doubts
            session_repo.update(session.session_id, session)
            
            # Process next slide speaker speech
            self.process_slide(session, next_slide_id)
            
            return self.get_status()
        else:
            # End of presentation
            session.is_active = False
            session.is_waiting_for_doubts = False
            session_repo.update(session.session_id, session)
            return self.get_status()

    def resolve_pending_doubts(self, session: SeminarSession, slide_id: int):
        """
        Resolve pending doubts for a slide.
        1. Fetch all doubts posted for this slide.
        2. Rank and pick top N doubts relevant to slide notes/contents using Vector DB.
        3. Retrieve relevant RAG context.
        4. Call Maker-Checker-Reviewer workflow to generate answers.
        5. Update doubts and store in session.
        """
        doubts = doubt_repo.get_pending_by_slide(slide_id)
        if not doubts:
            logger.info(f"No pending doubts to resolve for slide {slide_id}.")
            session.is_waiting_for_doubts = False
            session_repo.update(session.session_id, session)
            return

        slide = slide_repo.get(slide_id)
        
        # Rank and pick top 5 doubts using Vector DB relevance
        analyzed_doubts = rag_service.rank_doubts_for_slide(slide, doubts, top_n=5)
        top_doubts = [d for d in analyzed_doubts if d.category == "top_n"]
        
        # Get questions text list
        questions = [d.question for d in top_doubts]
        
        # Retrieve RAG context (combine contexts from Vector DB for all top doubts)
        combined_context = ""
        for d in top_doubts:
            ctx = rag_service.get_relevant_context(d.question, slide_id, n_results=2)
            if ctx:
                combined_context += ctx + "\n\n"
                
        if not combined_context:
            combined_context = f"Slide content: {slide.content}\nNotes: {slide.notes}"

        # Agent inputs for doubt resolution
        inputs = {
            "slide_title": slide.title,
            "slide_content": slide.content,
            "context": combined_context,
            "doubts": questions
        }
        
        # Run CrewAI (Maker-Checker-Reviewer)
        resolved_qa_text = run_agent_workflow("resolve_doubts", inputs)
        
        # For each top doubt, generate its own specific answer and mark as approved
        # In a real setup, CrewAI would output a structured JSON containing individual answers.
        # Here we parse or assign the combined answers, and save them.
        top_doubt_ids = {d.doubt_id for d in top_doubts}
        for d in doubts:
            if d.doubt_id in top_doubt_ids:
                d.answer = f"Resolved during QA: {resolved_qa_text}"
                d.status = "approved"
            else:
                d.answer = "Not selected for live resolution (outside top 5 relevant doubts)."
                d.status = "archived"
            doubt_repo.update(d.doubt_id, d)
            
        # Log in session
        if slide_id not in session.resolved_doubts:
            session.resolved_doubts[slide_id] = []
        session.resolved_doubts[slide_id].extend([d.doubt_id for d in top_doubts])
        
        # Clear wait status
        session.is_waiting_for_doubts = False
        session_repo.update(session.session_id, session)
        logger.info(f"Resolved doubts for slide {slide_id}.")

    def get_status(self) -> Optional[SeminarStatus]:
        """
        Get the current status of the seminar session.
        """
        session = session_repo.get_active()
        if not session:
            return None
            
        current_slide = slide_repo.get(session.current_slide_id)
        if not current_slide:
            return None
            
        # Get latest spoken speech for current slide if available
        speech_generated = None
        for log in session.speech_history:
            if log.slide_id == session.current_slide_id:
                speech_generated = log.content_spoken
                
        return SeminarStatus(
            session_id=session.session_id,
            current_slide_id=session.current_slide_id,
            title=current_slide.title,
            content=current_slide.content,
            notes=current_slide.notes,
            wait_for_doubts=current_slide.wait_for_doubts,
            is_waiting_for_doubts=session.is_waiting_for_doubts,
            is_active=session.is_active,
            speech_generated=speech_generated
        )

# Singleton Orchestrator
orchestrator = SeminarOrchestrator()
