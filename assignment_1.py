import datetime as dt

import pandas as pd
import plotly.express as px
import streamlit as st

from stock import Stock

st.title("Stock Analysis Dashboard")


@st.cache_data
def load_stock(ticker, start, end, ma_window, long_ma_window):
    return Stock(ticker, start, end, ma_window, long_ma_window)


st.sidebar.header("Settings")
ticker = st.sidebar.text_input("Ticker symbol", "AAPL")
start_date = st.sidebar.date_input("Start date", dt.date.today() - dt.timedelta(days=365))
end_date = st.sidebar.date_input("End date", dt.date.today())
ma_window = st.sidebar.slider("Short moving average window (days)", 5, 200, 20)
long_ma_window = st.sidebar.slider("Long moving average window (days)", 5, 200, 50)
fetch = st.sidebar.button("Fetch data")

tab1, tab2 = st.tabs(["Single Stock Analysis", "Portfolio Comparison"])

with tab1:
    if fetch:
        with st.spinner(f"Fetching data for {ticker.upper()}..."):
            stock = load_stock(ticker.upper(), start_date, end_date, ma_window, long_ma_window)

        if stock.data is None:
            st.error(stock.message)
        else:
            last_close = stock.data["Close"].iloc[-1]
            cum_return = stock.data["return"].sum()
            trading_days = len(stock.data)

            col1, col2, col3 = st.columns(3)
            col1.metric("Last Close", f"${last_close:.2f}")
            col2.metric("Cumulative Return", f"{cum_return:.2%}")
            col3.metric("Trading Days", trading_days)

            fig = px.line(stock.data,
                          x=stock.data.index,
                          y=["Close", "MA", "MA_long"],
                          title=f"{stock.symbol} Close Price with {ma_window}-Day and {long_ma_window}-Day Moving Averages",
                          labels={"x": "Date", "value": "Price", "variable": "Series"})
            st.plotly_chart(fig)

            st.plotly_chart(stock.plot_performance())
            st.plotly_chart(stock.plot_return_dist())

            st.subheader("Return Statistics")
            st.dataframe(stock.data["return"].describe())
    else:
        st.write("Choose your settings in the sidebar and click **Fetch data**.")

with tab2:
    tickers_text = st.text_input("Enter tickers separated by commas", "AAPL, MSFT, GOOG")

    if fetch:
        tickers = [t.strip().upper() for t in tickers_text.split(",") if t.strip() != ""]

        performance = pd.DataFrame()
        for symbol in tickers:
            with st.spinner(f"Fetching data for {symbol}..."):
                stock = load_stock(symbol, start_date, end_date, ma_window, long_ma_window)

            if stock.data is None:
                st.error(stock.message)
                continue

            cum = stock.data["return"].cumsum()
            performance[symbol] = cum - cum.iloc[0]

        if not performance.empty:
            fig = px.line(performance,
                          x=performance.index,
                          y=performance.columns,
                          title="Cumulative Performance Comparison",
                          labels={"x": "Date", "value": "Cumulative Return", "variable": "Ticker"})
            fig.update_layout(yaxis_tickformat=".1%")
            st.plotly_chart(fig)

            st.write("First-day values (should all be 0.0):")
            st.dataframe(performance.iloc[0])
    else:
        st.write("Enter tickers above, choose dates in the sidebar, and click **Fetch data**.")
