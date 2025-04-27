from dataclasses import dataclass

@dataclass(frozen=True)
class RepositoryConfig:
    """Configuration for repository behavior"""
    max_retries: int = 3
    retry_delay: float = 1.0  # seconds
    timeout: float = 10.0  # seconds