import logging
from typing import List, Dict, Any
from app.repositories.vector_repository import get_vector_repo
from app.repositories.doubt_repository import doubt_repo
from app.models.doubt import Doubt, DoubtAnalysis
from app.models.slide import Slide

logger = logging.getLogger(__name__)

class RAGService:
    def __init__(self):
        pass

    def index_slide(self, slide: Slide):
        """
        Index a slide's title, content, and notes into the vector database.
        """
        vector_db = get_vector_repo()
        
        # We index the slide as a whole, and optionally split content and notes
        slide_text = f"Slide {slide.slide_id}: {slide.title}\nContent: {slide.content}\nNotes: {slide.notes}"
        
        vector_db.add_documents(
            documents=[slide_text],
            metadatas=[{"slide_id": slide.slide_id, "type": "full_slide"}],
            ids=[f"slide_{slide.slide_id}"]
        )
        logger.info(f"Indexed slide {slide.slide_id} in vector DB.")

    def index_deck(self, slides: List[Slide]):
        """
        Index an entire deck of slides.
        """
        vector_db = get_vector_repo()
        vector_db.clear()  # Clear existing index for new session
        
        documents = []
        metadatas = []
        ids = []
        
        for slide in slides:
            # Full slide context
            documents.append(f"Slide {slide.slide_id}: {slide.title}\nContent: {slide.content}\nNotes: {slide.notes}")
            metadatas.append({"slide_id": slide.slide_id, "type": "full_slide"})
            ids.append(f"slide_{slide.slide_id}")
            
            # Content separately
            documents.append(f"Slide {slide.slide_id} Content: {slide.content}")
            metadatas.append({"slide_id": slide.slide_id, "type": "content"})
            ids.append(f"slide_content_{slide.slide_id}")
            
            # Notes separately
            documents.append(f"Slide {slide.slide_id} Notes/Context: {slide.notes}")
            metadatas.append({"slide_id": slide.slide_id, "type": "notes"})
            ids.append(f"slide_notes_{slide.slide_id}")
            
        vector_db.add_documents(documents, metadatas, ids)
        logger.info(f"Indexed {len(slides)} slides into Vector DB (total chunk count: {len(documents)}).")

    def get_relevant_context(self, query_text: str, slide_id: int, n_results: int = 3) -> str:
        """
        Retrieve relevant slide context for a specific query/doubt.
        """
        vector_db = get_vector_repo()
        results = vector_db.query(query_text, n_results=10)  # query more to filter by slide_id
        
        # Filter results relevant to this slide_id
        relevant_docs = []
        for res in results:
            if res["metadata"].get("slide_id") == slide_id:
                relevant_docs.append(res["document"])
                if len(relevant_docs) >= n_results:
                    break
                    
        if not relevant_docs:
            # Fallback if no specific chunks found, query without slide filtering
            relevant_docs = [res["document"] for res in results[:n_results]]
            
        return "\n\n---\n\n".join(relevant_docs)

    def rank_doubts_for_slide(self, slide: Slide, doubts: List[Doubt], top_n: int = 5) -> List[DoubtAnalysis]:
        """
        Analyze and rank user doubts against the presentation slides, returning categorized DoubtAnalysis.
        """
        if not doubts:
            return []
            
        vector_db = get_vector_repo()
        
        # Get count of slides to retrieve matches for all slides
        from app.repositories.slide_repository import slide_repo
        slides_count = len(slide_repo.get_all())
        n_results_to_query = max(20, slides_count * 3)
        
        analyzed_doubts: List[DoubtAnalysis] = []
        
        # --- STAGE 1: LOCAL VECTOR / SIMILARITY FILTERING ---
        for doubt in doubts:
            results = vector_db.query(doubt.question, n_results=n_results_to_query)
            
            slide_scores: Dict[int, float] = {}
            for res in results:
                s_id = res["metadata"].get("slide_id")
                if s_id is not None:
                    score = res.get("score", 0.0)
                    if hasattr(vector_db, "collection") and vector_db.collection is not None:
                        sim = 1.0 / (1.0 + score)
                    else:
                        sim = score
                    
                    s_id_int = int(s_id)
                    if s_id_int not in slide_scores or sim > slide_scores[s_id_int]:
                        slide_scores[s_id_int] = sim
            
            if slide_scores:
                best_matching_slide_id = max(slide_scores, key=slide_scores.get)
                similarity_score = slide_scores[best_matching_slide_id]
            else:
                best_matching_slide_id = None
                similarity_score = 0.0
            
            relevance_threshold = 0.35
            
            category = ""
            message = ""
            
            if similarity_score < relevance_threshold or best_matching_slide_id is None:
                category = "not_relevant_to_ppt"
                message = "Not relevant to PPT"
                best_matching_slide_id = None
            elif best_matching_slide_id != slide.slide_id:
                category = "diff_slide"
                if best_matching_slide_id < slide.slide_id:
                    message = f"covered in slide({best_matching_slide_id})"
                else:
                    message = "will be covered in next slide"
            else:
                category = "current_slide_candidate"
                message = ""
                
            analyzed_doubts.append(
                DoubtAnalysis(
                    doubt_id=doubt.doubt_id,
                    slide_id=doubt.slide_id,
                    question=doubt.question,
                    answer=doubt.answer,
                    status=doubt.status,
                    created_at=doubt.created_at,
                    similarity_score=similarity_score,
                    best_matching_slide_id=best_matching_slide_id,
                    category=category,
                    message=message
                )
            )
            
        # Collect candidates for the current slide
        current_candidates = [d for d in analyzed_doubts if d.category == "current_slide_candidate"]
        # Sort them by similarity score descending to prioritize the top ones for LLM pruning
        current_candidates.sort(key=lambda x: x.similarity_score, reverse=True)
        
        # Split into candidates to evaluate via LLM and ones that automatically get downgraded
        max_llm_candidates = 10
        llm_candidates = current_candidates[:max_llm_candidates]
        downgraded_candidates = current_candidates[max_llm_candidates:]
        
        for d in downgraded_candidates:
            d.category = "low_priority"
            d.message = "less relevant hence low priority"
            
        # --- STAGE 2: LLM LOGICAL VERIFICATION & DEDUPLICATION ---
        if llm_candidates:
            from app.agents.crew import get_llm
            llm = get_llm()
            
            llm_success = False
            
            if llm is not None:
                try:
                    import json
                    candidate_data = [
                        {"doubt_id": d.doubt_id, "question": d.question}
                        for d in llm_candidates
                    ]
                    
                    prompt = f"""You are an AI Seminar Assistant. Your task is to evaluate user-submitted questions against the current slide.
Current Slide Title: "{slide.title}"
Current Slide Content: "{slide.content}"
Current Slide Notes: "{slide.notes}"

Candidate Questions:
{json.dumps(candidate_data, indent=2)}

Analyze each question:
1. is_relevant (boolean): Set to true if this question is logically relevant to the current slide topic, notes, or content. Set to false if it is off-topic (e.g. completely unrelated programming questions, cheating, unrelated math topics).
2. duplicate_of (string or null): If multiple questions are asking the same underlying question, set duplicate_of to the doubt_id of the first occurrence of that question in the list. Otherwise set it to null.
3. priority_score (integer from 1 to 10): Assign a score indicating how relevant, deep, and intellectually useful the question is for a live Q&A session. Higher means better.

You must respond with ONLY a valid JSON object matching this schema, without any markdown formatting or extra text:
{{
  "evaluations": [
    {{
      "doubt_id": "string",
      "is_relevant": true,
      "duplicate_of": null,
      "priority_score": 8
    }}
  ]
}}"""
                    logger.info("Sending candidate doubts to LLM for stage-2 verification...")
                    raw_response = llm.call(messages=prompt)
                    
                    # Clean markdown fence blocks if present
                    raw_response = raw_response.strip()
                    if raw_response.startswith("```"):
                        lines = raw_response.splitlines()
                        if lines[0].startswith("```"):
                            lines = lines[1:]
                        if lines[-1].startswith("```"):
                            lines = lines[:-1]
                        raw_response = "\n".join(lines).strip()
                        
                    parsed_eval = json.loads(raw_response)
                    evaluations = parsed_eval.get("evaluations", [])
                    eval_map = {e["doubt_id"]: e for e in evaluations}
                    
                    # Process LLM classifications
                    stage2_candidates = []
                    for d in llm_candidates:
                        e = eval_map.get(d.doubt_id)
                        if e:
                            if not e.get("is_relevant", True):
                                d.category = "not_relevant_to_ppt"
                                d.message = "Filtered by LLM: Off-topic"
                                d.best_matching_slide_id = None
                            elif e.get("duplicate_of") is not None:
                                d.category = "low_priority"
                                d.message = "Duplicate of another question"
                            else:
                                d.category = "current_slide_candidate"
                                # Save the LLM's priority score as the sorting key
                                d.similarity_score = float(e.get("priority_score", 5)) / 10.0
                                stage2_candidates.append(d)
                        else:
                            # Default if missing in LLM response
                            stage2_candidates.append(d)
                            
                    # Categorize the unique/approved stage-2 candidates
                    stage2_candidates.sort(key=lambda x: x.similarity_score, reverse=True)
                    for idx, d in enumerate(stage2_candidates):
                        if idx < top_n:
                            d.category = "top_n"
                            d.message = "Top N relevant"
                        else:
                            d.category = "low_priority"
                            d.message = "less relevant hence low priority"
                            
                    llm_success = True
                    logger.info("Stage-2 LLM evaluation completed successfully.")
                except Exception as ex:
                    logger.error(f"Error during Stage-2 LLM verification: {ex}. Falling back to RAG mathematical ranking.")
                    
            if not llm_success:
                # Fallback to standard ranking logic for candidates
                llm_candidates.sort(key=lambda x: x.similarity_score, reverse=True)
                for idx, d in enumerate(llm_candidates):
                    if idx < top_n:
                        d.category = "top_n"
                        d.message = "Top N relevant"
                    else:
                        d.category = "low_priority"
                        d.message = "less relevant hence low priority"
                        
        # Sort all analyzed doubts by category priority and similarity score descending
        category_priority = {
            "top_n": 0,
            "low_priority": 1,
            "diff_slide": 2,
            "not_relevant_to_ppt": 3
        }
        
        analyzed_doubts.sort(key=lambda x: (category_priority.get(x.category, 99), -x.similarity_score))
        
        return analyzed_doubts

# Singleton service
rag_service = RAGService()
