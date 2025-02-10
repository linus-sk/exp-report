import numpy as np
import pandas as pd
from typing import Union, List
import requests
from datetime import datetime
import os
import streamlit as st
from core.utilities import get_korean_weekday
import json

def filter_data(
    data: pd.DataFrame, company_name: str, year: str
) -> pd.DataFrame:
    """
    Filters data based on the company name and a date range.

    Parameters:
    - data: A Pandas DataFrame containing the data to filter.
    - company_name: The name of the company to filter by.
    - year: Either "All" to select all dates or a list of specific dates to filter by.

    Returns:
    - A filtered Pandas DataFrame.
    """
    return data[
        (data["CompanyName"] == company_name)
        & (data["Year"] == year)
    ]

def prepare_chart_data(data: pd.DataFrame, company_name: str, year:str) -> dict:

    filtered_df = filter_data(data, company_name, year)

    filtered_df = filtered_df.sort_values(by="TransactionDate")

    transaction_data = data = filtered_df.groupby(
        ["ClientID", "CompanyName", "ServiceUsed"]
    )["TransactionAmount"].sum().reset_index()

    engagement_data, conversion_data = filtered_df.drop(
        columns=["ConversionRate"]
    ), filtered_df.drop(columns=["EngagementRate"])
  

    return {
        "transaction_data": transaction_data,
        "engagement_data": engagement_data,
        "conversion_data": conversion_data,
    }


def request_data_from_api(
    api_url: str, api_key: str, jql: str, selected_system: str
) -> Union[pd.DataFrame, None]:
    """
    Requests data from an API.

    Parameters:
    - api_url: The URL of the API.
    - api_key: The API key to use for authentication.
    - company_name: The name of the company to filter by.
    - year: Either "All" to select all dates or a list of specific dates to filter by.

    Returns:
    - A Pandas DataFrame containing the data if the request is successful, otherwise None.
    """
    # Make a request to the API
    response = requests.get(
        api_url,
        headers={
            "Authorization": f"Bearer {api_key}", 
            "Content-Type": "application/json", 
            "Accept": "application/json"
        },
        params={"jql": jql}
    )

    # Check if the request was successful
    if response.status_code == 200:
        # Parse the response as JSON
        data = response.json()

        if st.secrets['save_data']:
            # Save the JSON data to a file
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            file_path = os.path.join("data", f"{selected_system}_{timestamp}.json")
            with open(file_path, 'w') as file:
                json.dump(data, file, ensure_ascii=False, indent=4)

        return extract_issues(data)

    # Return None if the request was unsuccessful
    return None

def load_data(file_path: str) -> pd.DataFrame:
    """
    Loads data from a file.

    Parameters:
    - file_path: The path to the file to load.

    Returns:
    - A DataFrame containing the loaded data.
    """
    with open(file_path, 'r') as file:
        data = pd.read_json(file)
    
    return extract_issues(data)


def extract_issues(data: dict) -> pd.DataFrame:
    """
    Extracts issues from the given data and returns a DataFrame.

    Parameters:
    - data: The data containing issues.

    Returns:
    - A DataFrame containing the extracted issues.
    """
    issues = data.get('issues', [])

    # Extract specific fields
    extracted_data = []
    for issue in issues:
        # Extract inward issue links
        child_issues = []
        for link in issue.get('fields', {}).get('issuelinks', []):
            if 'inwardIssue' in link:
                child_issues.append(f"{link['inwardIssue']['key']} {link['inwardIssue']['fields']['summary']}")
            if 'outwardIssue' in link:
                child_issues.append(f"{link['outwardIssue']['key']} {link['outwardIssue']['fields']['summary']}")

        extracted_data.append({
            '이슈키': issue.get('key'),
            '요약': issue.get('fields', {}).get('summary'),
            '종료일': issue.get('fields', {}).get('customfield_10135'),
            '시작일': issue.get('fields', {}).get('customfield_10134'),
            '레이블': issue.get('fields', {}).get('labels'),
            '차일드': child_issues,
            '비고': None,
            '담당자': None,
        })
    
    issues_df = pd.DataFrame(extracted_data)
    issues_df['이슈'] = issues_df['이슈키'] + ' ' + issues_df['요약']
    issues_df['시작일'] = pd.to_datetime(issues_df['시작일'], errors='coerce')
    issues_df['종료일'] = pd.to_datetime(issues_df['종료일'], errors='coerce')

    issues_df['M/D'] = issues_df.apply(
        lambda row: np.busday_count(row['시작일'].date(), row['종료일'].date()) if pd.notna(row['시작일']) and pd.notna(row['종료일']) else None, axis=1
    )

    # M/D 값에 1을 추가 (None이 아닌 경우에만)
    issues_df['M/D'] = issues_df['M/D'].apply(lambda x: x + 1 if x is not None else None)


    issues_df['링크'] = issues_df['이슈키'].apply(
        lambda x: f"{st.secrets['jira_url']}/browse/{x}"
    )

    return issues_df


