from common.repositories.base import BaseRepository
from common.models.task import Task


class TaskRepository(BaseRepository):
    MODEL = Task

    def get_by_person_id(self, person_id: str, status_filter: str = None):
        """
        Get all tasks for a specific person

        Args:
            person_id: The person's entity_id
            status_filter: Optional filter - 'completed', 'incomplete', or None for all

        Returns:
            List of Task objects
        """
        conditions = {"person_id": person_id, "active": True}

        if status_filter == 'completed':
            conditions["is_completed"] = True
        elif status_filter == 'incomplete':
            conditions["is_completed"] = False
        # If None, get all tasks (both completed and incomplete)

        return self.get_many(conditions)

    def get_by_id_and_person(self, task_id: str, person_id: str):
        """
        Get a specific task by ID, ensuring it belongs to the person

        Args:
            task_id: The task's entity_id
            person_id: The person's entity_id

        Returns:
            Task object or None
        """
        return self.get_one({"entity_id": task_id, "person_id": person_id, "active": True})
