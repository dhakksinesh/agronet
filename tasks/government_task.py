from crewai import Task
from agents import GovernmentSchemeAgent
from .profile_task import profile_task

government_task = Task(
    description="""Identify government schemes eligible for the farmer based on their profile and location.

Consider:
- State and district for state-specific schemes
- Crop type for crop-specific subsidies
- Soil type for soil health schemes
- Small/medium farmer status

Output: List of eligible schemes with:
- Scheme name
- Description
- Eligibility criteria
- How to apply""",
    expected_output="List of eligible government schemes with descriptions",
    agent=GovernmentSchemeAgent,
    context=[profile_task],
)