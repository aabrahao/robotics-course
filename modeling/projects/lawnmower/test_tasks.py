import eml4806.task.task as task
import eml4806.task.executor as executor
import eml4806.task.context as context

def main():
    
    tasks = [
        task.Wait(duration=1.0),
        task.Wait(duration=1.5),
        task.Wait(duration=0.8),
    ]
    
    environment = context.Context()
    scheduler = executor.Executor(context, tasks)

    print("\n--- Starting Executor ---\n")

    t = 0.0
    dt = 0.1

    while True:
        
        state = scheduler.run(dt)

        if state in (task.State.DONE, task.State.FAILED):
            print("--- Executor finished with state:", state.name, "---")
            break

        t += dt
        
if __name__ == "__main__":
    main()