# ML Application Engineer Take Home Exam
Welcome to the ML Application Engineer take home assignment.

Your task is to build a low-latency process that will process data, run the endpoints within the `app.py` file in a local application server, send it to ML Endpoints to get predictions, send those prediction results to offers endpoint to get which offers to give to which members, and finally record the results. 

# Solution
A DAG Task Manager

Pros:
- Fully Customizable

To Improve:
- Streaming between tasks rather than wait for a task to be fully done
- Error Handling is limited
- Testing


## Setup
You can install the necessary packages by running the `pip install -rrequirements.txt` command.

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
