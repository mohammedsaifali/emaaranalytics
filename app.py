import pandas as pd
import streamlit as st
from io import BytesIO
import matplotlib.pyplot as plt

@st.experimental_memo
def prepare_data(file_path, include_rate=True) -> pd.DataFrame:
    df = pd.read_excel(file_path, header=2)
    df.columns = ['DocDate', 'DocType', 'DocNo', 'PRDORDNO', 'Code', 'Item', 'Store', 
                  'Qty', 'Unit', 'Rate', 'Amount', 'CreatedDate']
    df.dropna(subset=['DocDate', 'Item', 'Qty', 'Amount'], inplace=True)
    df['Qty'] = pd.to_numeric(df['Qty'].astype(str).str.replace(",", ""), errors='coerce')
    df['Amount'] = pd.to_numeric(df['Amount'].astype(str).str.replace(",", ""), errors='coerce')
    if include_rate:
        df['Rate'] = pd.to_numeric(df['Rate'].astype(str).str.replace(",", ""), errors='coerce')
    df.dropna(subset=['Qty', 'Amount'] + (['Rate'] if include_rate else []), inplace=True)
    df['month'] = pd.DatetimeIndex(df['DocDate']).month

    # Ensure the correct columns are included in the groupby operation
    group_columns = ['month', 'Item', 'Qty', 'Amount']
    if include_rate:
        group_columns.append('Rate')
    df = df.groupby(['month', 'Item'], as_index=False)[group_columns].sum()

    return df


def to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Sheet1')
        # No explicit save call needed here
    processed_data = output.getvalue()
    return processed_data



def main():
    st.header("Emaar Analytics :bar_chart:")
    typeofreport = st.selectbox('Pick one', ['DemandTrend', 'ProductTrend'])
    uploaded_data = st.file_uploader("Drag and Drop or Click to Upload", type=".xls")

    if uploaded_data:
        df = prepare_data(uploaded_data, include_rate=True)

        # Filter for items
        unique_items = df['Item'].unique()
        selected_items = st.multiselect('Select Items', unique_items, default=unique_items)

        # Filter dataframe based on selected items
        filtered_df = df[df['Item'].isin(selected_items)]

        # Plotting
        if not filtered_df.empty:
            fig, ax = plt.subplots()
            for item in selected_items:
                item_df = filtered_df[filtered_df['Item'] == item]
                ax.plot(item_df['month'], item_df['Qty'], label=item)
            ax.set_xlabel('Month')
            ax.set_ylabel('Quantity')
            ax.set_title('Monthly Quantity of Selected Items')
            ax.legend()
            st.pyplot(fig)

        st.write(filtered_df)

        # Download button
        st.download_button(
            label="Download Excel",
            data=to_excel(filtered_df),
            file_name="report.xlsx",
            mime="application/vnd.ms-excel"
        )

if __name__ == "__main__":
    main()

