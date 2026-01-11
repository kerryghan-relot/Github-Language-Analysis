from datetime import date
from dataclasses import dataclass

@dataclass
class RepositorySummary:
    name: str
    file_counts: int
    release_count: int
    size: int
    stars: int
    forks: int
    contributor_count: int
    created_at: date
    updated_at: date
    total_commits: int
    topics: list