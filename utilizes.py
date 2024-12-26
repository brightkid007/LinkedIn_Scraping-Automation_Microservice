import asyncio
from proxycurl.asyncio import Proxycurl, do_bulk
from proxycurl.asyncio.base import ProxycurlException
import csv, re, json
import httpx
from typing import List
from models import *

proxycurl = Proxycurl(api_key="CoQVnUVE23BMtzq4-_8e_w")

async def fetch_employeeInfo(companyList: List[CompanyPair], country: str, keyword: str):
    
    employeeSearchList = await asyncio.gather(
        *(proxycurl.linkedin.company.employee_search(
            keyword_regex=keyword.replace(' ', '|'),
            linkedin_company_profile_url=company.companyURL,
            page_size='15',
            country=country,
        ) for company in companyList)
    )

    for employeeSearch, company in zip(employeeSearchList, companyList):
        employeeSearch["companyURL"] = company.companyURL
        employeeSearch["type"] = company.companyType
    
    # print(employeeSearchList)

    file_path = "employeeSearchList.json"
    with open(file_path, "w", encoding="utf-8") as json_file:
        json.dump(employeeSearchList, json_file, indent=4, ensure_ascii=False)
        print(f"Employee search list successfully saved to {file_path}")

    concurrent_process = [
        type_filter_employee(
            employeeProfileURL=employee.get("profile_url"),
            employeeSearchType=employeeSearch.get("type"),
            companyURL=employeeSearch.get("companyURL"),
            subject=keyword
        )
        for employeeSearch in employeeSearchList for employee in employeeSearch.get("employees", [])
    ]

    employeeSearchResultList = await asyncio.gather(*concurrent_process)
    employeeSearchResultList = [e for e in employeeSearchResultList if e is not None]

    print(employeeSearchResultList)

    file_path = "employeeSearchResultList.json"
    with open(file_path, "w", encoding="utf-8") as json_file:
        json.dump(employeeSearchResultList, json_file, indent=4, ensure_ascii=False)
        print(f"Final Employee search list successfully saved to {file_path}")
    # print(employeeSearchResultList)

    return employeeSearchResultList

async def type_filter_employee(employeeProfileURL: str, employeeSearchType: str, companyURL: str, subject: str):
    try:
        companyURL = normalize_url(companyURL)
        employeeProfile = await proxycurl.linkedin.person.get(linkedin_profile_url=employeeProfileURL)

        experiences = employeeProfile.get("experiences", [])
        employeeType = "current" if is_current_type(experiences=experiences, companyURL=companyURL) else "former"

        if employeeSearchType == "both" or employeeSearchType == employeeType:
            try:
                companyProfile = await proxycurl.linkedin.company.get(url=companyURL)
                if not companyProfile:
                    print(f"Company profile not found for URL: {companyURL}")
                    return None
            except ProxycurlException as e:
                print(f"Error fetching company profile for {companyURL}: {e}")
                return None
            # companyProfile = await proxycurl.linkedin.company.get(
            #     url=companyURL
            # )
            return {
                "project_subject": subject,
                "companyURL": companyURL,
                "company_name": companyProfile.get("name"),
                "linkedinURL": employeeProfileURL,
                "headline": employeeProfile.get("headline"),
                "country": employeeProfile.get("country"),
                "first_name": employeeProfile.get("first_name"),
                "last_name": employeeProfile.get("last_name"),
                "full_name": employeeProfile.get("full_name"),
                "type": employeeType
            }
        return None
    except ProxycurlException as e:
        print(f"Error fetching employee profile for {employeeProfileURL}: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error in type_filter_employee: {e}")
        return None

def is_current_type(experiences, companyURL):
    for experience in experiences:
        experience_url = normalize_url(experience.get("company_linkedin_profile_url"))
        starts_at = experience.get("starts_at")
        ends_at = experience.get("ends_at")
        
        if starts_at and starts_at.get("year"):
            is_current = (
                experience_url == companyURL
                and ends_at is None  # No end date indicates it's a current role
            )
            return is_current
    return False

def normalize_url(url):
    return re.sub(r"/$", "", url) if url else None

async def get_contactInfo(employeeSearchResultList: List[EmployeeResultForm]):
    employeeContactInfoList = await asyncio.gather(
        *(fullenrich_bulk_request(employee=employee)
        for employee in employeeSearchResultList)
    )
    print(employeeContactInfoList)
    return employeeContactInfoList

    

async def fullenrich_bulk_request(employee: EmployeeResultForm):
    bulk_url = "https://app.fullenrich.com/api/v1/contact/enrich/bulk"
    headers = {
        "Authorization": "Bearer 01ae77fa-f631-4ec5-9587-668422b39ec6",
        "Content-Type": "application/json"
    }
    payload = {
        "name": "LinkedIn Employee ContactInfo",
        # "webhook_url": "https://example.com/webhook",
        "datas": [
            {
                "firstname": employee.get("first_name", ""),
                "lastname": employee.get("last_name", ""),
                "company_name": employee.get("company_name", ""),
                "linkedin_url": employee.get("linkedinURL", ""),
                # "firstname": employee.first_name,
                # "lastname": employee.last_name,
                # "company_name": employee.company_name,
                # "linkedin_url": employee.linkedinURL,
                "enrich_fields": ["contact.emails", "contact.phones"],
            }
        ]
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(bulk_url, json=payload, headers=headers)
        # print(response.json())
        enrichment_id = response.json().get("enrichment_id")
        if not enrichment_id:
            raise ValueError("Enrichment ID not found in response")
        print(enrichment_id)

        response = await wait_for_completion(enrichment_id=enrichment_id)
        print("Here is response: ", response)
        datas = response.get("datas", [])
        print("Data: ", datas)

        for data in datas:
            contact_info = data.get("contact", {})
            emails = contact_info.get("emails", [])
            phones = contact_info.get("phones", [])
            return { 
                "emails": emails,
                "phones": phones
            }

async def wait_for_completion(enrichment_id, interval=5):
    while True:
        data = await fetch_status(enrichment_id)
        status = data.get("status")
        print(f"Current status: {status}")
        
        if status == "FINISHED":
            print("Process finished successfully: ", data)
            return data  # Return the final data
        
        if status in {"CANCELED", "CREDITS_INSUFFICIENT", "RATE_LIMIT", "UNKNOWN"}:
            raise RuntimeError(f"Process failed with status: {status}")
        
        await asyncio.sleep(interval)

async def fetch_status(enrichment_id):
    url = f"https://app.fullenrich.com/api/v1/contact/enrich/bulk/{enrichment_id}"
    headers = {"Authorization": "Bearer 01ae77fa-f631-4ec5-9587-668422b39ec6"}
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        response.raise_for_status()
        return response.json()