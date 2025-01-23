import logging
import numpy as np
import pandas as pd
from typing import Union, List
import requests
import streamlit as st
from core.utilities import get_korean_weekday


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
    api_url: str, api_key: str, jql: str
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
        logging.info(f"Data received: {data}")

        # Convert the JSON data to a Pandas DataFrame
        return pd.DataFrame(data.get("issues", []))

    # Return None if the request was unsuccessful
    return None


def load_data(file_path: str) -> pd.DataFrame:
    """
    Loads data from a file.

    Parameters:
    - file_path: The path to the file to load.
    """

    with open(file_path, 'r') as file:
        data = pd.read_json(file)
        issues = data.get('issues', [])

        # Extract specific fields
        extracted_data = []
        for issue in issues:
            extracted_data.append({
                '이슈키': issue.get('key'),
                '요약': issue.get('fields', {}).get('summary'),
                '종료일': issue.get('fields', {}).get('customfield_10135'),
                '시작일': issue.get('fields', {}).get('customfield_10134'),
                '레이블': issue.get('fields', {}).get('labels'),
                '비고': None,   
                '담당자': None,
            })
        
        issues_df = pd.DataFrame(extracted_data)
        issues_df['이슈'] = issues_df['이슈키'] + ' ' + issues_df['요약']
        issues_df['시작일'] = pd.to_datetime(issues_df['시작일'], errors='coerce')
        issues_df['종료일'] = pd.to_datetime(issues_df['종료일'], errors='coerce')

        issues_df['M/D'] = issues_df.apply(
            lambda row: np.busday_count(row['시작일'].date(), row['종료일'].date()), axis=1
        )

        # M/D 값에 1을 추가
        issues_df['M/D'] = issues_df['M/D'] + 1

        issues_df['링크'] = issues_df['이슈키'].apply(
            lambda x: f"{st.secrets['jira_url']}/browse/{x}"
        )    

        # 시작일의 데이터를 기반으로 '일자' 컬럼 추가
        # selected_columns['일자'] = selected_columns['시작일'].dt.strftime('%m/%d (%a)')
        issues_df['일자'] = issues_df['시작일'].apply(lambda x: x.strftime('%m/%d') + f" ({get_korean_weekday(x)})")
    return issues_df
