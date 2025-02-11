import argparse
import logging
from src.job_config import OfferWorkFlowConfig
from src.workflow import OfferWorkFlow

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def main():
    # Create argument parser
    parser = argparse.ArgumentParser(description="Workflow Manager")
    
    # Change arg1 to an optional argument
    parser.add_argument("--config", help="Workflow JSON Config Path", type=str, default="default_workflow_config.json")
    
    # Parse the arguments
    args = parser.parse_args()
    
    # Load the config from the provided JSON file or default
    config = OfferWorkFlowConfig.from_json_file(args.config)

    logger.info(f"Loaded config: {config}")
    
    # Set up and start the workflow
    workflow = OfferWorkFlow(config)
    workflow.setup()
    workflow.start()
    workflow.save_summary("performance_summary.json")

if __name__ == "__main__":
    main()
