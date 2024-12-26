import gspread
from oauth2client.service_account import ServiceAccountCredentials
from google.oauth2.service_account import Credentials

import os, json, base64

def auth_sheet():
    # scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]


    encoded_creds = os.getenv('GOOGLE_CREDENTIALS')
    # encoded_creds = "ewogICJ0eXBlIjogInNlcnZpY2VfYWNjb3VudCIsCiAgInByb2plY3RfaWQiOiAic3RvcmllZC1wcm9ncmFtLTQ0NDAxMi10NSIsCiAgInByaXZhdGVfa2V5X2lkIjogImMzY2E3NDEzM2U2YWQ2NTA1M2UyNDFlNTNhNjIxMzAxNWFiY2Q5MDgiLAogICJwcml2YXRlX2tleSI6ICItLS0tLUJFR0lOIFBSSVZBVEUgS0VZLS0tLS1cbk1JSUV2Z0lCQURBTkJna3Foa2lHOXcwQkFRRUZBQVNDQktnd2dnU2tBZ0VBQW9JQkFRQ2NGKzNYSmJRcEVONUdcbjYzbWpySGttVWlpRHd5M0NSV0hUUzNmV0VZVU04UTN4UWhFUzd2czdUL25yelVXYnBsbEdpMmpJcW56c1MzVTJcbnVGV2ZkaENJd3J2dDArS3ZvYnh2TnFvQlZGY21NaEY4OUtmODdWVXcvdnBtUlkvYnNWc0VQeUlMKzZvd05XYmNcbitVVnpLenlFTjl5QnhLSUxXQUVRdFRGRW1vY0lTMDEvNm1UZm5vZmFMSmVETmt1T01NQXpGekg0c2hzcGhFWFdcbm9LbGZKdWFkaWpPODA2QmRaTWdDWFhYNytFRTNqUFZHblRuU0xXWVJwdlArTENIYXF1UUlSVFV0TmZ2NlJJRU9cbk45WjFVTzFabVlRbXN0U1VSdm9BNlg1QlVaSnQ4OSt1N3VlbG1lc0tpZklnR21tYWRNZDY5S2dMRmk1NzRueWlcbnNLRmRqck8vQWdNQkFBRUNnZ0VBRmNwdFpKU1o0d1c4MGcrN2FuTUFjcTRUZzlseWdPVm9zN09jWmlFSi92V0RcbjZjTThXUFZOMDBqbDdkbzVObkp4a2h5U0l6bFJ1VGNMaFBrVTB1OExmZHdabWlqelEydUR2ODdVeXR5NFVkZTVcbmcwVXdVbW5iYzd5VXZrUkZ3Zml2YVJkYkxHc1VwaWcrVk9qam5pRlNFRzh2OUZtNytYTnVxcU53M2svb08rcjNcbmNQNGZuaDNRZk9WeDY0MDhQTVZ4dnVDK1NEb2RjMUFCeXZNenNlVXl0MkRrcHRXajlnMmhaRHhMdmp5VFVjUldcbm9yekNza1paMFFucC9GQWlObCttMmFOVCtQQllYQ0xOOHBFeUxBYjZFMmVZenpKNmlMY1NIbm5qQTh5N0JOcG9cbjcxcXZ2bE1ISDltbXJRS0lSdmc0Y3RVeW5OMVVqVFNFZ2R6RndTSGhnUUtCZ1FETkNNK2U0QUd2U3lxQ3MxT3RcbmpMQnNaektDb1VKc1oxSGVaWkw4ZUlWM2RTaFRnUHBDRlg2SEorL3lwYllMTEhUVkNLcFB1L0VZMWJ3NWxsQ1hcbnJKd3BIeWcwV1JIZXdmVTRiTDVvSG5lL1VpTnZxZnc2eTRhWFV4YUsxS2VuWE0yQU5HUmJ1Tk5zNXl6Y0htSHJcblpMTGJJeXJmYm9iL3NVd3JKbG9sY2xDZ1FRS0JnUURDNU0yVmptcW9vb3AzZ0hoZzVRMmxXa2FrZzM3YmhEdlVcbnJuRy9BSVFtRlN1UVJXa1YzOFBMeUp6TlJyK0YrZDROdm9vVnJqcGxlNXdTZ3h1aFJ6ZG9sUERjSENDNFZaTE1cbnpiVm02d0V3cGhGZXBLSm40MmFTQ1M2M0tXZHdvZ1pJMGd5TFpKam1GM3BXN3I1Y2JESHJsZ0FWS3BmdDQxSVVcbmlER3I2TXBUL3dLQmdRQysweHVBNzFWQ0U0QWVJczZYY0tCbVUrbWp3SGcwc2poMDl5NUZBZHFlSXBFRW5yN01cbk1Ic1JTVzg5ODFLcHRaZUxDa1NRYndmbUtFN0ZmZ3ZHRG1WTXRHM1R3cTRxRjNTbUxqZE1ha2JpN295Q2liOXhcbjdTaDN3R0h6bGhYdll5VHoxRTh2T3FhejdiaEhxWk5TNU9hOW8wNXNvczdNUFBQNkdQaS9iMVJ3d1FLQmdIR0FcblBMWkhuWmdlS1JQVmJzWEhQNzQzcUFKeFRqVGJldGl1eXpHWVJGM0ZZSHlCMytSTVQ4UGpUbVpDT0pIMjVib05cbmFHK2Q2d1psQ1l6Q2JCbnQxcmdDWFk5aWxpK2tMbjAxbzlxUExEOC94OGZkaTNPRFBKMzUyUW4wZy9oVmMrRitcbjZxMVhaYkJDcGczd3RrNHUrSmVoNE9SeXpNNU8zK056T2JKTFBXSFRBb0dCQUwyMkErcDNKclhLbm8vOVBNZHhcbkJCd0F3a25WS08rak9ndDRzbk9aWjdmckdYSlJYOGM2eGR4UlpFalIxUzBLQU5Hbm9GaTI1NjY0YkQ4YjZjUTVcbkhqekJsMTFpK2JYRTB5d09UMHpSZFlBNDVOS3RyUTJ3N1JaL1dZSWUyM0dIVVZXeHlhTkpkUWxTUWUrU1QyNk1cbkhYWlE0L0s4a3h0TklHUnpDRU5tQzJZeFxuLS0tLS1FTkQgUFJJVkFURSBLRVktLS0tLVxuIiwKICAiY2xpZW50X2VtYWlsIjogImZvcm0xLXNoZWV0QHN0b3JpZWQtcHJvZ3JhbS00NDQwMTItdDUuaWFtLmdzZXJ2aWNlYWNjb3VudC5jb20iLAogICJjbGllbnRfaWQiOiAiMTA2ODU0MjMxMTYyMjU4Njc2MDk3IiwKICAiYXV0aF91cmkiOiAiaHR0cHM6Ly9hY2NvdW50cy5nb29nbGUuY29tL28vb2F1dGgyL2F1dGgiLAogICJ0b2tlbl91cmkiOiAiaHR0cHM6Ly9vYXV0aDIuZ29vZ2xlYXBpcy5jb20vdG9rZW4iLAogICJhdXRoX3Byb3ZpZGVyX3g1MDlfY2VydF91cmwiOiAiaHR0cHM6Ly93d3cuZ29vZ2xlYXBpcy5jb20vb2F1dGgyL3YxL2NlcnRzIiwKICAiY2xpZW50X3g1MDlfY2VydF91cmwiOiAiaHR0cHM6Ly93d3cuZ29vZ2xlYXBpcy5jb20vcm9ib3QvdjEvbWV0YWRhdGEveDUwOS9mb3JtMS1zaGVldCU0MHN0b3JpZWQtcHJvZ3JhbS00NDQwMTItdDUuaWFtLmdzZXJ2aWNlYWNjb3VudC5jb20iLAogICJ1bml2ZXJzZV9kb21haW4iOiAiZ29vZ2xlYXBpcy5jb20iCn0K"
    if encoded_creds is None:
        raise ValueError("GOOGLE_CREDENTIALS environment variable is not set.")

    # Decode the credentials
    decoded_creds = base64.b64decode(encoded_creds).decode('utf-8')

    # Load the credentials into a dictionary
    creds_dict = json.loads(decoded_creds)
    # creds = Credentials.from_service_account_info(creds_dict)
    creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)

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
    return sheet

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
        emails = "\n".join([email.get("email", "N/A") for email in employeeContactInfo.get("emails", [])])
        # emails = employeeContactInfo.get("emails")
        # emails_status = employeeContactInfo.get("")
        emails_status = "\n".join([email.get("status", "N/A") for email in employeeContactInfo.get("emails", [])])
        # phones = employeeContactInfo.get("phones")
        phones = "\n".join([phone.get("number", "N/A") for phone in employeeContactInfo.get("phones", [])])

        try:
            data = [
                [job_subject, company_url, company_name, linkedin_url, headline, country, first_name, last_name, full_name, \
                 type, emails, emails_status, phones]
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
