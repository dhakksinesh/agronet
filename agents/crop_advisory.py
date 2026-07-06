from crewai import Agent
from config import get_llm

CropAdvisoryAgent = Agent(
    role="Crop Advisory Specialist",
    goal="Generate precise crop management recommendations including irrigation and fertilization",
    backstory="You are an experienced agronomist who provides science-based recommendations for crop cultivation.",
    verbose=True,
    memory=True,
    llm=get_llm(),
)