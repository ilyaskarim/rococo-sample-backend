from datetime import datetime
from typing import Optional, List

from common.repositories.factory import RepositoryFactory, RepoType
from common.models.task import Task
from common.helpers.exceptions import APIException


class TaskService:

    def __init__(self, config):
        self.config = config
        self.repository_factory = RepositoryFactory(config)
        self.task_repo = self.repository_factory.get_repository(RepoType.TASK)

    def create_task(
        self,
        person_id: str,
        title: str,
        description: Optional[str] = None,
        due_date: Optional[datetime] = None,
        priority: str = 'medium'
    ) -> Task:
        """
        Create a new task for a person

        Args:
            person_id: The person's entity_id
            title: Task title (required)
            description: Task description (optional)
            due_date: Task due date (optional)
            priority: Task priority - 'low', 'medium', 'high', or 'urgent' (default: 'medium')

        Returns:
            Created Task object
        """
        task = Task(
            person_id=person_id,
            title=title,
            description=description,
            due_date=due_date,
            priority=priority,
            is_completed=False,
            completed_on=None
        )

        # Validate task before saving
        task.validate_task()

        return self.task_repo.save(task)

    def get_tasks(self, person_id: str, status_filter: Optional[str] = None) -> List[Task]:
        """
        Get all tasks for a person

        Args:
            person_id: The person's entity_id
            status_filter: Optional filter - 'completed', 'incomplete', or None for all

        Returns:
            List of Task objects
        """
        return self.task_repo.get_by_person_id(person_id, status_filter)

    def get_task_by_id(self, task_id: str, person_id: str) -> Task:
        """
        Get a specific task by ID, ensuring it belongs to the person

        Args:
            task_id: The task's entity_id
            person_id: The person's entity_id

        Returns:
            Task object

        Raises:
            APIException: If task not found or doesn't belong to person
        """
        task = self.task_repo.get_by_id_and_person(task_id, person_id)

        if not task:
            raise APIException("Task not found", status_code=404)

        return task

    def update_task(
        self,
        task_id: str,
        person_id: str,
        title: Optional[str] = None,
        description: Optional[str] = None,
        due_date: Optional[datetime] = None,
        priority: Optional[str] = None,
        is_completed: Optional[bool] = None
    ) -> Task:
        """
        Update a task

        Args:
            task_id: The task's entity_id
            person_id: The person's entity_id
            title: New title (optional)
            description: New description (optional)
            due_date: New due date (optional)
            priority: New priority (optional)
            is_completed: New completion status (optional)

        Returns:
            Updated Task object

        Raises:
            APIException: If task not found or doesn't belong to person
        """
        task = self.get_task_by_id(task_id, person_id)

        # Update fields if provided
        if title is not None:
            task.title = title
        if description is not None:
            task.description = description
        if due_date is not None:
            task.due_date = due_date
        if priority is not None:
            task.priority = priority
        if is_completed is not None:
            task.is_completed = is_completed
            # Set/clear completed_on timestamp based on completion status
            if is_completed:
                task.completed_on = datetime.now()
            else:
                task.completed_on = None

        # Validate task before saving
        task.validate_task()

        return self.task_repo.save(task)

    def mark_as_complete(self, task_id: str, person_id: str) -> Task:
        """
        Mark a task as complete

        Args:
            task_id: The task's entity_id
            person_id: The person's entity_id

        Returns:
            Updated Task object

        Raises:
            APIException: If task not found or doesn't belong to person
        """
        task = self.get_task_by_id(task_id, person_id)

        task.is_completed = True
        task.completed_on = datetime.now()

        return self.task_repo.save(task)

    def delete_task(self, task_id: str, person_id: str) -> bool:
        """
        Delete a task (soft delete - sets active=False)

        Args:
            task_id: The task's entity_id
            person_id: The person's entity_id

        Returns:
            True if successful

        Raises:
            APIException: If task not found or doesn't belong to person
        """
        task = self.get_task_by_id(task_id, person_id)

        task.active = False
        self.task_repo.save(task)

        return True
