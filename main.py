from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Any, Optional, Dict
from fastapi.middleware.cors import CORSMiddleware
import json, sys

import requests

import utilizes as utz
from models import *
# from sheets import *
import sheets as sht

origins = [
    "http://linkedin-scraping-automation-formui.onrender.com/",
    "https://linkedin-scraping-automation-formui.onrender.com/",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.post("/test")
def test(data: FormData):
    return {"Test": data}

@app.get("/package-location")
def get_package_location():
    return {"paths": sys.path}

@app.post("/employees")
async def get_employeeInfo(data: FormData):
    mail = data.email
    subject = data.subject
    country = data.selectedCountries.lower()
    companyList = data.companyPairs

    print(mail)
    print(subject)
    print(country)

    employeeSearchResultList = await utz.fetch_employeeInfo(companyList=companyList, country=country, keyword=subject)

    spreadsheet = sht.auth_sheet()
    sheet = sht.init_sheet(spreadsheet)

    # sht.write_sheet_1(sheet, employeeSearchResultList)
    
    employeeContactInfoList = await utz.get_contactInfo(employeeSearchResultList=employeeSearchResultList)

    sht.write_sheet(sheet, employeeSearchResultList, employeeContactInfoList)

@app.post("/contactInfo")
async def get_contactInfo(employeeSearchResultList: List[EmployeeResultForm]):
    print(employeeSearchResultList)
    result = await utz.get_contactInfo(employeeSearchResultList=employeeSearchResultList)
    # print(result)