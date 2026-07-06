from crewai import Task
from agents import ReportGeneratorAgent
from .profile_task import profile_task
from .weather_task import weather_task
from .knowledge_task import knowledge_task
from .crop_task import crop_task

simple_report_task = Task(
    description="""Answer the farmer's query in 2-4 short sentences. No headers, no farmer details, no weather summary, no sections. Just the direct answer.

If they ask about water: give exact liters/interval.
If they ask about fertilizer: give exact NPK ratio and amount.
If they ask about pests: name the pest and treatment.
If they ask about weather: give a short impact statement.

Current context (profile, weather, knowledge, crop advisory) is available — use it silently for accuracy.""",
    expected_output="2-4 sentence direct answer to the farmer's question",
    agent=ReportGeneratorAgent,
    context=[
        profile_task,
        weather_task,
        knowledge_task,
        crop_task,
    ],
)
