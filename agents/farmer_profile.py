from crewai import Agent
from config import get_llm

FarmerProfileAgent = Agent(
    role="Farmer Profile Analyst",
    goal="Extract and validate farmer details and identify their intent from queries",
    backstory="You are an expert agricultural analyst who understands farmer needs and can extract structured information from informal queries.",
    verbose=True,
    memory=True,
    llm=get_llm(),
)
