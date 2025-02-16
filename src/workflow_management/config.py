from abc import ABC, abstractmethod
from dataclasses import dataclass
import json

@dataclass
class Config(ABC):
    name: str
    description: str

    @abstractmethod
    def from_json_file(cls, file_path: str):
        raise NotImplementedError("from_json_file() must be implemented")

@dataclass
class CSVConfig(Config):
    csv_path: str

@dataclass
class ResultConfig(Config):
    result_output_path: str

@dataclass
class PerformanceConfig(Config):
    performance_output_path: str

@dataclass
class OfferWorkFlowConfig(CSVConfig, ResultConfig, PerformanceConfig):
    ats_url: str
    resp_url: str     
    offer_url: str     

    @classmethod
    def from_json_file(cls, file_path: str):
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        return cls(
            name=data.get("name"),
            description=data.get("description"),
            csv_path=data.get("csv_path"),
            ats_url=data.get("ats_url"),
            resp_url=data.get("resp_url"),
            offer_url=data.get("offer_url"),
            result_output_path=data.get("result_output_path"),
            performance_output_path=data.get("performance_output_path")
        )
