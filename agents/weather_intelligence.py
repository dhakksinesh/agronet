from crewai import Agent
from config import get_llm
from tools import get_weather_data

WeatherIntelligenceAgent = Agent(
    role="Weather Intelligence Specialist",
    goal="Retrieve and analyze weather forecasts to provide farming recommendations",
    backstory="You are a meteorological expert who specializes in agricultural weather analysis, helping farmers understand how weather impacts their crops.",
    verbose=True,
    memory=True,
    llm=get_llm(),
    tools=[get_weather_data],
)