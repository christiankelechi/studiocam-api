"""AI Generation Job Repository."""

from typing import List
from app.models.ai import GenerationJob
from app.repositories.base import ThreadSafeInMemoryRepository


class GenerationJobRepository(ThreadSafeInMemoryRepository[GenerationJob]):
    """Thread-safe Repository for AI Processing Jobs."""

    def list_by_user(self, user_id: str) -> List[GenerationJob]:
        """List generation jobs for a user ordered by creation time descending."""
        with self._lock:
            jobs = [j for j in self._storage.values() if j.user_id == user_id]
            jobs.sort(key=lambda j: j.created_at, reverse=True)
            return jobs


# Global singleton instance
job_repository = GenerationJobRepository()

