# ML Application Engineer Take Home Exam
Welcome to the ML Application Engineer take home assignment.

Your task is to build a low-latency process that will process data, run the endpoints within the `app.py` file in a local application server, send it to ML Endpoints to get predictions, send those prediction results to offers endpoint to get which offers to give to which members, and finally record the results. 

## Solution: A DAG Workflow Manager by Simo Benkirane

![Alt text](dag_task_manager.drawio.png?raw=true "DAG Workflow Manager")

### Inspiration:
I got inspired from the way Apache Airflow works! Initially, I thought of developing an ETL specific task manager, but it ended up being too limiting and unflexible and therefore decided to abtract each ETL stage into a task. Would love to further improve this implementation to possibly allow each task to run on a distributed server where a streaming queue such as Apache Kafka runs between the dependent tasks

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
- **Enhanced Error Handling**: Add retry mechanisms and failure recovery
- **Comprehensive Testing**: Expand test coverage for all components
- **Input/Output Validation**: Add Pydantic schemas for data validation between tasks

#### Performance & Monitoring
- **Advanced Metrics**: Add advanced performance tracking and task execution statistics
- **Structured Logging**: Implement detailed logging with correlation IDs
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

## The Assigned Task/Workflow
- Create a Python process which will:

    1. Read member data from the `member_data.csv` file. Not all data entries have all the columns in it, and some members will have multiple entries, which will be relevant for the next step. The csv file contains the following columns:
        - MEMBER_ID
        - LAST_TRANSACTION_TS (in UTC)
        - LAST_TRANSACTION_TYPE (buy, gift, redeem)
        - LAST_TRANSACTION_POINTS_BOUGHT (can be negative for redemption)
        - LAST_TRANSACTION_REVENUE_USD

    2. Transform the input member dataset into features for each member, which will have the following columns:

        - AVG_POINTS_BOUGHT, calculated as $\text{total points bought} / \text{number of transactions}$
        - AVG_REVENUE_USD, calculated as $\text{total transaction revenue} / \text{number of transactions}$
        - LAST_3_TRANSACTIONS_AVG_POINTS_BOUGHT, which is the AVG_POINTS_BOUGHT for the 3 most recent transactions
        - LAST_3_TRANSACTIONS_AVG_REVENUE_USD, which is the AVG_REVENUE_USD for the 3 most recent transactions
        - PCT_BUY_TRANSACTIONS, calculated as $\text{Number of transactions where transaction type was BUY} / \text{number of transactions}$
        - PCT_GIFT_TRANSACTIONS, calculated as $\text{Number of transactions where transaction type was GIFT} / \text{number of transactions}$
        - PCT_REDEEM_TRANSACTIONS, calculated as $\text{Number of transactions where transaction type was REDEEM} / \text{number of transactions}$
        - DAYS_SINCE_LAST_TRANSACTION, which is the number of days since a member's last transaction. (ie. Current day in UTC - last day of transaction in UTC)

    3. POST these inputs to the ATS (Average Transaction Size) and RESP (Probability to respond) prediction endpoints to get the estimated amount and likelihood of purchase respectively per member. The endpoints can be found in the `app.py` file, and they both take the member features described in the previous step as input.
    4. Combine the ATS and RESP predictions from the previous step into the Prediction object (found in `prediction.py`). This object can then be sent to the offer endpoint found in the `app.py` file to get which offer should be given to the member
    5. Store any data you produce thorougout the process in a file. The data should easily be able to be used for analyzing the performance, and should include the following:
        - Member features
        - Predictions
        - Offers assigned to each member
        - Latency and throughput of each step (e.g. time taken to read member data, to transformm...)
        - Any other data that can be used for performance analysis

- Create a CI/CD process that will:
  - Unit test the code
  - Be easily usable for multiple partners, which may have different requests, ML endpoints and features
## What we're looking for
- Processing speed/Parallelism/Latency
- Design patterns/programming paradigm
- Scalability
- Documentation
- Clean Code
- Testing
- Automated Testing
- Error Handling
- Readability
- Logging
- CI/CD
