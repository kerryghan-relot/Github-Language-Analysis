from datetime import date
from dataclasses import dataclass

@dataclass
class RepositorySummary:
    name: str
    created_at: date
    updated_at: date
    file_count: int
    release_count: int
    size: int
    star_count: int
    fork_count: int
    contributor_count: int
    commit_count: int
    issue_count: int
    topics: list