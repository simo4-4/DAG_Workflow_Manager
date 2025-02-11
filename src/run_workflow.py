import argparse
from src.job_config import OfferWorkFlowConfig
from src.workflow import OfferWorkFlow

def main():
    # Create argument parser
    parser = argparse.ArgumentParser(description="Workflow Manager")
    
    # Change arg1 to an optional argument
    parser.add_argument("--config", help="Workflow JSON Config Path", type=str, default="task_workflow_config.json")
    
    # Parse the arguments
    args = parser.parse_args()
    
    # Load the config from the provided JSON file or default
    config = OfferWorkFlowConfig.from_json_file(args.config)
    
    # Set up and start the workflow
    workflow = OfferWorkFlow(config)
    workflow.setup()
    workflow.start()

if __name__ == "__main__":
    main()
