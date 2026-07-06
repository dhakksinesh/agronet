from crewai import Crew
from agents import (
    FarmerProfileAgent,
    WeatherIntelligenceAgent,
    KnowledgeRetrievalAgent,
    CropAdvisoryAgent,
    DiseasePestAgent,
    GovernmentSchemeAgent,
    RecommendationAgent,
    EvaluationAgent,
    ReportGeneratorAgent
)
from tasks import (
    profile_task,
    weather_task,
    knowledge_task,
    crop_task,
    disease_task,
    government_task,
    recommendation_task,
    evaluation_task,
    report_task,
    simple_report_task,
)

agri_crew = Crew(
    agents=[
        FarmerProfileAgent,
        WeatherIntelligenceAgent,
        KnowledgeRetrievalAgent,
        CropAdvisoryAgent,
        DiseasePestAgent,
        GovernmentSchemeAgent,
        RecommendationAgent,
        EvaluationAgent,
        ReportGeneratorAgent
    ],
    tasks=[
        profile_task,
        weather_task,
        knowledge_task,
        crop_task,
        disease_task,
        government_task,
        recommendation_task,
        evaluation_task,
        report_task
    ],
    verbose=True,
    process="sequential"
)

simple_crew = Crew(
    agents=[
        FarmerProfileAgent,
        WeatherIntelligenceAgent,
        KnowledgeRetrievalAgent,
        CropAdvisoryAgent,
        ReportGeneratorAgent
    ],
    tasks=[
        profile_task,
        weather_task,
        knowledge_task,
        crop_task,
        simple_report_task,
    ],
    verbose=True,
    process="sequential"
)

__all__ = ["agri_crew", "simple_crew"]