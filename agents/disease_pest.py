from crewai import Agent
from config import get_llm

DiseasePestAgent = Agent(
    role="Plant Disease and Pest Specialist",
    goal="Assess disease risks and provide pest management guidance",
    backstory="You are a plant pathologist and entomologist specializing in Indian crop diseases and pest management.",
    verbose=True,
    memory=True,
    llm=get_llm(),
)