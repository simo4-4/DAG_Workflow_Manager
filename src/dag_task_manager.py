import json
import logging
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from src.task import Task
import networkx as nx

logger = logging.getLogger(__name__)

class DAGTaskManager:
    def __init__(self):
        self.tasks = {}
        self.dag = nx.DiGraph()  # DAG using NetworkX
        self.results = {}  # Store task results
        self.execution_time = None

    def add_task(self, task: Task) -> None:
        """Adds a new task to the DAG."""
        if task.name in self.tasks:
            raise ValueError(f"Task {task.name} already exists.")
        
        self.tasks[task.name] = task
        self.dag.add_node(task.name)

        if task.dependencies:
            for dep in task.dependencies:
                if dep not in self.tasks:
                    raise ValueError(f"Dependency {dep} not found for task {task.name}.")
                self.dag.add_edge(dep, task.name)  # Ensure dependency order

    def execute(self):
        start_time = time.time()
        """Executes the DAG tasks following dependency order."""
        if not nx.is_directed_acyclic_graph(self.dag):
            raise ValueError("The task dependencies form a cycle!")

        sorted_tasks = list(nx.topological_sort(self.dag))  # Get execution order
        completed_tasks = set()

        with ThreadPoolExecutor() as executor:
            futures = {}  # Map task name to Future object

            while sorted_tasks:
                ready_tasks = [
                    task for task in sorted_tasks if set(self.tasks[task].dependencies).issubset(completed_tasks)
                ]

                if not ready_tasks:
                    raise RuntimeError("Deadlock detected in task execution!")

                for task_name in ready_tasks:
                    task = self.tasks[task_name]
                    dependency_results = [self.results[dep] for dep in task.dependencies]  # Get dependency outputs
                    futures[task_name] = executor.submit(task.execute, dependency_results)
                    sorted_tasks.remove(task_name)

                for future in as_completed(futures.values()):
                    for task_name, f in futures.items():
                        if f == future:
                            self.results[task_name] = future.result()  # Store result
                            completed_tasks.add(task_name)
                            break
        self.execution_time = time.time() - start_time

    def get_summary(self):
        """Returns execution results and performance summary as a dictionary."""
        summary = {
            "tasks": {},
            "total_execution_time (sec)": self.execution_time
        }

        for task_name, task in self.tasks.items():
            summary["tasks"][task_name] = {
                "status": "Success" if task.result is not None else "Failed",
                "execution_time (sec)": task.execution_time,
                "processed_items": task.result_count,
                "throughput (item/sec)": task.result_count / task.execution_time if task.execution_time else 0
            }

        return summary

    def save_summary(self, output_file):
        """Saves execution results and performance summary to a JSON file."""
        summary = self.get_summary()
        with open(output_file, "w") as f:
            json.dump(summary, f, indent=4)