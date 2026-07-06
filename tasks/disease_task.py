from crewai import Task
from agents import DiseasePestAgent
from .profile_task import profile_task
from .weather_task import weather_task

disease_task = Task(
    description="""Assess pest and disease risks for the specified crop in the given region.

Consider:
- The specific crop type
- State and district (regional pest profiles)
- Current weather conditions
- Seasonal patterns
- Common diseases for the crop in that region

Output:
- Pest alerts and risk levels
- Disease risk assessment
- Preventive measures
- Treatment recommendations if needed""",
    expected_output="Pest alerts and disease management recommendations",
    agent=DiseasePestAgent,
    context=[profile_task, weather_task],
)