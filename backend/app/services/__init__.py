"""Backend services module"""
from app.services.github_service import github_service, GitHubService
# Note: AnalysisPipeline is imported lazily where needed to avoid circular imports

