from pydantic import BaseModel
from typing import List, Any, Optional, Dict

class CompanyPair(BaseModel):
    companyURL: str
    companyType: str

class FormData(BaseModel):
    email: str
    subject: str
    selectedCountries: str
    companyPairs: List[CompanyPair]

class EmployeeResultForm(BaseModel):
    project_subject: str
    companyURL: str
    company_name: str
    linkedinURL: str
    headline: str
    country: str
    first_name: str
    last_name: str
    full_name: str
    type: str

class FullenrichRequestForm(BaseModel):
    firstname: str
    lastname: str
    company_name: str
    linkedin_url: str
    enrich_fields: List[str]