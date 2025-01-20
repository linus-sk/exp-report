import streamlit as st
from datetime import datetime, timedelta, timezone
from dateutil.relativedelta import relativedelta
from urllib.parse import quote, quote_plus, urlencode

PREFIX = st.secrets["prefix"]   # EUXP


def dropdown_menus(
    company_label: str,
    company_options: list,
    year_label: str,
    year_options: list,
    default_company=None,
    default_year=None,
):
    """
    Creates dropdown menus in the Streamlit sidebar for selecting company and year.

    Parameters:
    - company_label: A string label for the company dropdown.
    - company_options: A list of options for the company dropdown.
    - year_label: A string label for the year dropdown.
    - year_options: A list of options for the year dropdown.
    - default_company: Default selected value for the company dropdown (optional).
    - default_year: Default selected value for the year dropdown (optional).

    Returns:
    - A tuple (selected_company, selected_year) containing the selected values.
    """

    # Ensure options are lists
    company_options = list(company_options)
    year_options = list(year_options)

    # Select company
    selected_company = st.sidebar.selectbox(
        company_label,
        company_options
    )

    # Select year
    selected_year = st.sidebar.selectbox(
        year_label,
        year_options)

    return selected_company, selected_year

def insert_image(image_path: str, caption: str):
    """
    Inserts an image into the Streamlit app.

    Parameters:
    - image_path: The path to the image file.
    - caption: A caption for the image.
    """
    st.image(image_path, caption=caption)

def make_url_encoded(text: str):
    """
    URL-encodes a string.

    Parameters:
    - text: The text to encode.

    Returns:
    - The URL-encoded text.
    """
    return quote_plus(text)


def make_status_str(time):
    n = datetime.now()
    end = datetime(n.year, n.month, 1)
    if (time is None or time >= end):
        return '진행중'
    return '완료'


def make_url_encoded_link(url: str, text: str):
    """
    Creates a URL-encoded link in Markdown format.

    Parameters:
    - url: The URL to link to.
    - text: The text to display for the link.

    Returns:
    - A string containing the Markdown link.
    """
    return f"[{text}]({quote_plus(url)})"

def make_weekly_report_query():
    n = datetime.now()
    start = n - timedelta(days=n.weekday(), weeks=1)
    end = start + timedelta(days=6)
    
    gte = start.strftime('%Y-%m-%d')
    lte = end.strftime('%Y-%m-%d')
    
    txt = f"""
project = BTVO and labels in ('{PREFIX}', '{PREFIX}_운영개발', '{PREFIX}_운영지원', '{PREFIX}_상용작업', '{PREFIX}_상용작업(DB)', '{PREFIX}_상용작업(배포)', '{PREFIX}_상용작업(기타)') and (("Start Date(WBSGantt)" >= {gte} and "Start Date(WBSGantt)" < {lte} ) or ("Finish Date(WBSGantt)" >= {gte} and "Finish Date(WBSGantt)" < {lte})) order by "Start Date(WBSGantt)" ASC
    """

    return txt

def make_monthly_report_query():
    n = datetime.now()
    end = datetime(n.year, n.month, 1)
    start = end - relativedelta(months=1)
    
    gte = start.strftime('%Y-%m-%d')
    lte = end.strftime('%Y-%m-%d')
    
    txt = f"""
project = BTVO and labels in ('{PREFIX}', '{PREFIX}_운영개발', '{PREFIX}_운영지원', '{PREFIX}_상용작업', '{PREFIX}_상용작업(DB)', '{PREFIX}_상용작업(배포)', '{PREFIX}_상용작업(기타)') and (("Start Date(WBSGantt)" >= {gte} and "Start Date(WBSGantt)" < {lte} ) or ("Finish Date(WBSGantt)" >= {gte} and "Finish Date(WBSGantt)" < {lte})) order by "Start Date(WBSGantt)" ASC
    """

    return txt

# project = BTVO and labels in ('{PREFIX}', '{PREFIX}_운영개발', '{PREFIX}_운영지원', '{PREFIX}_상용작업', '{PREFIX}_상용작업(DB)', '{PREFIX}_상용작업(배포)', '{PREFIX}_상용작업(기타)') and (("Start Date(WBSGantt)" >= {gte} and "Start Date(WBSGantt)" < {lte} ) or ("Finish Date(WBSGantt)" >= {gte} and "Finish Date(WBSGantt)" < {lte})) order by "Start Date(WBSGantt)" ASC

# project = BTVO and 업무구분 = {PREFIX} and labels IN ('{PREFIX}_운영지원') and (("Start Date(WBSGantt)" >= {gte} and "Start Date(WBSGantt)" < {lte} ) or ("Finish Date(WBSGantt)" >= {gte} and "Finish Date(WBSGantt)" < {lte}))

# project = BTVO and 업무구분 = {PREFIX} and labels IN ('{PREFIX}_운영개발') and (("Start Date(WBSGantt)" >= {gte} and "Start Date(WBSGantt)" < {lte} ) or ("Finish Date(WBSGantt)" >= {gte} and "Finish Date(WBSGantt)" < {lte}))

# project = BTVO and 업무구분 = {PREFIX} and labels IN ('{PREFIX}_상용작업', '{PREFIX}_상용작업(DB)', '{PREFIX}_상용작업(배포)', '{PREFIX}_상용작업(기타)') and (("Start Date(WBSGantt)" >= {gte} and "Start Date(WBSGantt)" < {lte} ) or ("Finish Date(WBSGantt)" >= {gte} and "Finish Date(WBSGantt)" < {lte}))
 
# 요일을 한국어로 변환하는 함수
def get_korean_weekday(date):
    weekdays = ['월', '화', '수', '목', '금', '토', '일']
    return weekdays[date.weekday()]
