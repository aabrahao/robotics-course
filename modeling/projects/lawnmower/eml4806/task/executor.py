from __future__ import annotations

from typing import Iterable, List, Optional

import eml4806.task.task as task

class Executor:
    def __init__(self, context, tasks=[]):
        self.context = context
        self.tasks = list(tasks)
        self.index = 0

    def set(self, tasks):
        self.tasks = list(tasks)
        self.index = 0

    def add(self, t):
        self.tasks.append(t)

    def clear(self):
        self.tasks.clear()
        self.index = 0

    def current(self):
        if 0 <= self.index < len(self.tasks):
            return self.tasks[self.index]
        return None

    def finished(self):
        return self.index >= len(self.tasks)

    def run(self, dt):
        s = task.State
        c = self.context
        # Already finished or no tasks
        if self.finished():
            return s.DONE
        current = self.current()
        if current is None:
            return s.DONE
        if current.state is s.READY:
            current.setup(c, dt)
            current.state = s.RUNNING
        state = current.run(c, dt)
        current.state = state
        if state is s.FAILED:
            current.cleanup(c, dt)
            return s.FAILED
        if state is s.DONE:
            current.cleanup(c, dt)
            self.index += 1
            return s.DONE if self.finished() else s.RUNNING
        return s.RUNNING
