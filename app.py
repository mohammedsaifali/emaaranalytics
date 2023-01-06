import functools
from pathlib import Path
import pandas as pd
import calendar
import streamlit as st
from st_aggrid import AgGrid
from st_aggrid.shared import JsCode
from st_aggrid.grid_options_builder import GridOptionsBuilder
import pandas as pd
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt
import altair as alt
from pandas.api.types import CategoricalDtype






@st.experimental_memo
def clean_data(df: pd.DataFrame) -> pd.DataFrame:
#df = pd.read_excel('dataemi2.xls',header=None)
    df = df.iloc[4:]
    df.columns =['DocDate', 'DocType', 'DocNo', 'PRDORDNO','Code','Item','Store','Qty','Unit','Rate','Amount']
    df.dropna(inplace=True)
    #df.round(2)
    df['Qty'] = df['Qty'].str.replace(",", "")
    df['month'] = pd.DatetimeIndex(df['DocDate']).month
    df['Qty'] = df['Qty'].astype('float')
    df = df.groupby(['month','Item'], as_index=False)['Qty'].sum()
    df['month'] = df['month'].apply(lambda x: calendar.month_abbr[x])
    #new_order = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
    #df.Tm = f.Tm.cat.set_categories(new_order)
    #df.sort_values(by='month', inplace = True)
    month_order = CategoricalDtype(['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'], ordered=True)
    df['month'] = df['month'].astype(month_order)
    df.sort_values('month')

    return df


@st.experimental_memo
def filter_data(
    df: pd.DataFrame, account_selections: list[str]
) -> pd.DataFrame:
    df1 = df[df.Item.isin(account_selections)]
    df1 = df1.groupby(['month','Item'], as_index=False)['Qty'].sum()
    #df1 = df1.sort_values(by = 'month')
    #df1.round(2)
    #df1['month'] = df1['month'].apply(lambda x: calendar.month_abbr[x])
    #fig = sns.barplot(x="month", y="Qty", hue="Item", data=df1)
    fig = alt.Chart(df1).mark_bar().encode(
    x='month',
    y='Qty',
    color='Item',
    #column='Item'
    )
    text = fig.mark_text(color='black'
    ).encode(
    text='Qty')
    st.altair_chart(fig+text,use_container_width=True)

def main() -> None:
    st.header(" Emaar Analytics :bar_chart:")

    with st.expander("How to Use This"):
        st.write(Path("README.md").read_text())

    st.subheader("Upload your CSV ")
    uploaded_data = st.file_uploader(
        "Drag and Drop or Click to Upload", type=".xls", accept_multiple_files=False
    )

    if uploaded_data:
        st.success("Uploaded your file!")
        #st.info("Using example data. Upload a file above to use your own data!")
        #uploaded_data = open("example.xls", "r")
    #else:
    #st.success("Uploaded your file!")

    df = pd.read_excel(uploaded_data,header=None)
    with st.expander("Raw Dataframe"):
        st.write(df)

    df = clean_data(df)
    with st.expander("Cleaned Data"):
        st.write(df)

    st.sidebar.subheader("Filter By Item")

    accounts = list(df.Item.unique())
    account_selections = st.sidebar.multiselect(
        "Select Items to View", options=accounts, default=accounts
    )
    account_selections = list(account_selections)
    filter_data(df, account_selections)
if __name__ == "__main__":
    st.set_page_config(
        "Emaar Analytics",
        "📊",
        initial_sidebar_state="expanded",
        layout="wide",
    )
    main()
