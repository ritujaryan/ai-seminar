import os
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

# Try importing CrewAI
CREWAI_AVAILABLE = False
try:
    from crewai import Agent, Task, Crew, Process
    # Check if we can import LLM classes
    from langchain_openai import ChatOpenAI
    from langchain_google_genai import ChatGoogleGenerativeAI
    CREWAI_AVAILABLE = True
except ImportError:
    logger.warning("CrewAI or LangChain dependencies not fully installed. Falling back to Mock Agents.")

def get_llm():
    """
    Get the configured LLM based on environment settings.
    """
    from app.core.config import settings
    from crewai import LLM
    
    if settings.LLM_PROVIDER == "openai":
        if not settings.OPENAI_API_KEY:
            logger.warning("OPENAI_API_KEY is missing. Defaulting to mock.")
            return None
        try:
            return LLM(
                model=settings.OPENAI_MODEL_NAME,
                api_key=settings.OPENAI_API_KEY,
                temperature=0.7
            )
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI LLM: {e}")
            return None
            
    elif settings.LLM_PROVIDER == "gemini":
        if not settings.GEMINI_API_KEY:
            logger.warning("GEMINI_API_KEY is missing. Defaulting to mock.")
            return None
        try:
            # crewai's LLM class uses litellm, which expects the 'gemini/' prefix
            model_name = settings.GEMINI_MODEL_NAME
            if not model_name.startswith("gemini/"):
                model_name = f"gemini/{model_name}"
            return LLM(
                model=model_name,
                api_key=settings.GEMINI_API_KEY,
                temperature=0.7
            )
        except Exception as e:
            logger.error(f"Failed to initialize Gemini LLM: {e}")
            return None
            
    return None

class MockCrew:
    """
    Mock implementation of CrewAI agent orchestration to allow running without API keys or packages.
    """
    def __init__(self, task_type: str, inputs: Dict[str, Any]):
        self.task_type = task_type
        self.inputs = inputs

    def kickoff(self) -> str:
        if self.task_type == "generate_speech":
            title = self.inputs.get("title", "Slide")
            content = self.inputs.get("content", "")
            notes = self.inputs.get("notes", "")
            
            # Simple Maker-Checker-Reviewer flow simulation
            maker_draft = f"Hello everyone. Today we are looking at: '{title}'. {content}. As a speaker, I want to highlight: {notes}."
            checker_review = f"[Approved Speech] {maker_draft}"
            reviewer_final = f"{checker_review}\n\nThank you, let me know if you have any questions before we move on!"
            return reviewer_final
            
        elif self.task_type == "resolve_doubts":
            slide_title = self.inputs.get("slide_title", "")
            slide_content = self.inputs.get("slide_content", "")
            context = self.inputs.get("context", "")
            doubts = self.inputs.get("doubts", [])
            
            resolved_text = []
            for i, d in enumerate(doubts):
                resolved_text.append(
                    f"Doubt {i+1}: '{d}'\n"
                    f"Answer: Based on the slide '{slide_title}' and context: {context[:100]}..., "
                    f"the answer is that we fully cover this topic in the notes. We make sure that doubts like '{d}' are resolved. "
                    f"If you need more details, please let us know!"
                )
            
            maker_draft = "\n\n".join(resolved_text)
            checker_review = f"[Verified Answers]\n{maker_draft}"
            reviewer_final = f"Here are the answers to your questions:\n\n{checker_review}"
            return reviewer_final
            
        return "Mock response generated."

def run_agent_workflow(task_type: str, inputs: Dict[str, Any]) -> str:
    """
    Executes the Maker-Checker-Reviewer agent workflow using CrewAI (if available) or the Mock fallback.
    """
    llm = get_llm()
    
    if not CREWAI_AVAILABLE or llm is None:
        logger.info("Using MockCrew for workflow execution.")
        crew = MockCrew(task_type, inputs)
        return crew.kickoff()
        
    try:
        # Standard CrewAI Multi-Agent Execution
        if task_type == "generate_speech":
            # 1. Maker
            maker = Agent(
                role="Seminar Content Creator",
                goal="Draft spoken presentation content based on slide title, content, and private notes.",
                backstory="An engaging, professional presenter who turns raw slide notes into easy-to-understand spoken dialogue.",
                verbose=True,
                llm=llm
            )
            # 2. Checker
            checker = Agent(
                role="Speech Quality Checker",
                goal="Review the drafted speech to verify correctness, ensuring no notes details are missed, and tone is appropriate.",
                backstory="A detail-oriented analyst who edits presentation drafts for accuracy, clarity, and professionalism.",
                verbose=True,
                llm=llm
            )
            # 3. Reviewer
            reviewer = Agent(
                role="Final Seminar Presenter",
                goal="Perform final edits to ensure flow is conversational, and provide final approval.",
                backstory="A charismatic keynote speaker who delivers polished, natural, and seamless presentation content.",
                verbose=True,
                llm=llm
            )
            
            # Tasks
            task1 = Task(
                description=(
                    "Draft an engaging speech for Slide Title: '{title}'.\n"
                    "Slide Content: '{content}'\n"
                    "Slide Notes (incorporate these): '{notes}'\n"
                    "Keep it professional and conversational."
                ),
                expected_output="A drafted spoken script incorporating the content and notes.",
                agent=maker
            )
            
            task2 = Task(
                description="Review the speech draft. Ensure it is professional, doesn't contain placeholders, and accurately reflects the notes.",
                expected_output="An edited and verified presentation script.",
                agent=checker
            )
            
            task3 = Task(
                description="Finalize the speech for public presentation. Add natural speech transitions and output the final speech script.",
                expected_output="The final polished speaking script.",
                agent=reviewer
            )
            
            crew = Crew(
                agents=[maker, checker, reviewer],
                tasks=[task1, task2, task3],
                process=Process.sequential,
                verbose=True
            )
            
            result = crew.kickoff(inputs=inputs)
            return str(result)
            
        elif task_type == "resolve_doubts":
            # 1. Maker (Doubt Solver)
            maker = Agent(
                role="Seminar Doubt Solver",
                goal="Formulate detailed answers to audience doubts using slide content and retrieved context.",
                backstory="An expert educator who resolves student and professional doubts clearly, referencing the provided source materials.",
                verbose=True,
                llm=llm
            )
            # 2. Checker
            checker = Agent(
                role="Answers Verification Analyst",
                goal="Verify that the answers generated are completely accurate to the provided slide context and do not hallucinate information.",
                backstory="A rigorous researcher who checks facts, references context, and ensures compliance with accuracy guidelines.",
                verbose=True,
                llm=llm
            )
            # 3. Reviewer
            reviewer = Agent(
                role="Final Seminar Q&A Editor",
                goal="Add polite, conversational framing and structure to the doubts and answers, delivering the final approved Q&A response.",
                backstory="A professional moderator who addresses the audience gracefully and summarizes answers concisely.",
                verbose=True,
                llm=llm
            )
            
            # Formulate prompt text for doubts
            doubts_list = "\n".join([f"- {d}" for d in inputs.get("doubts", [])])
            
            task1 = Task(
                description=(
                    "Answer these audience doubts:\n"
                    f"{doubts_list}\n"
                    "Using the slide context: '{slide_title}' - '{slide_content}'\n"
                    "And retrieved context/notes: '{context}'\n"
                    "Draft an answer for each doubt separately."
                ),
                expected_output="A list of doubts and their corresponding drafted answers.",
                agent=maker
            )
            
            task2 = Task(
                description="Verify the drafted answers against the slide content and retrieved context. Correct any inaccuracies.",
                expected_output="A list of verified doubts and answers.",
                agent=checker
            )
            
            task3 = Task(
                description="Format the verified Q&A into a polished response for the speaker to read. Add professional, conversational greetings and summaries.",
                expected_output="The final polished and approved Q&A transcript.",
                agent=reviewer
            )
            
            crew = Crew(
                agents=[maker, checker, reviewer],
                tasks=[task1, task2, task3],
                process=Process.sequential,
                verbose=True
            )
            
            result = crew.kickoff(inputs=inputs)
            return str(result)
            
    except Exception as e:
        logger.error(f"Error in CrewAI execution: {e}. Falling back to MockCrew.")
        crew = MockCrew(task_type, inputs)
        return crew.kickoff()
        
    return "Error in workflow execution."
