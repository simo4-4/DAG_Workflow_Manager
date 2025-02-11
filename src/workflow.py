from abc import ABC, abstractmethod
from functools import partial
import json
import logging
from src.dag_task_manager import DAGTaskManager
from src.job_config import OfferWorkFlowConfig

from src.offer_functions import combiner_task, extract_task, load_task, transform_task
from src.prediction_ep import Prediction
from src.task import AsyncTask, RequestTask, Task

logging.basicConfig()
logger = logging.getLogger()
logger.setLevel(logging.INFO)

class WorkFlow(ABC):
    @abstractmethod
    def start(self):
        raise NotImplementedError("start() must be implemented")

class LargeCSVWorkFlow(WorkFlow):
    # This method will partition the csv file into smaller independent chunks
    def csv_partition(self):
        pass

    #This will take each chunk and configure a task manager to process it
    def setup(self):
        pass

    #This will start the processing of each chunk in parallel either on different processes in one machine or different servers
    def start(self):
        pass

class OfferWorkFlow(WorkFlow):
    def __init__(self, config:OfferWorkFlowConfig):
        self.config = config
        self.task_manager = DAGTaskManager()

    def setup(self):
        self.task_manager.add_task(Task("Extract", partial(extract_task, file_path=self.config.csv_path)))
        self.task_manager.add_task(Task("Transform", transform_task, dependencies=["Extract"]))
        self.task_manager.add_task(RequestTask("ATS Predict", self.config.ats_url, dependencies=["Transform"]))
        self.task_manager.add_task(RequestTask("RESP Predict", self.config.resp_url, dependencies=["Transform"]))
        self.task_manager.add_task(Task("ATS-RESP Combiner", partial(combiner_task, output_format=Prediction), dependencies=["ATS Predict", "RESP Predict"]))
        self.task_manager.add_task(RequestTask("Offer Recommendation", self.config.offer_url, dependencies=["ATS-RESP Combiner"]))
        self.task_manager.add_task(Task("Load", partial(load_task, output_file=self.config.output_path), dependencies=["Transform", "ATS-RESP Combiner","Offer Recommendation"]))
    
    def start(self):
        self.task_manager.execute()
        logger.info(f"Workflow {self.config.name} completed successfully")

    def save_summary(self, output_path):
        workflow_information = {
            "name": self.config.name,
            "description": self.config.description,
        }

        workflow_information.update(self.task_manager.get_summary())
        
        with open(output_path, "w") as f:
            json.dump(workflow_information, f, indent=4)
