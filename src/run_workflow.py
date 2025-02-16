import argparse
import logging
from .workflow_management import WorkFlowFactory

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def main():
    try:
        parser = argparse.ArgumentParser(description="Workflow Manager")
        parser.add_argument("--workflow", help="Workflow type", type=str, default="OfferWorkFlow")
        parser.add_argument("--config", help="Workflow JSON Config Path", type=str, default="default_workflow_config.json")
        args = parser.parse_args()
        
        workflow = WorkFlowFactory.create_workflow(args.workflow, args.config)
        workflow.start()
    except Exception as e:
        logger.error(f"Error: {e}")

if __name__ == "__main__":
    main()
