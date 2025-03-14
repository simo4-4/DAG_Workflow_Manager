## A DAG Workflow Manager by Simo Benkirane
A plug-and-play workflow manager to schedule, run, and monitor workflows.
Plug your custom functions to a workflow and let the system do the rest !
![Alt text](dag_task_manager.drawio.png?raw=true "DAG Workflow Manager")

### Inspiration:
I got inspired from the way Apache Airflow works! Initially, I thought of developing an ETL specific task manager, but it ended up being too limiting and unflexible and therefore decided to abtract each ETL stage into a task.

### Project Structure:

    ├── src/
    │   ├── workflow_management/
    │   ├── api/
    │   ├── user_functions/
    │   └── run_workflow.py         # Main entry point script

#### Workflow Management Structure

    ├── workflow_management/
    │   ├── __init__.py
    │   ├── workflow.py         # Workflow class implementations
    │   ├── workflow_factory.py # Factory for creating workflows
    │   ├── dag_task_manager.py # Core DAG execution engine
    │   ├── config.py           # Configuration classes
    │   └── task.py             # Task base classes and implementations

### Installation:

1. Install the dependencies (preferably on a virtual environment)
    ```
    cd ml-application-dag-task-manager
    pip install -r requirements.txt
    ```

### Running the System
1. Run the Local Server:
    ```
    uvicorn src.api.app:app --host localhost --port 8000
    ```
2. Run the assignment's default assigned workflow `OfferWorkFlow`
    ```
    python -m src.run_workflow
    ```

The results will be available in 2 separate files `plusgrade_performance_summary.json` and `plusgrade_workflow_result.csv` for easy readability

### Running different configs and workflow variations
1. Run a custom configuration for the `OfferWorkFlow`
    ```
    python -m src.run_workflow --config "your config path"
    ```
2. Run a custom workflow
    ```
    python -m src.run_workflow --workflow CustomWorkFlow --config "your config path"
    ```

### Creating Custom Workflows

There are two ways to create custom workflows:

#### 1. Using the Factory Pattern
```python
# 1. Create your workflow class
class CustomWorkflow(PreloadedWorkflow):
    def preload(self) -> None:
        self.add_task(SyncTask("CustomTask1", task1_function))
        self.add_task(SyncTask("CustomTask2", task2_function, dependencies=["CustomTask1"]))

# 2. Add it to the WorkflowFactory inside the create_workflow()
elif workflow_type == "CustomWorkflow":
    config = CustomConfig.from_json_file(config_path)
    logger.info(f"Loaded config: {config}")
    return CustomConfig(config)

# 3. Run from command line
python -m src.run_workflow --workflow CustomWorkflow --config "config.json"
```

#### 2. Direct Instantiation
```python
# Create workflow instance
config = Config.from_json_file("config.json")
workflow = BasicWorkFlow(config)

# Add tasks
workflow.add_task(SyncTask("Extract", extract_function))
workflow.add_task(RequestTask("API Call", api_function, dependencies=["Extract"]))

# Execute
workflow.start()
```

Choose the factory pattern approach when:
- The workflow will be reused
- You want commandline execution support
- You need configuration management

Use direct instantiation for:
- Quick prototyping
- One time workflows
- Interactive development


### How It Works

#### 1. Task Definition & Dependencies
Tasks are the fundamental building blocks of a workflow. 

- Each task function that relies on the results of a previous task must have as input:
- -  `previous_result`: The output of the previous task on which it depends

- Task functions that don't rely on other tasks don't need an input


- And must return:
- - `result`: Output data passed to dependent tasks
- - `item_count`: Number of processed items
- - `failure_count`: Number of failed items

See `offer_workflow_functions.py` and `workflow.py` for implementation examples.

#### 2. Workflow Creation
```python
# Create a workflow instance
workflow = BasicWorkFlow(config)

# Add tasks with dependencies
workflow.add_task(SyncTask("Extract", extract_task))
workflow.add_task(SyncTask("Transform", transform_task, dependencies=["Extract"]))
workflow.add_task(SyncTask("Load", custom_task_function, dependencies=["Transform"]))
```

#### 3. Workflow Execution
```python
# Start the workflow
workflow.start()
```

#### 4. Execution Model
- **Parallel Execution**: Independent tasks run concurrently in separate threads
- **Dependencies**: Tasks execute only after all dependencies complete
- **Task Types**:
  - `SyncTask`: For CPU-bound operations
  - `AsyncTask`: For I/O-bound operations (uses asyncio)
  - `RequestTask`: For HTTP API calls

#### Custom Task Types
You can extend the base `Task` class to create specialized tasks:
- Database ingestion tasks
- Message queue consumers
- Custom processing tasks

> **Performance Tip**: For network-heavy functions, use `AsyncTask` instead of `SyncTask` to leverage asyncio's event loop and avoid thread overhead.

### Advantages
- **Clean Interface**: Intuitive API for workflow creation and management
- **Flexible Architecture**: Easily extensible for custom workflows and tasks
- **Concurrent Execution**: Independent tasks run in parallel using thread pools

### Limitations
- **Sequential Dependencies**: Tasks with dependencies must run sequentially, limiting streaming capabilities
- **Memory Usage**: Complete task results must be held in memory until dependent tasks finish

### Future Improvements

#### Core Features
- **Streaming Processing**: Implement data streaming between dependent tasks
- **Enhanced Error Handling**: Add retry mechanisms
- **Comprehensive Testing**: Expand test coverage for all components
- **Input/Output Validation**: Add Pydantic schemas for data validation between tasks

#### Performance & Monitoring
- **Advanced Metrics**: Add advanced performance tracking and task execution statistics
- **Resource Monitoring**: Track memory usage and thread pool utilization

#### Scalability
- **Distributed Execution**: Support for multi-node task distribution
- **Data Partitioning**: Implement smart data chunking (e.g., by `memberId` hash) for large files
- **Integration Options**: 
  - Apache Kafka for streaming between tasks
  - Apache Spark for large-scale data processing

> [!NOTE]
> The current `OfferWorkFlow` separates ATS, RESP, and OFFER tasks to showcase DAG capabilities. 
> For optimal performance, these could be combined into a single `AsyncTask` using asyncio.
