import pandas as pd 
from io import BytesIO

def run_excel(data: pd.DataFrame, company_name: str, year:str) -> pd.DataFrame:
    """
    Filters data based on the company name and a date range.

    Parameters:
    - data: A Pandas DataFrame containing the data to filter.
    - company_name: The name of the company to filter by.
    - year: Either "All" to select all dates or a list of specific dates to filter by.

    Returns:
    - A filtered Pandas DataFrame.
    """
    filtered_data = data[
        (data["CompanyName"] == company_name)
        & (data["Year"] == year)
    ]
    output = BytesIO()
    filtered_data.to_excel(output, index=False, sheet_name="Filtered Data")
    output.seek(0)  

    return output