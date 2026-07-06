from crewai import Task
from agents import FarmerProfileAgent
from pydantic import BaseModel
from typing import Optional

class FarmerProfile(BaseModel):
    state: str
    district: str
    crop: str
    soil_type: str
    query: str
    intent: Optional[str] = None

profile_task = Task(
    description="""Analyze the farmer's query and recent conversation history to determine their intent.

The farmer's profile is already provided as inputs:
- state: {state}
- district: {district}
- crop: {crop}
- soil_type: {soil_type}
- query: {query}
- current_date: {current_date}
- current_season: {current_season}

Today's date is {current_date}. The current agricultural season is {current_season}.

Conversation history (previous exchanges):
{conversation_history}

Your job is to understand {query} in the context of the conversation history above. If the query is a follow-up (e.g. "what about fertilizer?"), use the history to determine what it refers to.

Return a structured profile with:
- state: {state}
- district: {district}
- crop: {crop}
- soil_type: {soil_type}
- query: {query}
- intent: The identified intent (e.g., irrigation, fertilization, pest management, general advice, etc.)""",
    expected_output="Structured farmer profile with state, district, crop, soil type, query, and identified intent",
    agent=FarmerProfileAgent,
    output_pydantic=FarmerProfile,
)