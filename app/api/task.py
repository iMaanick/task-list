from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from app.adapters.sqlalchemy_db.models import User
from app.application.exceptions import MissingTasksError, DataConflictError, TaskNotFoundError
from app.application.fastapi_users import fastapi_users
from app.application.models import TaskCreate, TaskResponse, TaskTitleUpdate, TaskUpdate, ReorderRequest
from app.application.models.task import DeleteTaskResponse, ReorderTasksResponse, Task
from app.application.protocols.database import DatabaseGateway, UoW
from app.application.task import add_task, delete_task_from_list, get_tasks, update_task_title_by_id, update_task_by_id, \
    tasks_reorder

task_router = APIRouter()


@task_router.post("/", response_model=TaskResponse)
async def create_task(
        database: Annotated[DatabaseGateway, Depends()],
        task: TaskCreate,
        user: User = Depends(fastapi_users.current_user(optional=True)),
) -> Task:
    """
    Creates a new task for the authenticated user.

    **Endpoint**: `/tasks/`

    ### Request:
    - **Method**: POST
    - **Body**: A JSON object representing the task to be created.
      Example:
      ```json
      {
          "title": "Sample Task",
          "completed": false,
          "description": "This is a sample task"
      }
      ```

    ### Response:
    - **Status 200**: Returns the created task.
      Example:
      ```json
      {
          "id": 1,
          "title": "Sample Task",
          "completed": false,
          "createdAt": "2024-12-09T12:00:00",
          "description": "This is a sample task"
      }
      ```

    ### Parameters:
    - `database` (DatabaseGateway): Injected database dependency.
    - `task` (TaskCreate): Task details.
    - `user` (User): Authenticated user information.

    ### Returns:
    - `TaskResponse`: The created task details.
    """
    if user is None:
        raise HTTPException(status_code=401, detail="Not authenticated")
    new_task = await add_task(user.id, task, database)
    return new_task


@task_router.delete("/{task_id}", response_model=DeleteTaskResponse)
async def delete_task(
        database: Annotated[DatabaseGateway, Depends()],
        task_id: int,
        user: User = Depends(fastapi_users.current_user(optional=True)),
) -> DeleteTaskResponse:
    """
        Deletes a task by its ID for the authenticated user.

        **Endpoint**: `/tasks/{task_id}`

        ### Request:
        - **Method**: DELETE
        - **Path Parameter**: `task_id` (int) - ID of the task to be deleted.

        ### Response:
        - **Status 200**: Returns a confirmation message.
          Example:
          ```json
          {
              "detail": "Task deleted successfully"
          }
          ```
        - **Status 404**: If the task is not found.
        - **Status 401**: If the user is not authenticated.

        ### Parameters:
        - `database` (DatabaseGateway): Injected database dependency.
        - `task_id` (int): ID of the task to delete.
        - `user` (User): Authenticated user information.

        ### Returns:
        - `DeleteTaskResponse`: Confirmation of task deletion.
        """
    if user is None:
        raise HTTPException(status_code=401, detail="Not authenticated")
    deleted_task_id = await delete_task_from_list(user.id, task_id, database)
    if deleted_task_id is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return DeleteTaskResponse(detail="Task deleted successfully")


@task_router.get("/", response_model=list[TaskResponse])
async def read_tasks(
        database: Annotated[DatabaseGateway, Depends()],
        user: User = Depends(fastapi_users.current_user(optional=True)),
        skip: int = 0,
        limit: int = 10,
) -> list[Task]:
    """
    Retrieves a list of tasks for the authenticated user.

    **Endpoint**: `/tasks/`

    ### Request:
    - **Method**: GET
    - **Query Parameters**:
      - `skip` (int, optional): Number of tasks to skip. Default: 0.
      - `limit` (int, optional): Maximum number of tasks to retrieve. Default: 10.

    ### Response:
    - **Status 200**: Returns a list of tasks.
      Example:
      ```json
      [
          {
              "id": 1,
              "title": "Sample Task",
              "completed": false,
              "createdAt": "2024-12-09T12:00:00",
              "description": "This is a sample task"
          }
      ]
      ```
    - **Status 401**: If the user is not authenticated.

    ### Parameters:
    - `database` (DatabaseGateway): Injected database dependency.
    - `user` (User): Authenticated user information.
    - `skip` (int): Number of tasks to skip.
    - `limit` (int): Maximum number of tasks to retrieve.

    ### Returns:
    - `list[TaskResponse]`: List of tasks for the user.
    """
    if user is None:
        raise HTTPException(status_code=401, detail="Not authenticated")
    tasks = await get_tasks(user.id, skip, limit, database)
    return tasks


@task_router.patch("/{task_id}/title", response_model=TaskResponse)
async def update_task_title(
        task_id: int,
        task_update: TaskTitleUpdate,
        database: Annotated[DatabaseGateway, Depends()],
        uow: Annotated[UoW, Depends()],
        user: User = Depends(fastapi_users.current_user(optional=True)),
) -> Task:
    """
        Updates the title of a task for the authenticated user.

        **Endpoint**: `/tasks/{task_id}/title`

        ### Request:
        - **Method**: PATCH
        - **Path Parameter**: `task_id` (int) - ID of the task to update.
        - **Body**: A JSON object containing the new title.
          Example:
          ```json
          {
              "title": "Updated Task Title"
          }
          ```

        ### Response:
        - **Status 200**: Returns the updated task.
          Example:
          ```json
          {
              "id": 1,
              "title": "Updated Task Title",
              "completed": false,
              "createdAt": "2024-12-09T12:00:00",
              "description": "This is a sample task"
          }
          ```
        - **Status 404**: If the task is not found.
        - **Status 401**: If the user is not authenticated.

        ### Parameters:
        - `task_id` (int): ID of the task to update.
        - `task_update` (TaskTitleUpdate): New title of the task.
        - `database` (DatabaseGateway): Injected database dependency.
        - `uow` (UoW): Unit of Work dependency.
        - `user` (User): Authenticated user information.

        ### Returns:
        - `TaskResponse`: Updated task details.
        """
    if user is None:
        raise HTTPException(status_code=401, detail="Not authenticated")
    updated_task = await update_task_title_by_id(user.id, task_id, task_update, database, uow)
    if updated_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return updated_task


@task_router.put("/{task_id}", response_model=TaskResponse)
async def update_task(
        task_id: int,
        task_update: TaskUpdate,
        database: Annotated[DatabaseGateway, Depends()],
        uow: Annotated[UoW, Depends()],
        user: User = Depends(fastapi_users.current_user(optional=True)),
) -> Task:
    """
       Updates a task's details for the authenticated user.

       **Endpoint**: `/tasks/{task_id}`

       ### Request:
       - **Method**: PUT
       - **Path Parameter**: `task_id` (int) - ID of the task to update.
       - **Body**: A JSON object containing the updated details.
         Example:
         ```json
         {
             "title": "Updated Task Title",
             "completed": true
         }
         ```

       ### Response:
       - **Status 200**: Returns the updated task.
         Example:
         ```json
         {
             "id": 1,
             "title": "Updated Task Title",
             "completed": true,
             "createdAt": "2024-12-09T12:00:00",
             "description": "This is a sample task"
         }
         ```
       - **Status 404**: If the task is not found.
       - **Status 401**: If the user is not authenticated.

       ### Parameters:
       - `task_id` (int): ID of the task to update.
       - `task_update` (TaskUpdate): Updated task details.
       - `database` (DatabaseGateway): Injected database dependency.
       - `uow` (UoW): Unit of Work dependency.
       - `user` (User): Authenticated user information.

       ### Returns:
       - `TaskResponse`: Updated task details.
       """
    if user is None:
        raise HTTPException(status_code=401, detail="Not authenticated")
    updated_task = await update_task_by_id(user.id, task_id, task_update, database, uow)
    if updated_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return updated_task


@task_router.post("/reorder", response_model=ReorderTasksResponse)
async def reorder_tasks(
        reorder_data: ReorderRequest,
        database: Annotated[DatabaseGateway, Depends()],
        user: User = Depends(fastapi_users.current_user(optional=True)),
) -> ReorderTasksResponse:
    """
    Reorders tasks for the authenticated user.

    **Endpoint**: `/tasks/reorder`

    ### Request:
    - **Method**: POST
    - **Body**: A JSON object containing the task IDs and their new positions.
      Example:
      ```json
      {
          "tasks": [
              {"id": 1, "position": 2},
              {"id": 2, "position": 1}
          ]
      }
      ```

    ### Response:
    - **Status 200**: Returns a confirmation message.
      Example:
      ```json
      {
          "detail": "Tasks reordered successfully"
      }
      ```
    - **Status 400**: If required tasks are missing.
    - **Status 404**: If a task is not found.
    - **Status 409**: If there is a data conflict.
    - **Status 401**: If the user is not authenticated.

    ### Parameters:
    - `reorder_data` (ReorderRequest): Task IDs and their new positions.
    - `database` (DatabaseGateway): Injected database dependency.
    - `user` (User): Authenticated user information.

    ### Returns:
    - `ReorderTasksResponse`: Confirmation of task reordering.
    """
    if user is None:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        await tasks_reorder(user.id, reorder_data, database)
    except MissingTasksError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except TaskNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except DataConflictError as e:
        raise HTTPException(status_code=409, detail=str(e))
    return ReorderTasksResponse(detail="Tasks reordered successfully")
