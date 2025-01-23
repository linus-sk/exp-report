import streamlit as st
from datetime import datetime, timedelta, timezone
from dateutil.relativedelta import relativedelta
from urllib.parse import quote, quote_plus, urlencode


def dropdown_menus(
    system_label: str,
    system_options: list,
    report_label: str,
    report_options: list,
    default_system=None,
    default_report=None,
):
    """
    사이드바에 시스템과 레포트 형식을 선택하기 위한 드롭다운 메뉴를 생성합니다.

    Parameters:
    - system_label: 시스템 드롭다운 메뉴의 레이블.
    - system_options: 시스템 드롭다운 메뉴의 옵션 리스트.
    - report_label: 레포트 드롭다운 메뉴의 레이블.
    - report_options: 레포트 드롭다운 메뉴의 옵션 리스트.
    - default_system: 시스템 드롭다운 메뉴의 기본 선택값 (선택사항).
    - default_report: 레포트 드롭다운 메뉴의 기본 선택값 (선택사항).

    Returns:
    - 선택된 시스템과 레포트 형식.
    """

    # Ensure options are lists
    system_options = list(system_options)
    report_options = list(report_options)

    # Select system
    selected_system = st.sidebar.selectbox(
        system_label,
        system_options
    )

    # Select report
    selected_report = st.sidebar.selectbox(
        report_label,
        report_options)

    return selected_system, selected_report

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


def make_report_query(system, report):
    n = datetime.now()
    if report == "Weekly":
        start = n - timedelta(days=n.weekday(), weeks=1)
        end = start + timedelta(days=6)
    elif report == "Monthly":
        end = datetime(n.year, n.month, 1)
        start = end - relativedelta(months=1)
    else:
        return None
    
    gte = start.strftime('%Y-%m-%d')
    lte = end.strftime('%Y-%m-%d')
    
    txt = f"""
project = BTVO and labels in ('{system}', '{system}_운영개발', '{system}_운영지원', '{system}_상용작업', '{system}_상용작업(DB)', '{system}_상용작업(배포)', '{system}_상용작업(기타)') and (("Start Date(WBSGantt)" >= {gte} and "Start Date(WBSGantt)" < {lte} ) or ("Finish Date(WBSGantt)" >= {gte} and "Finish Date(WBSGantt)" < {lte})) order by "Start Date(WBSGantt)" ASC
    """

    return txt

def make_weekly_report_query(system: str):
    n = datetime.now()
    start = n - timedelta(days=n.weekday(), weeks=1)
    end = start + timedelta(days=6)
    
    gte = start.strftime('%Y-%m-%d')
    lte = end.strftime('%Y-%m-%d')
    
    txt = f"""
project = BTVO and labels in ('{system}', '{system}_운영개발', '{system}_운영지원', '{system}_상용작업', '{system}_상용작업(DB)', '{system}_상용작업(배포)', '{system}_상용작업(기타)') and (("Start Date(WBSGantt)" >= {gte} and "Start Date(WBSGantt)" < {lte} ) or ("Finish Date(WBSGantt)" >= {gte} and "Finish Date(WBSGantt)" < {lte})) order by "Start Date(WBSGantt)" ASC
    """

    return txt

def make_monthly_report_query(system: str):
    n = datetime.now()
    end = datetime(n.year, n.month, 1)
    start = end - relativedelta(months=1)
    
    gte = start.strftime('%Y-%m-%d')
    lte = end.strftime('%Y-%m-%d')
    
    txt = f"""
project = BTVO and labels in ('{system}', '{system}_운영개발', '{system}_운영지원', '{system}_상용작업', '{system}_상용작업(DB)', '{system}_상용작업(배포)', '{system}_상용작업(기타)') and (("Start Date(WBSGantt)" >= {gte} and "Start Date(WBSGantt)" < {lte} ) or ("Finish Date(WBSGantt)" >= {gte} and "Finish Date(WBSGantt)" < {lte})) order by "Start Date(WBSGantt)" ASC
    """

    return txt

# project = BTVO and labels in ('{system}', '{system}_운영개발', '{system}_운영지원', '{system}_상용작업', '{system}_상용작업(DB)', '{system}_상용작업(배포)', '{system}_상용작업(기타)') and (("Start Date(WBSGantt)" >= {gte} and "Start Date(WBSGantt)" < {lte} ) or ("Finish Date(WBSGantt)" >= {gte} and "Finish Date(WBSGantt)" < {lte})) order by "Start Date(WBSGantt)" ASC

# project = BTVO and 업무구분 = {system} and labels IN ('{system}_운영지원') and (("Start Date(WBSGantt)" >= {gte} and "Start Date(WBSGantt)" < {lte} ) or ("Finish Date(WBSGantt)" >= {gte} and "Finish Date(WBSGantt)" < {lte}))

# project = BTVO and 업무구분 = {system} and labels IN ('{system}_운영개발') and (("Start Date(WBSGantt)" >= {gte} and "Start Date(WBSGantt)" < {lte} ) or ("Finish Date(WBSGantt)" >= {gte} and "Finish Date(WBSGantt)" < {lte}))

# project = BTVO and 업무구분 = {system} and labels IN ('{system}_상용작업', '{system}_상용작업(DB)', '{system}_상용작업(배포)', '{system}_상용작업(기타)') and (("Start Date(WBSGantt)" >= {gte} and "Start Date(WBSGantt)" < {lte} ) or ("Finish Date(WBSGantt)" >= {gte} and "Finish Date(WBSGantt)" < {lte}))
 
# 요일을 한국어로 변환하는 함수
def get_korean_weekday(date):
    weekdays = ['월', '화', '수', '목', '금', '토', '일']
    return weekdays[date.weekday()]
