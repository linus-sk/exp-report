from datetime import datetime, timedelta
import streamlit as st
import pandas as pd
from core.utilities import make_report_query, dropdown_menus, make_monthly_report_query, make_weekly_report_query, get_korean_weekday, make_url_encoded
from core.data import request_data_from_api, load_data
from core.presentation import make_presentation
import numpy as np


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
    system_options=["EUXP"],
    report_label="레포트 선택",
    report_options=["Weekly", "Monthly"],
    default_system="EUXP",
    default_report="Weekly",
)


if st.button("보고서 생성"):
    jql = make_report_query(selected_system, selected_report)
    mode = st.secrets["mode"]
    if mode == "dev":
        issues = load_data("data/test_data_24_12_euxp.json")
    else:
        issues = request_data_from_api(
            st.secrets["jira_url"] + "/rest/api/2/search",
            st.secrets["jira_token"],
            jql
        )

    today = datetime.now()

    # Set baseline_day based on selected_report
    if selected_report == "Weekly":
        baseline_day = today - timedelta(days=today.weekday())  # This week's first day (Monday)
    elif selected_report == "Monthly":
        baseline_day = today.replace(day=1)  # This month's first day

    # 상태 컬럼 추가
    issues['상태'] = issues['종료일'].apply(
        lambda x: '진행중' if pd.isna(x) or x >= baseline_day else '완료'
    )

    # Convert 레이블 values
    issues['레이블'] = issues['레이블'].apply(
        lambda labels: [
            label.replace(f"{selected_system}_", "")
                .replace(f"{selected_system}", "")
            for label in labels
        ]
    )
    issues['레이블'] = issues['레이블'].apply(lambda labels: ''.join(labels))


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


    # 태그값이 '운영개발'인 항목만 필터링
    operation_development = issues.query("레이블 == '운영개발'")
    operation_development_issues = operation_development[['이슈']]

    st.write("4. 개발 진행 상황:")
    st.dataframe(operation_development_issues.reset_index(drop=True), hide_index=True)


    ppt_buffer = make_presentation(
    )

    st.download_button(
        label="파워포인트 다운로드",
        data=ppt_buffer,
        file_name=f'{selected_system}-{selected_report}_{today.strftime("%Y%m%d")}.pptx',
        mime="application/vnd.openxmlformats-officedocument.presentationml.presentation",
    )

