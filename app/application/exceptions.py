class DatabaseError(Exception):
    pass


class MissingTasksError(DatabaseError):
    def __init__(self, missing_task_ids):
        self.missing_task_ids = missing_task_ids
        super().__init__(f"Some tasks not found: {missing_task_ids}")


class TaskNotFoundError(DatabaseError):
    def __init__(self, task_id):
        self.task_id = task_id
        super().__init__(f"Task with id {task_id} not found")


class DataConflictError(DatabaseError):
    def __init__(self, message):
        super().__init__(message)
