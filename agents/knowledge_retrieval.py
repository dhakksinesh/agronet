from crewai import Agent
from config import get_llm
from rag import retrieve_knowledge

KnowledgeRetrievalAgent = Agent(
    role="Agricultural Knowledge Retriever",
    goal="Retrieve relevant information from trusted agricultural documents using RAG",
    backstory="You are an expert in Indian agricultural practices with access to ICAR, TNAU, and government publications.",
    verbose=True,
    memory=True,
    llm=get_llm(),
    tools=[retrieve_knowledge],
)