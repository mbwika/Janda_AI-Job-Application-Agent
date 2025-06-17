# File: agents/orchestrator.py

from crewai import Crew
from .tasks import (
    ResumeUploadTask,
    JobScrapingTask,
    ProfileBuildingTask,
    MatchingTask,
    ResumeTailoringTask,
    JobApplicationTask
)

def run_agents_for_user(email: str):
    """
    Orchestrates the multi-agent flow for a given user.
    Injects the email into tasks if necessary (e.g., for identification in MongoDB/FAISS).
    """
    
    # Optionally inject email into task descriptions if agents need it explicitly
    ProfileBuildingTask.description += f" The user email is {email}."
    MatchingTask.description += f" The profile to match belongs to {email}."
    ResumeTailoringTask.description += f" Generate documents for {email}."
    JobApplicationTask.description += f" Apply on behalf of user {email}."

    agents = [
        ResumeUploadTask.agent,
        JobScrapingTask.agent,
        ProfileBuildingTask.agent,
        MatchingTask.agent,
        ResumeTailoringTask.agent,
        JobApplicationTask.agent
    ]
    agents = [agent for agent in agents if agent is not None]

    crew = Crew(
        agents=agents,
        tasks=[
            ResumeUploadTask,
            JobScrapingTask,
            ProfileBuildingTask,
            MatchingTask,
            ResumeTailoringTask,
            JobApplicationTask
        ],
        verbose=True  # Set to False in production if you don’t want logs
    )

    crew.kickoff()  # Start the multi-agent orchestration
