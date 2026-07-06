from crewai import Task
from agents import WeatherIntelligenceAgent
from .profile_task import profile_task

weather_task = Task(
    description="""Retrieve and summarize weather forecast for the farmer's location.

Farmer location: {district}, {state}
Current date: {current_date}
Current season: {current_season}

Use the district and state above to get coordinates, then fetch weather data.

Output a weather summary including:
- temperature_max: Daily maximum temperature
- temperature_min: Daily minimum temperature
- rainfall: Precipitation amount
- wind_speed: Maximum wind speed
- humidity_avg: Average humidity""",
    expected_output="Weather summary including temperature, rainfall, humidity, and wind conditions",
    agent=WeatherIntelligenceAgent,
    context=[profile_task],
)