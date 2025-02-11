from dataclasses import dataclass

@dataclass
class Config:
    name: str
    description: str

@dataclass
class CSVConfig(Config):
    csv_path: str

@dataclass
class OfferWorkFlowConfig(CSVConfig):
    ats_url: str
    resp_url: str     
    offer_url: str     
