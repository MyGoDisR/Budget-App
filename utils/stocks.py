import pandas as pd
import numpy as np
import yfinance as yf
from functools import reduce
import datetime as dt

### It is importand to add how to save it into DB with Foreign Key

# This function reads all open transactions and put them into a single table with information about
# Symbol, Volume, Open price, Portfolio allocation, Market price, Currency and Gross P/L
def open_stocks_data_and_present_open_position(path_to_excel):
    df_open = pd.read_excel(path_to_excel, sheet_name=1, header=10).iloc[:-1,[1,2,3,4,5,6,7,8,15]]
    total_invested = df_open['Purchase value'].sum()
    df_open['Portoflio Allocation'] = round(df_open['Purchase value']/total_invested,3)
    df_open_positions = df_open.groupby('Symbol').agg({'Volume': 'sum','Open price':'mean','Portoflio Allocation':'sum'}).reset_index()
    df_open_positions['Market price'] = 0
    df_open_positions['Currecny'] = 'Unknown'
    for index,ticker_ in enumerate(df_open_positions['Symbol']):
        a, b = ticker_.split('.')
        print(b)
        if b=='DE':
            df_open_positions['Currecny'][index] = 'EUR'
        elif b=='US':
            df_open_positions['Currecny'][index] = 'USD'
        elif b=='PL':
            df_open_positions['Currecny'][index] = 'PLN'
        b = b.replace('PL','WA')
        ticker_ = a + '.' + b
        try:
            ticker = yf.Ticker(ticker_)
            last_price = ticker.fast_info.last_price
        except:
            last_price = np.nan
        
        df_open_positions['Market price'][index] = last_price
    df_open_positions['Gross P/L'] = (df_open_positions['Market price'] - df_open_positions['Open price']) * df_open_positions['Volume']
    df_open_positions['Portoflio Allocation'] = df_open_positions['Portoflio Allocation'].map('{:.1%}'.format)
    return df_open_positions

# This function reads all open transactions and put them into a table with single trades and combined version - Portfolio value
# Based on that user can see single trades and their performance as well as combined version, MoM, MTD, YTD and other KPIs related to portfolio performance
def open_stocks_data_portfolio(path_to_excel):
    df_open = pd.read_excel(path_to_excel, sheet_name=1, header=10).iloc[:-1,[1,2,3,4,5,6,7,8,15]]
    total_invested = df_open['Purchase value'].sum()
    df_open['Portoflio Allocation'] = round(df_open['Purchase value']/total_invested,3)
    ticker_names = []
    all_dfs = []
    todays_date = dt.datetime.now().strftime('%Y-%m-%d')
    for i in range(len(df_open)):
        trans_ = df_open.iloc[i,:]
        a, b = trans_['Symbol'].split('.')
        b = b.replace('PL','WA')
        if a == 'SPOT':
            trans_['Symbol'] = a
        else:
            trans_['Symbol'] = a + '.' + b
        ticker_names.append(trans_['Symbol'])
        trans_hist = yf.download(trans_['Symbol'], trans_['Open time'], todays_date)['Close']
        trans_hist = trans_hist * trans_['Volume']
        all_dfs.append(trans_hist)

    portfolio_df = pd.DataFrame()
    for ticker_ in list(set(ticker_names)):
        temp_df = pd.DataFrame()
        for i in all_dfs:
            if i.columns[0] == ticker_:
                #temp_df = pd.concat([temp_df, i], axis=1)
                temp_df = temp_df.add(i, fill_value=0)
        portfolio_df = pd.concat([portfolio_df, temp_df], axis=1)
    portfolio_df = portfolio_df.sort_index()

    for col in portfolio_df.columns:
        portfolio_df[col] = portfolio_df[col].ffill()

    portfolio_df['Portfolio'] = portfolio_df.sum(axis=1, numeric_only=False)
    
    return portfolio_df