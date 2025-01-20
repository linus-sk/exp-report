import streamlit as st
import pandas as pd
from core.utilities import dropdown_menus
from core.presentation import run_presentation
from core.data import prepare_chart_data
from core.excel import run_excel

# Configure the main page
st.set_page_config(
    page_title="Self-Service Portal",
    page_icon="📊",
    layout="wide",
)

# Set title
st.title("Client Self-Service Portal")

subheader = st.subheader("Instructions:")

# Set text
st.write(
    "Welcome to the self-service portal! Use the dropdown menus below to select a company and year, and then click the button to generate a PowerPoint presentation."
)

file_path = "data/client_data_2023-2025.csv"

data = pd.read_csv(file_path, sep=",")

selected_company, selected_year = dropdown_menus(
    company_label="Select Company",
    company_options=data["CompanyName"].unique(),
    year_label="Select Year",
    year_options=data["Year"].unique(),
    default_company="Company 1",
    default_year=2023,
)

filtered_df = prepare_chart_data(data, selected_company, selected_year)

if st.button("Generate PowerPoint"):
    ppt_buffer = run_presentation(
        filtered_df["transaction_data"],
        filtered_df["engagement_data"],
        filtered_df["conversion_data"],
    )

    st.download_button(
        label="Download PowerPoint",
        data=ppt_buffer,
        file_name="presentation.pptx",
        mime="application/vnd.openxmlformats-officedocument.presentationml.presentation",
    )

if st.button("Generate Excel"):
    excel_buffer = run_excel(data, selected_company, selected_year)

    st.download_button(
        label="Download Excel",
        data=excel_buffer,
        file_name="filtered_data.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )

# insert image
st.image("assets/picture.jpg")
