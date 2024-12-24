import gspread
from oauth2client.service_account import ServiceAccountCredentials
from google.oauth2.service_account import Credentials

import os, json, base64

def auth_sheet():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

    encoded_creds = os.getenv('GOOGLE_CREDENTIALS')
    if encoded_creds is None:
        raise ValueError("GOOGLE_CREDENTIALS environment variable is not set.")

    # Decode the credentials
    decoded_creds = base64.b64decode(encoded_creds).decode('utf-8')

    # Load the credentials into a dictionary
    creds_dict = json.loads(decoded_creds)
    creds = Credentials.from_service_account_info(creds_dict)

    # creds = ServiceAccountCredentials.from_json_keyfile_name('./storied-program-444012-t5-c3ca74133e6a.json', scope)
    client = gspread.authorize(creds)
    spreadsheet = client.open("Linkedin Employee")
    return spreadsheet

def init_sheet(spreadsheet):
    try:
        sheet = spreadsheet.worksheet("Employee Results")
    except:
        sheet = spreadsheet.add_worksheet(title="Employee Results", rows="9999", cols="26")
        headers = [["Job Subject", "Company URL", "Company Name", "LinkedIn URL", "Headline", "Country", \
                    "First Name", "Last Name", "Full Name", "Type", "Contact Email", "Email Status", "Phone Number"]]
        sheet.update(values=headers, range_name='A1:M1')

def write_sheet(sheet, employeeSearchResultList, employeeContactInfoList):
    for employeeSearchResult, employeeContactInfo in zip(employeeSearchResultList, employeeContactInfoList):
        job_subject = employeeSearchResult.get("project_subject")
        company_url = employeeSearchResult.get("companyURL")
        company_name = employeeSearchResult.get("company_name")
        linkedin_url = employeeSearchResult.get("linkedinURL")
        headline = employeeSearchResult.get("headline")
        country = employeeSearchResult.get("country")
        first_name = employeeSearchResult.get("first_name")
        last_name = employeeSearchResult.get("last_name")
        full_name = employeeSearchResult.get("full_name")
        type = employeeSearchResult.get("type")
        emails = employeeContactInfo.get("emails")
        phones = employeeContactInfo.get("phones")

        try:
            data = [
                [job_subject, company_url, company_name, linkedin_url, headline, country, first_name, last_name, full_name, \
                 type, emails, phones]
            ]

            next_row = get_next_available_row(sheet)
            range_name = f'A{next_row}:M{next_row}'

            sheet.update(values=data, range_name=range_name)

            print("Employee search result data written successfully!")
        except Exception as e:
            print(f"An error occurred: {e}")

# def write_sheet_13(sheet, employeeContactInfoList):
#     for employeeContactInfo in employeeContactInfoList:
#         emails = [email.get("email", "N/A") for email in employeeContactInfo.get("emails", [])]
#         emails_status = [email.get("status", "N/A") for email in employeeContactInfo.get("emails", [])]
#         phones = [phone.get("number", "N/A") for phone in employeeContactInfo.get("phones", [])]

#         try:
#             data = [
#                 [", ".join(emails), ", ".join(emails_status), ", ".join(phones)]
#             ]

#             next_row = get_next_available_row(sheet)
#             range_name = f'K{next_row}:M{next_row}'

#             sheet.update(values=data, range_name=range_name)
#             print("Contact Info result data written successfully!")
#         except Exception as e:
#             print(f"An error occurred: {e}")
        

def get_next_available_row(sheet):
    values = sheet.col_values(1)
    return len(values) + 1
