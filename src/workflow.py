from abc import ABC, abstractmethod
from functools import partial
import json
import logging
from src.dag_task_manager import DAGTaskManager
from src.config import Config, OfferWorkFlowConfig

from src.offer_workflow_functions import combiner_task, extract_task, load_task, transform_task
from src.prediction_ep import Prediction
from src.task import RequestTask, SyncTask, Task

logging.basicConfig()
logger = logging.getLogger()
logger.setLevel(logging.INFO)

class IWorkFlow(ABC):
    @abstractmethod
    def add_task(self, task: Task):
        raise NotImplementedError("add_task() must be implemented")   

    @abstractmethod
    def start(self):
        raise NotImplementedError("start() must be implemented")
    
class IPreloadedWorkFlow(IWorkFlow):
    @abstractmethod 
    def preload(self):
        raise NotImplementedError("preload() must be implemented")
    
class BasicWorkFlow(IWorkFlow):
    def __init__(self, config:Config):
        self.config = config
        self.task_manager = DAGTaskManager()

    def add_task(self, task: Task) -> None:
        self.task_manager.add_task(task)
        
    def start(self):
        self.task_manager.execute()
        logger.info(f"Workflow {self.config.name} completed successfully")

class PreloadedWorkFlow(BasicWorkFlow, IPreloadedWorkFlow):
    def __init__(self, config: Config):
        super().__init__(config)
        self.preloaded = False
            
    def start(self) -> None:
        if not self.preloaded:
            self.preload()
            self.preloaded = True
        self.task_manager.execute()
        logger.info(f"Workflow {self.config.name} completed successfully")

class OfferWorkFlow(PreloadedWorkFlow):
    def __init__(self, config: OfferWorkFlowConfig):
        super().__init__(config)

    def preload(self):
        self.add_task(SyncTask("Extract", partial(extract_task, file_path=self.config.csv_path)))
        self.add_task(SyncTask("Transform", transform_task, dependencies=["Extract"]))
        self.add_task(RequestTask("ATS Predict", self.config.ats_url, dependencies=["Transform"]))
        self.add_task(RequestTask("RESP Predict", self.config.resp_url, dependencies=["Transform"]))
        self.add_task(SyncTask("ATS-RESP Combiner", partial(combiner_task, output_format=Prediction), dependencies=["ATS Predict", "RESP Predict"]))
        self.add_task(RequestTask("Offer Recommendation", self.config.offer_url, dependencies=["ATS-RESP Combiner"]))
        self.add_task(SyncTask("Load", partial(load_task, output_file=self.config.result_output_path), dependencies=["Transform", "ATS Predict", "RESP Predict","Offer Recommendation"]))
    
    def save_summary(self) -> None:
        workflow_information = {
            "name": self.config.name,
            "description": self.config.description,
        }

        workflow_information.update(self.task_manager.get_summary())

        with open(self.config.performance_output_path, "w") as f:
            json.dump(workflow_information, f, indent=4)
        
        logger.info(f"Workflow {self.config.name} saved a summary successfully")

    def start(self) -> None:
        super().start()
        self.save_summary()
