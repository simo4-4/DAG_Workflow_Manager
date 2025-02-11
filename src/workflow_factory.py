from src.job_config import OfferWorkFlowConfig
from src.workflow import OfferWorkFlow, WorkFlow
import logging

logger = logging.getLogger(__name__)

class WorkFlowFactory:
    @staticmethod
    def create_workflow(workflow_type: str, config_path) -> WorkFlow:
        if workflow_type == "OfferWorkFlow":
            config = OfferWorkFlowConfig.from_json_file(config_path)
            logger.info(f"Loaded config: {config}")
            return OfferWorkFlow(config)
        else:
            raise ValueError("Unknown workflow type")
