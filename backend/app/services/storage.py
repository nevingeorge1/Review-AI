"""Storage repository abstractions and implementations for ReviewAI.

Decouples review domain persistence from databases (In-Memory, SQLite, PostgreSQL).
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Tuple
from backend.app.schemas.review import ReviewResponse


class ReviewRepository(ABC):
    """Abstract interface for persisting and querying code review records."""

    @abstractmethod
    async def create_review(self, review: ReviewResponse) -> ReviewResponse:
        """Persist a new review record."""
        pass

    @abstractmethod
    async def get_review(self, review_id: str) -> Optional[ReviewResponse]:
        """Retrieve a review record by unique review ID."""
        pass

    @abstractmethod
    async def list_reviews(self, limit: int = 20, offset: int = 0) -> Tuple[List[ReviewResponse], int]:
        """List historical review records with pagination and return total count."""
        pass

    @abstractmethod
    async def update_review(self, review: ReviewResponse) -> Optional[ReviewResponse]:
        """Update an existing review record."""
        pass

    @abstractmethod
    async def delete_review(self, review_id: str) -> bool:
        """Delete a review record by ID."""
        pass

    @abstractmethod
    async def count(self) -> int:
        """Return total count of stored reviews."""
        pass


class InMemoryReviewRepository(ReviewRepository):
    """Thread-safe in-memory repository implementation for development, testing, and foundation."""

    def __init__(self) -> None:
        self._storage: Dict[str, ReviewResponse] = {}

    async def create_review(self, review: ReviewResponse) -> ReviewResponse:
        self._storage[review.review_id] = review
        return review

    async def get_review(self, review_id: str) -> Optional[ReviewResponse]:
        return self._storage.get(review_id)

    async def list_reviews(self, limit: int = 20, offset: int = 0) -> Tuple[List[ReviewResponse], int]:
        items = list(self._storage.values())
        # Sort descending by creation date
        items.sort(key=lambda r: r.created_at, reverse=True)
        total = len(items)
        paginated = items[offset : offset + limit]
        return paginated, total

    async def update_review(self, review: ReviewResponse) -> Optional[ReviewResponse]:
        if review.review_id in self._storage:
            self._storage[review.review_id] = review
            return review
        return None

    async def delete_review(self, review_id: str) -> bool:
        if review_id in self._storage:
            del self._storage[review_id]
            return True
        return False

    async def count(self) -> int:
        return len(self._storage)
