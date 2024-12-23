import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt


@st.cache_data
def fetch_commodity_data(api_key):
    url = f'https://api.tradingeconomics.com/markets/index?c={api_key}'
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        cleaned_data = [item for item in data if 'Ticker' in item and ':' in item.get('Symbol', '')]
        
        df = pd.DataFrame(cleaned_data)
        
        percent_columns = [
            'DailyPercentualChange',
            'WeeklyPercentualChange',
            'MonthlyPercentualChange',
            'YearlyPercentualChange',
            'YTDPercentualChange'
        ]
        
        for col in percent_columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        
        return df
    except requests.exceptions.HTTPError as http_err:
        st.error(f"HTTP error occurred: {http_err}")
    except Exception as err:
        st.error(f"Other error occurred: {err}")
    return None


st.sidebar.title("Trading Economics Dashboard")
API_KEY = st.sidebar.text_input("Enter your API Key", type="password")

if not API_KEY:
    st.sidebar.warning("Please enter your API Key to proceed.")
    st.stop()

with st.spinner('Fetching data...'):
    df = fetch_commodity_data(API_KEY)

if df is not None and not df.empty:
    st.title("Currency Market Indices")
    
    st.subheader("Data Overview")
    st.dataframe(df)
    
    st.subheader("Select Percentage Change to Compare Across Currencies")
    change_type = st.selectbox(
        "Choose Percentage Change Type",
        [
            'Daily Percentual Change',
            'Weekly Percentual Change',
            'Monthly Percentual Change',
            'Yearly Percentual Change',
            'YTD Percentual Change'
        ]
    )
    change_column_map = {
        'Daily Percentual Change': 'DailyPercentualChange',
        'Weekly Percentual Change': 'WeeklyPercentualChange',
        'Monthly Percentual Change': 'MonthlyPercentualChange',
        'Yearly Percentual Change': 'YearlyPercentualChange',
        'YTD Percentual Change': 'YTDPercentualChange'
    }
    
    selected_column = change_column_map.get(change_type)
    
    if selected_column:
        plot_df = df.dropna(subset=[selected_column])
        
        plot_df = plot_df.sort_values(by=selected_column, ascending=False)
        
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.barh(plot_df['Ticker'], plot_df[selected_column], color='skyblue')
        ax.set_xlabel('Percentage Change (%)')
        ax.set_title(f'{change_type} Across Currencies')
        ax.invert_yaxis()  #highest value on top
        
        #labels for bars
        for i, v in enumerate(plot_df[selected_column]):
            ax.text(v + 0.01, i, f"{v:.2f}%", va='center')
        
        st.pyplot(fig)
    
    st.subheader("Additional Metrics")
    metrics_columns = [
        'Symbol', 'Name', 'Country', 'Last', 'Close',
        'DailyChange', 'WeeklyChange', 'MonthlyChange',
        'YearlyChange', 'YTDChange'
    ]
    
    metrics_df = df[metrics_columns].copy()
    metrics_df.rename(columns={
        'Symbol': 'Symbol',
        'Name': 'Name',
        'Country': 'Country',
        'Last': 'Last Price',
        'Close': 'Close Price',
        'DailyChange': 'Daily Change',
        'WeeklyChange': 'Weekly Change',
        'MonthlyChange': 'Monthly Change',
        'YearlyChange': 'Yearly Change',
        'YTDChange': 'YTD Change'
    }, inplace=True)
    st.dataframe(metrics_df)
    
else:
    st.error("No data available. Please check your API Key and try again.")
