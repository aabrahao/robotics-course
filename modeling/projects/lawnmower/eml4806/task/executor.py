from __future__ import annotations

from typing import Any, Iterable, List, Optional, Protocol
from eml4806.task.task import TaskState

from eml4806.task.context import Context

class Executor:
    def __init__(self, context: Context, tasks=[]) -> None:
        self._context = context
        self._tasks = list(tasks)
        self._task_index: int = 0

    def set(self, tasks) -> None:
        self._tasks = list(tasks)
        self._task_index = 0

    def add(self, task) -> None:
        self._tasks.append(task)

    def clear(self) -> None:
        self._tasks = []
        self._task_index = 0

    def current(self) -> Any:
        if 0 <= self._task_index < len(self._tasks):
            return self._tasks[self._task_index]
        return None

    def finished(self) -> bool:
        return self._task_index >= len(self._tasks)

    def run(self, dt: float) -> TaskState:
        
        # Shared memory between tasks
        context = self._context

        # No tasks left
        if self.finished():
            return TaskState.DONE

        current = self.current()
        if current is None:
            return TaskState.DONE

        # First touch: setup
        if current.state is TaskState.READY:
            current.setup(context, dt)
            current.state = TaskState.RUNNING

        new_state = current.run(context, dt)
        current.state = new_state

        # FAILED
        if new_state is TaskState.FAILED:
            current.cleanup(context, dt)
            return TaskState.FAILED

        # DONE
        if new_state is TaskState.DONE:
            current.cleanup(context, dt)
            self._task_index += 1

            if self.finished():
                return TaskState.DONE
            return TaskState.RUNNING

        # RUNNING or other non-terminal state
        return new_state
