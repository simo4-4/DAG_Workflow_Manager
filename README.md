# ML Application Engineer Take Home Exam
Welcome to the ML Application Engineer take home assignment.

Your task is to build a low-latency process that will process data, run the endpoints within the `app.py` file in a local application server, send it to ML Endpoints to get predictions, send those prediction results to offers endpoint to get which offers to give to which members, and finally record the results. 

## Solution: A DAG Workflow Manager by Simo Benkirane

![Alt text](dag_task_manager.drawio.png?raw=true "DAG Workflow Manager")

### Inspiration:
I got inspired from the way Apache Airflow works! Initially, I thought of developing an ETL specific task manager, but it ended up being too limiting and unflexible and therefore decided to abtract each ETL stage into a task. Would love to further improve this implementation to possibly allow each task to run on a distributed server where a streaming queue such as Apache Kafka runs between the dependencies

### Usage:
- To run the default configuration:  
  `python -m src.run_workflow` which will run a OfferWorkFlow instance by default
  
- To run with a custom configuration from the command line:  
  `python -m src.run_workflow --config "your config path"`
  
- To define and run your custom workflow from the command line
- -  Create a new workflow class extending the PreloadedWorkflow class, add it to the factory pattern, run it through the `run_workflow` file using the `--workflow` argument.
- - (E.g, `python -m src.run_workflow --workflow CustomWorkFlow --config "your config path"`)
- - See the `OfferWorkFlow` class inside the `workflow.py` file for a concrete example
- You can also run a custom workflow by instantiating an instance of the `BasicWorkFlow` and add `Tasks` to it and run it from a python interpretor

### How It Works:
1. **Task Definition & Dependencies**:  
   Define your tasks and their dependencies using an easy-to-use interface. Each function used to instantie a task needs to output a `result` which will be used as input for the next dependent task, a `item_count` representing the number of items_processed, and a `failure_count `representing the number of items that fails to be processed. See `offer_workflow_function.py` for an example.

2. **Add them to a workflow**:
    Use the add_task() method on an instantied BasicWorkFlow to add your tasks

2. **Run your WorkFlow**:
    Call the start() method on your workflow to run it!
   
2. **Task Execution**:  
   Tasks are executed in the order defined within a workflow, with independent tasks running in parallel.

3. **Threaded Execution**:  
   Each task runs in its own thread.

- **Task Information**:
   - A task is a basic unit of execution that has dependencies with other tasks
   - You can extend the Task class and create your own custom Task, which can be reusuable or not, as you see fit ! For example, you cound have a task in charge of ingesting data from a database or from a RabbitMQ queue which would then pass the results to the next component.
   - For **Network I/O-heavy tasks**, use the **AsyncTask** type where Asyncio event loops are used for concurrency to avoid the overhead of additional threads.

### Pros:
- Clean interface
- Fully **Customizable**.
- Independent tasks run in **parallel threads**.

### Cons:
- **Dependent tasks** run sequentially and cannot stream or utilize intermediate outputs.

### Areas for Improvement:
- **Streaming between dependent tasks** rather than waiting for one task to complete before starting the next
- **Error handling** is currently limited and needs enhancement
- **Testing** only cover the the extract and trasform tasks, we still need to cover the other tasks, the DAG task manager, the workflows, ect...
- **More Metrics** can be further added
- **Better logging** can be further added
- **Input and output validation between each task** could be enforced using a pydantic schema
- **Allow for distributed workflows** for files and inputs that can partitioned and ran on different servers separately
- - For example, we could chunk a CSV file by a hash of `memberId`, ensuring rows with the same `memberId` are grouped together and run the partitions on different processes or machines. Alternatively, a solution using Spark can be considered if streaming is implemented between the tasks.

### Note
In my OfferWorkFlow workflow, I intentionnally seperated the ATS, RESP, and OFFER tasks to demonstrate the DAG and its dependency management. The workflow would run faster if I combined them into one AsyncTask leveraging the concurrency of the events loop.


## Setup
You can install the necessary packages by running the `pip install -r requirements.txt` command.

A part of this assignment requires you to run a local application to interact with the endpoints defined in `app.py` You can use any tool of your choosing to accomplish this, however it is worth noting that this project comes with [uvicorn](https://www.uvicorn.org/) by default, which can be used to run the said server.

## The Task
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
