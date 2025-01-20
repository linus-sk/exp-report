from datetime import datetime
import streamlit as st
import pandas as pd
from core.utilities import dropdown_menus, make_monthly_report_query, make_weekly_report_query, get_korean_weekday, make_url_encoded
import numpy as np



PREFIX = st.secrets["prefix"]   # EUXP

# Configure the main page
st.set_page_config(
    page_title="월간 보고서 생성기",
    page_icon="📊",
    layout="wide",
)

# Set title
st.title("📒 보고서 생성기")

st.write(
    "1. 아래 링크에서 CSV 파일(보기>CVS (모든필드))을 다운로드합니다."
)

report_type = st.selectbox("Select Report Type:", ["Weekly", "Monthly"])

if report_type == "Weekly":
    jql = make_weekly_report_query()
elif report_type == "Monthly":
    jql = make_monthly_report_query()


# jql = make_monthly_report_query()
# st.code(jql)



jql = make_url_encoded(jql)

url = st.secrets["jira_url"] + "/issues/?jql=" + jql

# st.write(make_url_encoded_link(url, 'JIRA 검색'))
# st.write("check out this [link](%s)" % url+jql)
st.markdown("[JIRA 검색](%s)" % url)

# insert image
st.image("assets/csv-download.png", width=200)


st.write(
    "2. 다운로드한 파일을 선택합니다."
)

uploaded_file = st.file_uploader(
    "Jira's CSV 파일 선택"
)

# file_path = "data/Jira.csv"
if uploaded_file is not None:
    data = pd.read_csv(uploaded_file, sep=",")

    # '이슈 키'와 '요약' 컬럼 추출
    # selected_columns = data[['이슈 키', '요약', '상태', '레이블']]
    selected_columns = data.filter(regex='Finish Date|\(Start Date|이슈 키|요약|상태|레이블')
    selected_columns = selected_columns.sort_values(by='상태', ascending=False)

    # 컬럼명 변경
    selected_columns = selected_columns.rename(columns={
        '레이블.1': '태그',
        '이슈 키': '이슈키',
    })

    selected_columns.columns = selected_columns.columns.str.replace(r'.*Start.*', '시작일', regex=True)
    selected_columns.columns = selected_columns.columns.str.replace(r'.*Finish.*', '종료일', regex=True)

    # df['전화번호_숫자만'] = df['전화번호'].str.replace('-', '')
    selected_columns['태그'] = selected_columns['태그'].str.replace('{PREFIX}_', '')
    selected_columns['이슈'] = selected_columns['이슈키'] + ' ' + selected_columns['요약']
    selected_columns['비고'] = None
    selected_columns['담당자'] = None
    

    # 날짜 형식으로 변환
    selected_columns['시작일'] = pd.to_datetime(selected_columns['시작일'])
    selected_columns['종료일'] = pd.to_datetime(selected_columns['종료일'])

    # 워크데이 계산
    # selected_columns['M/D'] = (selected_columns['종료일'] - selected_columns['시작일']).dt.days + 1
    selected_columns['M/D'] = selected_columns.apply(
        lambda row: np.busday_count(row['시작일'].date(), row['종료일'].date()), axis=1
    )

    # M/D 값에 1을 추가
    selected_columns['M/D'] = selected_columns['M/D'] + 1

    # 진행여부 컬럼 추가
    current_month_first_day = datetime(datetime.now().year, datetime.now().month, 1)
    selected_columns['진행여부'] = selected_columns['종료일'].apply(
        lambda x: '진행중' if pd.isna(x) or x >= current_month_first_day else '완료'
    )

    selected_columns['링크'] = selected_columns['이슈키'].apply(
        # lambda x: make_url_encoded_link('https://jira.skbroadband.com/browse/' + x, x)
        lambda x: f"https://jira.skbroadband.com/browse/{x}"
    )    

    # 시작일의 데이터를 기반으로 '일자' 컬럼 추가
    # selected_columns['일자'] = selected_columns['시작일'].dt.strftime('%m/%d (%a)')
    selected_columns['일자'] = selected_columns['시작일'].apply(lambda x: x.strftime('%m/%d') + f" ({get_korean_weekday(x)})")



    excel_columns = selected_columns.filter(regex='이슈|비고|상태|M/D|담당자')
    excel_columns = excel_columns.reindex(columns=['이슈', '비고', '상태', 'M/D', '담당자'])

    # 엑셀에 복사하는 양식
    st.subheader("엑셀에 복사하는 양식")
    st.write("아래 양식을 복사하여 엑셀에 붙여넣기 하세요.")
    st.dataframe(excel_columns.reset_index(drop=True), hide_index = True)


        
    # st.table(selected_columns.reset_index(drop=True))
    info_columns = selected_columns.filter(regex='이슈키|요약|진행여부|링크|일자')
    info_columns = info_columns.rename(columns={
        '진행여부': '상태',
        '이슈키': '이슈',
        '요약': '내용',
    })
    info_columns = info_columns.reindex(columns=['이슈', '일자', '내용', '상태', '링크'])
    st.dataframe(
        info_columns.reset_index(drop=True), 
        hide_index = True,
        column_config={'링크': st.column_config.LinkColumn(

        )}
    )


    # 레이블 카운트
    label_counts = selected_columns['태그'].value_counts().reset_index()
    # label_counts = label_counts.sort_values(ascending=False)
    label_counts.columns = ['태그', '전체']
    
    # 태그 + 진행여부로 카운트
    # tag_status_counts = selected_columns.groupby(['태그', '진행여부']).size().reset_index(name='카운트')
    # 태그 + 진행여부로 카운트
    tag_status_counts = selected_columns.pivot_table(index='태그', columns='진행여부', aggfunc='size', fill_value=0).reset_index()

    # 레이블 카운트와 태그 + 진행여부 카운트 병합
    label_counts = label_counts.merge(tag_status_counts, on='태그', how='left')


    st.subheader("파워포인트에 복사하는 양식")
    st.write("아래 양식을 복사하여 파워포인트에 붙여넣기 하세요.")
    # 레이블 카운트 출력
    st.write("1. 운영 업무 현황:")
    # st.table(label_counts)
    st.dataframe(label_counts.reset_index(drop=True), hide_index = True)


    # 태그값이 '운영개발'인 항목만 필터링
    operation_development = selected_columns.query("태그 == '운영개발'")
    operation_development_issues = operation_development[['이슈']]

    st.write("4. 개발 진행 상황:")
    st.dataframe(operation_development_issues.reset_index(drop=True), hide_index=True)
    

