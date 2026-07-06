from crewai import Agent
from config import get_llm
from tools import get_eligible_schemes

GovernmentSchemeAgent = Agent(
    role="Government Scheme Advisor",
    goal="Identify eligible government schemes based on farmer profile and location",
    backstory="You are knowledgeable about Indian agricultural schemes like PM-KISAN, PMFBY, and state-specific programs.",
    verbose=True,
    memory=True,
    llm=get_llm(),
    tools=[get_eligible_schemes],
)