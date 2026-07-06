from crewai import Task
from agents import ReportGeneratorAgent
from .profile_task import profile_task
from .weather_task import weather_task
from .knowledge_task import knowledge_task
from .crop_task import crop_task
from .disease_task import disease_task
from .government_task import government_task
from .recommendation_task import recommendation_task
from .evaluation_task import evaluation_task

report_task = Task(
    description="""Generate a final structured advisory report for the farmer.

Create a comprehensive, easy-to-read report including:
1. Header with farmer details (state, district, crop, soil type)
2. Weather Summary
3. Government Schemes Eligibility
4. Crop Advisory (irrigation, fertilization, management)
5. Pest & Disease Alerts
6. Knowledge References (from RAG)
7. Prioritized Action Plan
8. Validation Summary

Format for easy farmer understanding with clear sections and actionable items.""",
    expected_output="Comprehensive, readable advisory report with all recommendations",
    agent=ReportGeneratorAgent,
    context=[
        profile_task,
        weather_task,
        knowledge_task,
        crop_task,
        disease_task,
        government_task,
        recommendation_task,
        evaluation_task,
    ],
)