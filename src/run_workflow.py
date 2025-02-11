import argparse
import logging
from src.job_config import OfferWorkFlowConfig
from src.workflow import OfferWorkFlow
from src.workflow_factory import WorkFlowFactory

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def main():
    parser = argparse.ArgumentParser(description="Workflow Manager")
    parser.add_argument("--workflow", help="Workflow type", type=str, default="OfferWorkFlow")
    parser.add_argument("--config", help="Workflow JSON Config Path", type=str, default="default_workflow_config.json")
    args = parser.parse_args()
    
    workflow = WorkFlowFactory.create_workflow(args.workflow, args.config)
    workflow.setup()
    workflow.start()
    workflow.save_summary()

if __name__ == "__main__":
    main()
