from crewai import Task
from agents import KnowledgeRetrievalAgent
from .profile_task import profile_task

knowledge_task = Task(
    description="""Retrieve relevant agricultural knowledge from trusted documents using RAG.

Farmer details - Crop: {crop}, State: {state}, District: {district}
Farmer query: {query}

Use the crop, state, district, and query above to search the knowledge base.

Search for information about:
- Crop-specific cultivation practices for the region
- Recommended irrigation schedules
- Fertilizer recommendations for the crop
- Local pest and disease profiles
- Regional best practices""",
    expected_output="Retrieved context from trusted agricultural documents (ICAR, TNAU, etc.)",
    agent=KnowledgeRetrievalAgent,
    context=[profile_task],
)