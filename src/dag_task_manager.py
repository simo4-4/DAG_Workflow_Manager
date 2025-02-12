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
        self.dag = nx.DiGraph() 
        self.results = {} 
        self.execution_time = None

    def add_task(self, task: Task) -> None:
        """Adds a new task to the DAG"""
        if task.name in self.tasks:
            raise ValueError(f"Task {task.name} already exists.")
        
        self.tasks[task.name] = task
        self.dag.add_node(task.name)

        if task.dependencies:
            for dep in task.dependencies:
                if dep not in self.tasks:
                    raise ValueError(f"Dependency {dep} not found for task {task.name}.")
                self.dag.add_edge(dep, task.name)

    def execute(self):
        start_time = time.time()
        """Executes the DAG tasks following dependency order"""
        if not nx.is_directed_acyclic_graph(self.dag):
            raise ValueError("The task dependencies form a cycle!")

        sorted_tasks = list(nx.topological_sort(self.dag)) 
        completed_tasks = set()

        with ThreadPoolExecutor() as executor:
            futures = {}

            while sorted_tasks:
                ready_tasks = [
                    task for task in sorted_tasks if set(self.tasks[task].dependencies).issubset(completed_tasks)
                ]

                if not ready_tasks:
                    raise RuntimeError("Deadlock detected in task execution!")

                for task_name in ready_tasks:
                    task = self.tasks[task_name]
                    dependency_results = [self.results[dep] for dep in task.dependencies]
                    futures[task_name] = executor.submit(task.execute, dependency_results)
                    sorted_tasks.remove(task_name)

                for future in as_completed(futures.values()):
                    for task_name, f in futures.items():
                        if f == future:
                            self.results[task_name] = future.result()
                            completed_tasks.add(task_name)
                            break
        self.execution_time = time.time() - start_time

    def get_summary(self):
        """Returns execution results and performance summary as a dictionary"""
        summary = {
            "tasks": {},
            "total_execution_time (sec)": self.execution_time,
            "UTC_time_of_completion": time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
        }

        for task_name, task in self.tasks.items():
            summary["tasks"][task_name] = {
                "status": "Success" if task.failure_count == 0 and task.result_count != 0 else "Failed",
                "execution_time (sec)": task.execution_time,
                "processed_item_count": task.result_count,
                "item_failure_count": task.failure_count,
                "throughput (item/sec)": task.result_count / task.execution_time if task.execution_time else 0
            }

        return summary