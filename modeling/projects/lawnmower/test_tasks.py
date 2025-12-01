from __future__ import annotations

from eml4806.task.task import AbstractTask, WaitTask, TaskState
from eml4806.task.executor import Executor
from eml4806.task.context import Context

class EchoTask(AbstractTask):
    def __init__(self, n: int) -> None:
        self.count: int = n
        self.index: int = 0
        super().__init__(name="Echo", arguments=f"count: {n}")

    def setup(self, context: Context, dt: float) -> None:
        """Called once before the first run()."""
        super().setup(context, dt)
        self.index = 0
        print(f"[{self.name}] initialzed...")

    def run(self, context: Context, dt: float) -> TaskState:
        """Do one non-blocking step. Return new state."""
        # Already done? (defensive)
        if self.index >= self.count:
            return TaskState.DONE
        # Safely get the message from context
        message = getattr(context, "variable1", "<no message>")
        print(f'[{self.index}] "{message}"')
        self.index += 1
        # Check termination after increment
        return TaskState.RUNNING

    def cleanup(self, context: Context, dt: float) -> None:
        """Called once when DONE or FAILED."""
        print(f"[{self.name}] finalized!")
        super().cleanup(context, dt)
        self.index = 0

def main() -> None:
    tasks = [
        WaitTask(duration=1.0),
        EchoTask(4),
        WaitTask(duration=1.5),
        EchoTask(4),
        WaitTask(duration=0.8),
    ]

    # Shared memory with all classes
    context = Context()
    context.variable1 = "Robotics rocks!"

    # Scheduler
    executor = Executor(context, tasks)

    print("--- Executor Started ---")

    t = 0.0
    dt = 0.1

    while True:
        # Run each task in sequence
        state = executor.run(dt)

        if state in (TaskState.DONE, TaskState.FAILED):
            print("--- Executor finished with state:", state.name, "---")
            break

        t += dt

if __name__ == "__main__":
    main()
