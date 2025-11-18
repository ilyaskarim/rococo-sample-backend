from flask_restx import Namespace, Resource
from flask import request
from datetime import datetime

from app.helpers.response import get_success_response, get_failure_response, parse_request_body, validate_required_fields
from app.helpers.decorators import login_required
from common.app_config import config
from common.services.task import TaskService
from common.helpers.exceptions import APIException

# Create the task namespace
task_api = Namespace('task', description="Task management APIs")


@task_api.route('/')
class TaskList(Resource):

    @login_required()
    @task_api.doc(params={'status': 'Filter by status: completed, incomplete, or all (default: all)'})
    def get(self, person):
        """
        Get all tasks for the authenticated user
        Query parameter 'status' can be: 'completed', 'incomplete', or omitted for all tasks
        """
        task_service = TaskService(config)

        # Get status filter from query parameters
        status = request.args.get('status', 'all')

        # Normalize the status filter
        if status == 'all' or status is None:
            status_filter = None
        elif status in ['completed', 'incomplete']:
            status_filter = status
        else:
            return get_failure_response(
                message="Invalid status filter. Use 'completed', 'incomplete', or 'all'",
                status_code=400
            )

        tasks = task_service.get_tasks(person.entity_id, status_filter)
        tasks_data = [task.as_dict() for task in tasks]

        return get_success_response(tasks=tasks_data, count=len(tasks_data))

    @login_required()
    @task_api.expect({
        'type': 'object',
        'properties': {
            'title': {'type': 'string', 'description': 'Task title (required)'},
            'description': {'type': 'string', 'description': 'Task description (optional)'},
            'due_date': {'type': 'string', 'format': 'date-time', 'description': 'Due date in ISO format (optional)'},
            'priority': {'type': 'string', 'enum': ['low', 'medium', 'high', 'urgent'], 'description': 'Task priority (default: medium)'}
        },
        'required': ['title']
    })
    def post(self, person):
        """
        Create a new task for the authenticated user
        """
        parsed_body = parse_request_body(request, ['title', 'description', 'due_date', 'priority'])

        # Validate required fields
        if not parsed_body.get('title'):
            return get_failure_response(message="'title' is required and cannot be empty", status_code=400)

        task_service = TaskService(config)

        # Parse due_date if provided
        due_date = None
        if parsed_body.get('due_date'):
            try:
                due_date = datetime.fromisoformat(parsed_body['due_date'].replace('Z', '+00:00'))
            except ValueError:
                return get_failure_response(
                    message="Invalid due_date format. Use ISO format (e.g., 2024-12-31T23:59:59)",
                    status_code=400
                )

        try:
            task = task_service.create_task(
                person_id=person.entity_id,
                title=parsed_body['title'],
                description=parsed_body.get('description'),
                due_date=due_date,
                priority=parsed_body.get('priority', 'medium')
            )

            return get_success_response(task=task.as_dict(), message="Task created successfully", status_code=201)

        except Exception as e:
            raise e
            return get_failure_response(message=str(e), status_code=400)


@task_api.route('/<string:task_id>')
class TaskDetail(Resource):

    @login_required()
    def get(self, person, task_id):
        """
        Get a specific task by ID
        """
        task_service = TaskService(config)

        try:
            task = task_service.get_task_by_id(task_id, person.entity_id)
            return get_success_response(task=task.as_dict())

        except APIException as e:
            return get_failure_response(message=str(e), status_code=e.status_code)

    @login_required()
    @task_api.expect({
        'type': 'object',
        'properties': {
            'title': {'type': 'string', 'description': 'Task title'},
            'description': {'type': 'string', 'description': 'Task description'},
            'due_date': {'type': 'string', 'format': 'date-time', 'description': 'Due date in ISO format'},
            'priority': {'type': 'string', 'enum': ['low', 'medium', 'high', 'urgent'], 'description': 'Task priority'},
            'is_completed': {'type': 'boolean', 'description': 'Task completion status'}
        }
    })
    def put(self, person, task_id):
        """
        Update a task
        """
        parsed_body = parse_request_body(request, ['title', 'description', 'due_date', 'priority', 'is_completed'])
        task_service = TaskService(config)

        # Parse due_date if provided
        due_date = None
        if parsed_body.get('due_date'):
            try:
                due_date = datetime.fromisoformat(parsed_body['due_date'].replace('Z', '+00:00'))
            except ValueError:
                return get_failure_response(
                    message="Invalid due_date format. Use ISO format (e.g., 2024-12-31T23:59:59)",
                    status_code=400
                )

        try:
            task = task_service.update_task(
                task_id=task_id,
                person_id=person.entity_id,
                title=parsed_body.get('title'),
                description=parsed_body.get('description'),
                due_date=due_date,
                priority=parsed_body.get('priority'),
                is_completed=parsed_body.get('is_completed')
            )

            return get_success_response(task=task.as_dict(), message="Task updated successfully")

        except APIException as e:
            return get_failure_response(message=str(e), status_code=e.status_code)
        except Exception as e:
            return get_failure_response(message=str(e), status_code=400)

    @login_required()
    def delete(self, person, task_id):
        """
        Delete a task (soft delete)
        """
        task_service = TaskService(config)

        try:
            task_service.delete_task(task_id, person.entity_id)
            return get_success_response(message="Task deleted successfully")

        except APIException as e:
            return get_failure_response(message=str(e), status_code=e.status_code)


@task_api.route('/<string:task_id>/complete')
class TaskComplete(Resource):

    @login_required()
    def patch(self, person, task_id):
        """
        Mark a task as complete
        """
        task_service = TaskService(config)

        try:
            task = task_service.mark_as_complete(task_id, person.entity_id)
            return get_success_response(task=task.as_dict(), message="Task marked as complete")

        except APIException as e:
            return get_failure_response(message=str(e), status_code=e.status_code)
