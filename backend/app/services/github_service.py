"""
GitHub Repository Service

Handles cloning, validation, and metadata extraction from GitHub repositories.
"""

import os
import re
import shutil
import subprocess
import tempfile
import logging
from pathlib import Path
from typing import Optional, Tuple
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class RepoMetadata:
    """Metadata extracted from a GitHub repository"""
    owner: str
    name: str
    full_name: str
    clone_url: str
    default_branch: str = "main"


@dataclass
class RepoInfo:
    """Information about a cloned repository"""
    local_path: Path
    metadata: RepoMetadata
    detected_language: str
    file_count: int
    total_size_bytes: int
    cloned_at: datetime


class GitHubServiceError(Exception):
    """Base exception for GitHub service errors"""
    pass


class InvalidURLError(GitHubServiceError):
    """Raised when GitHub URL is invalid"""
    pass


class CloneError(GitHubServiceError):
    """Raised when repository cloning fails"""
    pass


class RepoTooLargeError(GitHubServiceError):
    """Raised when repository exceeds size limit"""
    pass


class GitHubService:
    """
    Service for interacting with GitHub repositories
    
    Provides functionality to:
    - Validate GitHub URLs
    - Clone repositories
    - Extract repository metadata
    - Detect primary programming language
    """
    
    # GitHub URL pattern: https://github.com/owner/repo or git@github.com:owner/repo
    GITHUB_URL_PATTERN = re.compile(
        r'^(?:https?://)?(?:www\.)?github\.com/([a-zA-Z0-9_-]+)/([a-zA-Z0-9_.-]+?)(?:\.git)?/?$'
    )
    
    # Maximum repository size in bytes (100 MB)
    MAX_REPO_SIZE = 100 * 1024 * 1024
    
    # Clone timeout in seconds
    CLONE_TIMEOUT = 300
    
    # Language detection by file extension
    LANGUAGE_EXTENSIONS = {
        'python': ['.py'],
        'golang': ['.go'],
        'javascript': ['.js', '.jsx', '.ts', '.tsx'],
        'java': ['.java'],
        'rust': ['.rs'],
        'cpp': ['.cpp', '.cc', '.cxx', '.hpp', '.h'],
    }
    
    def __init__(self, repos_base_dir: Optional[Path] = None):
        """
        Initialize GitHub service
        
        Args:
            repos_base_dir: Base directory for cloned repositories.
                          If None, uses system temp directory.
        """
        self.repos_base_dir = repos_base_dir or Path(tempfile.gettempdir()) / "study_game_repos"
        self.repos_base_dir.mkdir(parents=True, exist_ok=True)
    
    def validate_url(self, url: str) -> bool:
        """
        Validate if URL is a valid GitHub repository URL
        
        Args:
            url: URL to validate
            
        Returns:
            True if valid GitHub URL, False otherwise
        """
        return bool(self.GITHUB_URL_PATTERN.match(url.strip()))
    
    def parse_url(self, url: str) -> Tuple[str, str]:
        """
        Parse GitHub URL to extract owner and repo name
        
        Args:
            url: GitHub repository URL
            
        Returns:
            Tuple of (owner, repo_name)
            
        Raises:
            InvalidURLError: If URL is not a valid GitHub URL
        """
        match = self.GITHUB_URL_PATTERN.match(url.strip())
        if not match:
            raise InvalidURLError(f"Invalid GitHub URL: {url}")
        
        owner, repo = match.groups()
        # Remove .git suffix if present
        if repo.endswith('.git'):
            repo = repo[:-4]
        return owner, repo
    
    def get_repo_metadata(self, url: str) -> RepoMetadata:
        """
        Extract metadata from GitHub URL
        
        Args:
            url: GitHub repository URL
            
        Returns:
            RepoMetadata object
        """
        owner, name = self.parse_url(url)
        return RepoMetadata(
            owner=owner,
            name=name,
            full_name=f"{owner}/{name}",
            clone_url=f"https://github.com/{owner}/{name}.git"
        )
    
    async def clone_repository(
        self, 
        url: str,
        target_dir: Optional[Path] = None,
        depth: int = 1,
        branch: Optional[str] = None
    ) -> RepoInfo:
        """
        Clone a GitHub repository
        
        Args:
            url: GitHub repository URL
            target_dir: Target directory for clone. If None, auto-generates.
            depth: Clone depth (1 for shallow clone)
            branch: Specific branch to clone
            
        Returns:
            RepoInfo with clone details
            
        Raises:
            InvalidURLError: If URL is invalid
            CloneError: If clone operation fails
            RepoTooLargeError: If repository exceeds size limit
        """
        metadata = self.get_repo_metadata(url)
        
        # Generate target directory if not provided
        if target_dir is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            target_dir = self.repos_base_dir / f"{metadata.owner}_{metadata.name}_{timestamp}"
        
        # Ensure target doesn't exist
        if target_dir.exists():
            shutil.rmtree(target_dir)
        
        # Build git clone command
        cmd = ["git", "clone"]
        
        if depth:
            cmd.extend(["--depth", str(depth)])
        
        if branch:
            cmd.extend(["--branch", branch])
        
        cmd.extend([metadata.clone_url, str(target_dir)])
        
        logger.info(f"Cloning repository: {metadata.full_name} to {target_dir}")
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.CLONE_TIMEOUT,
                env={**os.environ, "GIT_TERMINAL_PROMPT": "0"}  # Disable git prompts
            )
            
            if result.returncode != 0:
                error_msg = result.stderr or result.stdout
                raise CloneError(f"Git clone failed: {error_msg}")
                
        except subprocess.TimeoutExpired:
            # Cleanup partial clone
            if target_dir.exists():
                shutil.rmtree(target_dir)
            raise CloneError(f"Clone timeout after {self.CLONE_TIMEOUT} seconds")
        except subprocess.SubprocessError as e:
            raise CloneError(f"Clone error: {str(e)}")
        
        # Check repository size
        total_size = self._calculate_dir_size(target_dir)
        if total_size > self.MAX_REPO_SIZE:
            shutil.rmtree(target_dir)
            raise RepoTooLargeError(
                f"Repository too large: {total_size / 1024 / 1024:.1f}MB "
                f"(max: {self.MAX_REPO_SIZE / 1024 / 1024:.1f}MB)"
            )
        
        # Detect primary language
        detected_language = self.detect_language(target_dir)
        file_count = self._count_source_files(target_dir, detected_language)
        
        logger.info(
            f"Successfully cloned {metadata.full_name}: "
            f"{file_count} {detected_language} files, "
            f"{total_size / 1024:.1f}KB"
        )
        
        return RepoInfo(
            local_path=target_dir,
            metadata=metadata,
            detected_language=detected_language,
            file_count=file_count,
            total_size_bytes=total_size,
            cloned_at=datetime.now()
        )
    
    def detect_language(self, repo_path: Path) -> str:
        """
        Detect the primary programming language of a repository
        
        Uses file extension counting to determine the dominant language.
        
        Args:
            repo_path: Path to cloned repository
            
        Returns:
            Detected language string (e.g., 'python', 'golang')
        """
        extension_counts: dict[str, int] = {}
        
        for ext_list in self.LANGUAGE_EXTENSIONS.values():
            for ext in ext_list:
                extension_counts[ext] = 0
        
        # Count files by extension
        for file_path in repo_path.rglob("*"):
            if file_path.is_file():
                ext = file_path.suffix.lower()
                if ext in extension_counts:
                    extension_counts[ext] += 1
        
        # Map extensions back to languages and count
        language_counts: dict[str, int] = {}
        for lang, extensions in self.LANGUAGE_EXTENSIONS.items():
            language_counts[lang] = sum(extension_counts.get(ext, 0) for ext in extensions)
        
        # Return language with most files
        if not any(language_counts.values()):
            return "unknown"
        
        return max(language_counts, key=lambda k: language_counts[k])
    
    def cleanup(self, repo_path: Path) -> None:
        """
        Clean up a cloned repository
        
        Args:
            repo_path: Path to repository to remove
        """
        if repo_path.exists():
            shutil.rmtree(repo_path)
            logger.info(f"Cleaned up repository: {repo_path}")
    
    def _calculate_dir_size(self, path: Path) -> int:
        """Calculate total size of directory in bytes"""
        total = 0
        for file_path in path.rglob("*"):
            if file_path.is_file():
                total += file_path.stat().st_size
        return total
    
    def _count_source_files(self, repo_path: Path, language: str) -> int:
        """Count source files for a given language"""
        extensions = self.LANGUAGE_EXTENSIONS.get(language, [])
        count = 0
        for file_path in repo_path.rglob("*"):
            if file_path.is_file() and file_path.suffix.lower() in extensions:
                count += 1
        return count


# Singleton instance
github_service = GitHubService()
