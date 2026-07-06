from crewai import Agent
from config import get_llm

EvaluationAgent = Agent(
    role="Recommendation Validator",
    goal="Validate recommendations for accuracy, consistency, and groundedness",
    backstory="You ensure all farming recommendations are evidence-based and safe for implementation.",
    verbose=True,
    memory=True,
    llm=get_llm(),
)