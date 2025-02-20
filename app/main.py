from datetime import datetime, timedelta
import streamlit as st
from streamlit.components.v1 import html
import pandas as pd
from tabulate import tabulate
from core.utilities import make_report_query, dropdown_menus, refine_issues, get_korean_weekday
from core.data import request_data_from_api, load_data
from core.presentation import make_presentation
import numpy as np
import logging

logging.basicConfig(level=logging.INFO)


# Configure the main page
st.set_page_config(
    page_title="보고서 생성기",
    page_icon="📊",
    layout="wide",
)

# Set title
st.title("📒 보고서 생성기")

st.write(
    "1. 사이드바에서 시스템과 레포트를 선택합니다."
)


selected_system, selected_report = dropdown_menus(
    system_label="시스템 선택",
    system_options=["EUXP", "NCMS"],
    report_label="레포트 선택",
    report_options=["Weekly", "Monthly"],
    default_system="EUXP",
    default_report="Weekly",
)

st.sidebar.markdown(f"[이슈 생성하기]({st.secrets['jira_url']}/secure/CreateIssue!default.jspa)")

if selected_report == "Monthly":
    st.markdown("'<span style='color:red'>월간 일일점검 체크리스트</span>' 일감은 생성하셨나요?", unsafe_allow_html=True)


if st.button("보고서 생성"):
    jql = make_report_query(selected_system, selected_report)

    # Print jql to the terminal
    logging.info(f"JQL: {jql}")

    # Print jql to the browser console
    # st.write(f"<script>console.log('JQL: {jql}');</script>", unsafe_allow_html=True)
    html_code = f"""
    <script>
        console.log("SYSTEM: {selected_system}");
        console.log("REPORT: {selected_report}");
        console.log({jql!r});
    </script>
    """
    html(html_code)
    # st.javascript(f"console.log('JQL: {jql}');")

    mode = st.secrets["mode"]
    if mode == "test":
        test_data = st.secrets["test_data"]
        logging.info(f"Loading test data...{test_data}")
        issues = load_data(f"data/{test_data}")
    else:
        issues = request_data_from_api(
            st.secrets["jira_url"] + "/rest/api/2/search",
            st.secrets["jira_token"],
            jql,
            selected_system
        )

    issues = refine_issues(issues, selected_system, selected_report)


    excel_columns = issues.filter(regex='이슈|비고|상태|M/D|담당자')
    excel_columns = excel_columns.reindex(columns=['이슈', '비고', '상태', 'M/D', '담당자'])

    # 엑셀에 복사하는 양식
    st.subheader("엑셀에 복사하는 양식")
    st.write("아래 양식을 복사하여 엑셀에 붙여넣기 하세요.")
    st.dataframe(excel_columns.reset_index(drop=True), hide_index = True)

    info_columns = issues.reindex(columns=['이슈','레이블', '일자', '내용', '상태', '링크'])
    st.dataframe(
        info_columns.reset_index(drop=True), 
        hide_index = True,
        column_config={'링크': st.column_config.LinkColumn(

        )}
    )


    # 레이블 카운트
    label_counts = issues['레이블'].value_counts().reset_index()
    # label_counts = label_counts.sort_values(ascending=False)
    label_counts.columns = ['레이블', '전체']
    
    # 레이블 + 상태로 카운트
    label_status_counts = issues.pivot_table(index='레이블', columns='상태', aggfunc='size', fill_value=0).reset_index()

    # 레이블 카운트와 태그 + 진행여부 카운트 병합
    label_counts = label_counts.merge(label_status_counts, on='레이블', how='left')


    st.subheader("파워포인트에 복사하는 양식")
    st.write("아래 양식을 복사하여 파워포인트에 붙여넣기 하세요.")
    # 레이블 카운트 출력
    st.write("1. 운영 업무 현황:")
    # st.table(label_counts)
    st.dataframe(label_counts.reset_index(drop=True), hide_index = True)

    st.write("2. 사전 검증(BMT) 현황:")
    bmt_issues = issues[issues['BMT'] == True]    
    bmt_issues = bmt_issues[['시스템', '일자', '차일드']]
    bmt_issues = bmt_issues.rename(columns={'시스템': '구분', '차일드': '설명'})
    bmt_issues['설명'] = bmt_issues['설명'].apply(lambda x: '\n'.join(x))

    st.dataframe(bmt_issues.reset_index(drop=True), hide_index=True)

    st.write("3. 변경 관리 현황: 상용 배포")
    pm_issues = issues[issues['PM'] == True]    
    pm_issues = pm_issues[['시스템', '일자', '차일드']]
    pm_issues = pm_issues.rename(columns={'시스템': '구분', '차일드': '설명'})
    pm_issues['설명'] = pm_issues['설명'].apply(lambda x: '\n'.join(x))

    # st.dataframe(pm_issues.reset_index(drop=True), hide_index=True)
    # st.table(pm_issues.reset_index(drop=True))
    st.markdown(tabulate(pm_issues, headers='keys', tablefmt='pipe'), unsafe_allow_html=True)



    # 태그값이 '운영개발'인 항목만 필터링
    operation_development = issues.query("레이블 == '운영개발'")
    operation_development_issues = operation_development[['이슈']]

    st.write("4. 개발 진행 상황:")
    st.dataframe(operation_development_issues.reset_index(drop=True), hide_index=True)


    ppt_buffer = make_presentation(
    )

    today = datetime.now()

    st.download_button(
        label="파워포인트 다운로드",
        data=ppt_buffer,
        file_name=f'{selected_system}-{selected_report}_{today.strftime("%Y%m%d")}.pptx',
        mime="application/vnd.openxmlformats-officedocument.presentationml.presentation",
    )

