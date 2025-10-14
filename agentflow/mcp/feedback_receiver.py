import asyncio
import uuid
from datetime import datetime
from typing import Dict, List, Optional

class FeedbackManager:
    """
    A class to manage feedback asynchronously using in-memory storage.

    Attributes:
        _feedback_store (Dict[str, Dict]): A dictionary storing feedback records.
        _lock (asyncio.Lock): A lock to ensure thread-safe operations.
    """

    def __init__(self) -> None:
        """
        Initializes the FeedbackManager with an empty feedback store and a lock.
        """
        self._feedback_store: Dict[str, Dict] = {}
        self._lock = asyncio.Lock()

    async def add_feedback(self, user_id: str, feedback_text: str, rating: int) -> str:
        """
        Adds feedback to the feedback store and returns the unique feedback ID.

        Args:
            user_id (str): The ID of the user submitting feedback.
            feedback_text (str): The feedback text.
            rating (int): The rating given by the user (1-5).

        Returns:
            str: The unique feedback ID.

        Raises:
            ValueError: If feedback_text is empty or rating is invalid.
        """
        if not feedback_text:
            raise ValueError("Feedback text cannot be empty.")
        if not isinstance(rating, int) or rating < 1 or rating > 5:
            raise ValueError("Rating must be an integer between 1 and 5.")

        feedback_id = str(uuid.uuid4())
        feedback_record = {
            "id": feedback_id,
            "user_id": user_id,
            "text": feedback_text,
            "rating": rating,
            "timestamp": datetime.utcnow(),
        }

        async with self._lock:
            self._feedback_store[feedback_id] = feedback_record

        return feedback_id

    async def get_feedback(self, feedback_id: str) -> Optional[Dict]:
        """
        Retrieves a feedback record by its ID.

        Args:
            feedback_id (str): The ID of the feedback record.

        Returns:
            Dict: The feedback record if found, else None.
        """
        async with self._lock:
            return self._feedback_store.get(feedback_id)

    async def get_user_feedback(self, user_id: str) -> List[Dict]:
        """
        Retrieves all feedback records for a given user.

        Args:
            user_id (str): The ID of the user.

        Returns:
            List[Dict]: A list of feedback records for the user.
        """
        async with self._lock:
            return [
                feedback for feedback in self._feedback_store.values()
                if feedback["user_id"] == user_id
            ]

    async def delete_feedback(self, feedback_id: str) -> bool:
        """
        Deletes a feedback record by its ID.

        Args:
            feedback_id (str): The ID of the feedback record.

        Returns:
            bool: True if the feedback was deleted, False if it was not found.
        """
        async with self._lock:
            if feedback_id in self._feedback_store:
                del self._feedback_store[feedback_id]
                return True
            return False

    async def calculate_average_rating(self, user_id: str) -> Optional[float]:
        """
        Calculates the average rating for a given user.

        Args:
            user_id (str): The ID of the user.

        Returns:
            Optional[float]: The average rating if feedback exists, else None.
        """
        user_feedback = await self.get_user_feedback(user_id)
        if not user_feedback:
            return None

        total_rating = sum(feedback["rating"] for feedback in user_feedback)
        return total_rating / len(user_feedback)