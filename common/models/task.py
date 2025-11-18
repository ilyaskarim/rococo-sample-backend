from dataclasses import dataclass
from typing import ClassVar, Optional
from datetime import datetime

from rococo.models.versioned_model import VersionedModel, ModelValidationError


@dataclass
class Task(VersionedModel):
    use_type_checking: ClassVar[bool] = True

    person_id: str = None
    title: str = None
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    priority: str = 'medium'
    is_completed: bool = False
    completed_on: Optional[datetime] = None

    def __post_init__(self, *args, **kwargs):
        super().__post_init__(*args, **kwargs)
        # Validation is called explicitly in service layer before save operations
        # to avoid validation errors when ORM reconstructs objects from database

    def validate_task(self):
        """Validate task fields"""
        errors = []

        # Validate title
        if not self.title or not isinstance(self.title, str):
            errors.append("Title is required and must be a string")
        elif len(self.title.strip()) == 0:
            errors.append("Title cannot be empty")
        elif len(self.title) > 255:
            errors.append("Title cannot exceed 255 characters")

        # Validate priority
        valid_priorities = ['low', 'medium', 'high', 'urgent']
        if self.priority and self.priority not in valid_priorities:
            errors.append(f"Priority must be one of: {', '.join(valid_priorities)}")

        # Validate person_id
        if not self.person_id or not isinstance(self.person_id, str):
            errors.append("Person ID is required and must be a string")

        if errors:
            raise ModelValidationError(errors)

    def as_dict(self, *args, **kwargs):
        """Convert task to dictionary for API responses"""
        return {
            'entity_id': self.entity_id,
            'version': self.version,
            'person_id': self.person_id,
            'title': self.title,
            'description': self.description,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'priority': self.priority,
            'is_completed': self.is_completed,
            'completed_on': self.completed_on.isoformat() if self.completed_on else None,
            'changed_on': self.changed_on.isoformat() if self.changed_on else None,
            'active': self.active
        }
