from crewai import Task
from agents import RecommendationAgent
from .profile_task import profile_task
from .weather_task import weather_task
from .knowledge_task import knowledge_task
from .crop_task import crop_task
from .disease_task import disease_task
from .government_task import government_task

recommendation_task = Task(
    description="""Combine all agent outputs into a prioritized farming action plan.

Synthesize information from:
- Weather data (temperature, rainfall, humidity, wind)
- Crop advisory (irrigation, fertilization, management)
- Disease and pest assessment
- Government schemes
- Knowledge retrieval context
- Farmer profile (crop, soil type, location)

Output a prioritized action plan with:
1. Immediate actions (this week)
2. Short-term recommendations (next 2-4 weeks)
3. Long-term planning (seasonal)
4. Priority ranking with reasons""",
    expected_output="Consolidated recommendations with priority ranking",
    agent=RecommendationAgent,
    context=[
        profile_task,
        weather_task,
        knowledge_task,
        crop_task,
        disease_task,
        government_task,
    ],
)