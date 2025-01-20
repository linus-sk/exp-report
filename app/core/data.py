import pandas as pd
from typing import Union, List

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
