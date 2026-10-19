import pandas as pd
import yfinance as yf
import sqlite3
from utils import queries as qs

DB_PATH = "db/users_.sql"
SCHEMA_PATH = "db/schema.sql"

def get_last_available_price():
    # Download last avilable price
    try:
        df_fx = yf.download(['PLNUSD=X','PLNEUR=X'], progress=False).Close.round(6).tail(2)
        
        # handling connection issues
        if len(df_fx) == 0:
            raise Exception("No data")
        
        # data wrangling
        df_fx.rename(columns={'PLNEUR=X':'PLN_EUR','PLNUSD=X':'PLN_USD'}, inplace=True)
        df_fx.reset_index(inplace=True)
        df_fx['Weekend'] = df_fx['Date'].dt.dayofweek > 4
        df_fx.set_index('Date', inplace=True)

        # appending newly retrieved data
        qs.append_to_fx_table(df_fx)

        # clean table
        qs.clean_fx_table()

        return df_fx.tail(1)
    except Exception:
        return qs.get_last_available_price_from_db()