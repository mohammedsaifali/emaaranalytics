import functools
from pathlib import Path
import pandas as pd
import calendar
import streamlit as st
from st_aggrid import AgGrid
from st_aggrid.shared import JsCode
from st_aggrid.grid_options_builder import GridOptionsBuilder
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt
import altair as alt
from pandas.api.types import CategoricalDtype

@st.experimental_memo
def convert_df(df):
    return df.to_csv().encode('utf-8')

@st.experimental_memo
def clean_quote(file_path: str) -> pd.DataFrame:
    # Load the Excel file, skipping the first two rows and setting the third row as headers
    df = pd.read_excel(file_path, header=2)

    # Rename columns to have consistent names
    df.rename(columns={'Unnamed: 7': 'Qty', 'Unnamed: 10': 'Amount'}, inplace=True)

    # Drop rows with NaN values in essential columns
    df.dropna(subset=['DocDate', 'Item', 'Qty', 'Amount'], inplace=True)

    # Replace commas and convert 'Qty' and 'Amount' to float
    df['Qty'] = df['Qty'].replace(",", "").astype('float')
    df['Amount'] = df['Amount'].replace(",", "").astype('float')

    # Convert 'DocDate' to datetime and extract the month
    df['month'] = pd.DatetimeIndex(df['DocDate']).month

    # Group by 'month' and 'Item', and sum 'Qty' and 'Amount'
    df = df.groupby(['month', 'Item'], as_index=False)[['Qty', 'Amount']].sum()

    return df


@st.experimental_memo
def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    df = df.iloc[4:]
    df.columns = ['DocDate', 'DocType', 'DocNo', 'PRDORDNO','Code','Item','Store','Qty','Unit','Rate','Amount','CreatedDate']
    df.dropna(inplace=True)
    df['Qty'] = df['Qty'].str.replace(",", "")
    df['month'] = pd.DatetimeIndex(df['DocDate']).month
    df['Qty'] = df['Qty'].astype('float')
    df['Amount'] = df['Amount'].astype('float')
    df = df.groupby(['month', 'Item'], as_index=False)[['Qty', 'Amount']].sum()
    return df

@st.experimental_memo
def filter_data(df: pd.DataFrame, account_selections: list[str]) -> pd.DataFrame:
    df1 = df[df.Item.isin(account_selections)]
    df1 = df1.groupby(['month', 'Item'], as_index=False)['Qty'].sum()
    fig = alt.Chart(df1).mark_bar().encode(
        x='month',
        y='Qty',
        color='Item'
    )
    text = fig.mark_text(color='black').encode(text='Qty')
    st.altair_chart(fig + text, use_container_width=True)

def main() -> None:
    st.header("Emaar Analytics :bar_chart:")
    typeofreport = st.selectbox('Pick one', ['DemandTrend', 'ProductTrend'])

    with st.expander("How to Use This"):
        st.write(Path("README.md").read_text())
    st.subheader("Upload your Excel File")
    uploaded_data = st.file_uploader("Drag and Drop or Click to Upload", type=".xls", accept_multiple_files=False)

    if uploaded_data:
        st.success("Uploaded your file!")
        if typeofreport == "DemandTrend":
            df = clean_quote(uploaded_data)
        else:
            df = clean_data(uploaded_data)
        
        with st.expander("View Report"):
            st.write(df)

        st.sidebar.subheader("Filter By Item")
        accounts = list(df.Item.unique())
        account_selections = st.sidebar.multiselect("Select Items to View", options=accounts, default=accounts)
        filter_data(df, account_selections)

if __name__ == "__main__":
    st.set_page_config("Emaar Analytics", "📊", initial_sidebar_state="expanded", layout="wide")
    main()
