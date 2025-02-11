# ML Application Engineer Take Home Exam
Welcome to the ML Application Engineer take home assignment.

Your task is to build a low-latency process that will process data, run the endpoints within the `app.py` file in a local application server, send it to ML Endpoints to get predictions, send those prediction results to offers endpoint to get which offers to give to which members, and finally record the results. 

## Solution: A DAG Task Manager

### Inspiration:
I got inspired from the way Apache Airflow works! Would love to further improve this implementation to possibly allow each task to run on a distributed server where a streaming queue such as kafka runs between the dependencies

### Usage:
- To run the default configuration:  
  `python -m src.run_workflow` which will run a OfferWorkFlow instance by default
  
- To run with a custom configuration:  
  `python -m src.run_workflow --config "your config path"`
  
- To define and run your custom workflow with corresponding tasks, create a new workflow class, add it to the factory pattern, run it through the `run_workflow` file using the `--workflow` argument.
(E.g, `python -m src.run_workflow --workflow NewWorkFlow --config "your config path"`)

### How It Works:
1. **Task Definition & Dependencies**:  
   Define your tasks and their dependencies using an easy-to-use interface.
   
2. **Task Execution**:  
   Tasks are executed in the order defined, with independent tasks running in parallel.

3. **Threaded Execution**:  
   Each task runs in its own thread.

4. **Task Types**:
   - Tasks can be either **CPU-heavy** or **I/O-heavy**.
   - For **Network I/O-heavy tasks**, Asyncio event loops are used for concurrency to avoid the overhead of additional threads.

5. **Chunking Large Files** *(to be implemented)*:  
   Large files can be chunked by columns and saved into different partitions. These partitions can be processed on different processes or servers. For example, we could chunk a CSV file by a hash of `memberId`, ensuring rows with the same `memberId` are grouped together. Alternatively, a solution using Spark can be considered.

### Pros:
- Fully **Customizable**.
- Independent tasks run in **parallel threads**.

### Cons:
- **Dependent tasks** run sequentially and cannot stream or utilize intermediate outputs.

### Areas for Improvement:
- **Streaming between dependent tasks** rather than waiting for one task to complete before starting the next.
- **Error handling** is currently limited and needs enhancement.
- **Testing** requires further development.
- **More Metrics** can be further added

### Note
In my OfferWorkFlow workflow, I intentionnally seperated the ATS, RESP, and OFFER tasks to demonstrate the DAG. The workflow would run faster if I combined them into one task


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
