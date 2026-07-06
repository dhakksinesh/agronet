from crewai import Agent
from config import get_llm

ReportGeneratorAgent = Agent(
    role="Agricultural Report Generator",
    goal="Create a structured, readable advisory report for farmers",
    backstory="You format complex agricultural advice into clear, actionable reports that farmers can easily follow.",
    verbose=True,
    memory=True,
    llm=get_llm(),
)