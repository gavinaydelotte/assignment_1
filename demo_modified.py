from datetime import date, timedelta
import pandas as pd
import plotly.express as px
import streamlit as st
import yfinance as yf

END = date.today()
START = date.today() - timedelta(days=365)

st.set_page_config(page_title="Stock Price Dashboard", page_icon=":bar_chart:", layout="wide")
st.title("Stock Analysis")

st.sidebar.title("Inputs")
ticker = st.sidebar.text_input("Enter Stock Ticker", value="AAPL")
col1, col2 = st.sidebar.columns(2)
start_date = col1.date_input("Start Date", START)
end_date = col2.date_input("End Date", END)
short_ma = st.sidebar.slider("Short Moving Average Window", min_value=1, max_value=100, value=20, step=1)
long_ma = st.sidebar.slider("Long Moving Average Window", min_value=1, max_value=200, value=50, step=1)
run_analysis = st.sidebar.button("Run Analysis")

def get_stock_data(ticker, start_date, end_date):
    try:
        data = yf.download(ticker, start=start_date, end=end_date)
    except Exception as e:
        return None, f"Error fetching data for ticker '{ticker}': {e}"
    if data.empty:
        return None, f"No data found for ticker '{ticker}' in the specified date range."
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)
    return data, f"Data for ticker '{ticker}' from {start_date} to {end_date} retrieved successfully."

if run_analysis:
    with st.spinner("Fetching data..."):
        df, msg = get_stock_data(ticker, start_date, end_date)
        if df is not None:
            st.sidebar.success(msg)
        else:
            st.sidebar.error(msg)
            st.stop()
        df["Short MA"] = df["Close"].rolling(window=short_ma).mean()
        df["Long MA"] = df["Close"].rolling(window=long_ma).mean()
        df['pct_chg'] = df['Close'].pct_change()
        tab1, tab2, tab3 = st.tabs(['Chart', 'Statistics', 'Data'])

        with tab1:
            st.subheader(f"{ticker} Price Analysis")
            col1, col2, col3 = st.columns(3)
            col1.metric("Last Price", f"${df['Close'].iloc[-1]:.2f}")
            col2.metric("Cumulative Change", f"{(df['Close'].iloc[-1] - df['Close'].iloc[0]) / df['Close'].iloc[0]:.2%}")
            col3.metric("Trading Days", f"{df['Close'].count()}")
            fig = px.line(df, x=df.index, y=["Close", "Short MA", "Long MA"], labels={"x": "Date", "value": "Price"})
            fig.update_layout(hovermode='x unified')
            st.plotly_chart(fig, use_container_width=True)

        with tab2:
            st.subheader(f"{ticker} Summary Statistics")
            col1, col2 = st.columns(2)
            with col1:
                st.write("**Daily Change Stats**")
                summary = df["pct_chg"].describe()
                st.dataframe(summary)
            with col2:
                price_stats = pd.DataFrame({
                    'Metric': ['High', 'Low', 'Mean', 'Volatility'],
                    'Values': [df['Close'].max(), df['Close'].min(), df['Close'].mean(), df['Close'].std()]
                })
                st.dataframe(price_stats)
        with tab3:
            st.subheader(f"{ticker} Raw Data")
            st.dataframe(df)
            csv = df.to_csv()
            st.download_button(label="Download Raw Data", data=csv, file_name=f"{ticker}_Raw_Data.csv", mime='text/csv')
