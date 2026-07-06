from crewai import Task
from agents import CropAdvisoryAgent
from .profile_task import profile_task
from .weather_task import weather_task

crop_task = Task(
    description="""Generate crop-specific recommendations for irrigation, fertilization, and management.

Consider:
- The specific crop type
- Soil type from farmer profile
- Weather conditions
- Regional growing season
- Best practices from agricultural research

Output detailed recommendations for:
- Irrigation schedule and timing
- Fertilizer types and application rates
- Crop management practices
- Harvest timing""",
    expected_output="Detailed crop advisory including irrigation schedule and fertilizer recommendations",
    agent=CropAdvisoryAgent,
    context=[profile_task, weather_task],
)