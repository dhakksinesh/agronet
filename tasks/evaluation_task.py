from crewai import Task
from agents import EvaluationAgent
from .recommendation_task import recommendation_task

evaluation_task = Task(
    description="""Validate all recommendations for accuracy, consistency, and groundedness.

Check:
- Weather-based recommendations are consistent with forecast
- Crop recommendations match the crop type and soil
- Disease recommendations are appropriate for the region
- Government schemes are correctly matched to the profile
- No contradictory advice between recommendations
- Safety of all recommendations
- Grounding in retrieved agricultural knowledge

Output: Validation report with:
- Confirmed accuracy statements
- Any flagged issues or concerns
- Confidence levels for each recommendation""",
    expected_output="Validation report with any flagged issues or confirmed accuracy",
    agent=EvaluationAgent,
    context=[recommendation_task],
)