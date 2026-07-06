from crewai import Agent
from config import get_llm

RecommendationAgent = Agent(
    role="Farming Recommendation Coordinator",
    goal="Combine all agent outputs into a prioritized, actionable farming plan",
    backstory="You synthesize information from multiple sources to create comprehensive, easy-to-follow farming recommendations.",
    verbose=True,
    memory=True,
    llm=get_llm(),
)