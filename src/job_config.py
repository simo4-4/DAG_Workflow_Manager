from dataclasses import dataclass
import json

@dataclass
class Config:
    name: str
    description: str

@dataclass
class CSVConfig(Config):
    csv_path: str

@dataclass
class OutputConfig(Config):
    output_path: str

@dataclass
class OfferWorkFlowConfig(CSVConfig, OutputConfig):
    ats_url: str
    resp_url: str     
    offer_url: str     

    @classmethod
    def from_json_file(cls, file_path: str):
        # Open and read the JSON file
        with open(file_path, 'r') as f:
            data = json.load(f)  # Parse JSON content
        
        # Return a new OfferWorkFlowConfig instance
        return cls(
            name=data.get("name"),
            description=data.get("description"),
            csv_path=data.get("csv_path"),
            ats_url=data.get("ats_url"),
            resp_url=data.get("resp_url"),
            offer_url=data.get("offer_url"),
            output_path=data.get("output_path")
        )
