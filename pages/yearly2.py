import yfinance as yf
import streamlit as st
import numpy as np
import pandas as pd
import requests
import nltk
import statistics as stats
# from nltk.sentiment import SentimentIntensityAnalyzer
from utils.trading import trading_yfin_2


from datetime import datetime, timezone, timedelta

st.page_link(f"pages/trading_v2.py", icon="🔙",label="Go back to Trading")
ticker_ = "AAPL"
gmt_plus_2 = timezone(timedelta(hours=2))

dat = yf.Ticker(ticker_)
df = trading_yfin_2(ticker_, "2024-01-01", "2026-10-02")

df_stock_info = []
try:
    df_stock_info.append(dat.info["country"])
    df_stock_info.append(dat.info["industry"])
    df_stock_info.append(dat.info["sector"])
except KeyError:
    df_stock_info.append("N/A")
    df_stock_info.append("Crypto")
    df_stock_info.append("Crypto")

dat = yf.Search(ticker_)
all_news = dat.news

df_news = pd.DataFrame()

# nltk.download('vader_lexicon')
# sid = SentimentIntensityAnalyzer()


for i in range(len(all_news)):
    news_ = []
    news_.append(all_news[i]['title'])
    news_.append(all_news[i]['publisher'])
    news_.append(all_news[i]['link'])
    news_.append(datetime.fromtimestamp(all_news[i]['providerPublishTime'], tz=gmt_plus_2).strftime('%Y-%m-%d'))
    news_.append(all_news[i]['relatedTickers'])
    # concating news to df
    df_news = pd.concat([df_news, pd.DataFrame([news_], columns=['Title', 'Publisher', 'Link', 'Publication Date','Releated Tickets'])], ignore_index=True)

# Sidebar news
with st.sidebar:
    st.title('Latest news')

    st.metric(
        label="Overall News Sentiment",
        value='TBD',
        #value=np.mean(df_news['Sentiment']),
        #delta=stats.mode(df_news['Feedback']),
        #delta_color="red" if stats.mode(df_news['Feedback'])=='Negative' else ("green" if stats.mode(df_news['Feedback'])=='Positive' else "grey"),
        #delta_arrow='down' if stats.mode(df_news['Feedback'])=='Negative' else ("up" if stats.mode(df_news['Feedback'])=='Positive' else "off")
    )
    st.divider()

    for i in range(0,5):
        st.subheader(df_news['Title'][i])
        #st.write(f"Sentiment Score: {df_news['Sentiment'][i]} ({df_news['Feedback'][i]})")
        st.write(f"Publication Date: {df_news['Publication Date'][i]}")
        st.write(f"Related Tickets {df_news['Releated Tickets'][i]}")
        #st.html(f"Summary: {df_news['Summary'][i]}")
        st.markdown(f"[Read more]({df_news['Link'][i]})")
        st.divider()

# Last News
st.title(f'{ticker_} Details')
st.metric('',f"Current Price: {round(df['Close'][-1],2)}")

col1, col2, col3 = st.columns(3)

with col1:
    st.write(f"Country: {df_stock_info[0]}")

with col2:
    st.write(f"Industry: {df_stock_info[1]}")

with col3:
    st.write(f"Sector: {df_stock_info[2]}")

left, middle, right = st.columns(3, border=True)

left.metric("DoD:",
            round(df['Close'][-2],2),
            str(round((df['Close'][-1] - df['Close'][-2])/df['Close'][-2]*100)) + " %",
            delta_color="red" if round((df['Close'][-1] - df['Close'][-2])/df['Close'][-2]*100,2) < 0 else "green")
middle.metric("MoM:",
            round(df['Close'][-30],2),
            str(round((df['Close'][-1] - df['Close'][-30])/df['Close'][-30]*100)) + " %",
            delta_color="red" if round((df['Close'][-1] - df['Close'][-30])/df['Close'][-30]*100,2) < 0 else "green")
right.metric("YoY:",
            round(df['Close'][-365],2),
            str(round((df['Close'][-1] - df['Close'][-365])/df['Close'][-365]*100)) +  " %",
            delta_color="red" if round((df['Close'][-1] - df['Close'][-365])/df['Close'][-365]*100,2) < 0 else "green")

tab1, tab2 = st.tabs(["Close Price", "Volume"])

with tab1:
    st.line_chart(df['Close'])
with tab2:
    st.line_chart(df['Volume'])

# options
#dat.option_chain(dat.options[0]).calls
# analysis
#dat.analyst_price_targets
# get financials
#st.dataframe(dat.balance_sheet)
#dat.balance_sheet
dat = yf.Ticker(ticker_)
df = dat.quarterly_income_stmt.loc[["Total Revenue", "Gross Profit", "Operating Income", "EBITDA", "Net Income", "Diluted EPS", "Diluted Average Shares", "Cost Of Revenue", "Operating Expense"],:]#, "Interest Expense"],:]
for col in df.columns:
    col = str(col).split(" ")[0]
    df[col] = df[col].map('{:,.1f}'.format)
df = df.T

st.write('Quaterly Reportings')

st.dataframe(df, use_container_width=True)
# dates
# dat.calendar
