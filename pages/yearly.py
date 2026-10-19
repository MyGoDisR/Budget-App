  # Libraries
import streamlit as st
import pandas as pd
import altair as alt
import sys
import os
import utils.finance as finance
import utils.navigation as navigation
import utils.fx_rates as fx_rates
import requests
from datetime import date

# Security 
if "role_" not in st.session_state:
    st.switch_page("app.py")

# Language chosen
if 'lang' not in st.session_state:
    st.session_state.lang = "ENG"

# Navigation applied
# As of now users have option what to see in the navigation panel
# that is chosen at the registration form
navigation.menu()

# Getting Last Avialbale FX Rates or Download the new one form the internet
# This should be after securit is checked not to make unnecessary API calls
fx_rates_ = fx_rates.get_last_available_price()

# Dictionary with translations for the app, in order to make it multilingual
translations = {
    "title": {"ENG": "Budget Overview", "POL": "Ogólny zarys budżetu"},
    "filtered_title": {"ENG": "Filter your transactions and view insights.", "POL": "Filtruj swoje transakcje and zobacz wnioski"},
    "sel_curr": {"ENG": "Please select currency", "POL": "Wybierz walutę"},
    "sel_year": {"ENG": "Choose Year:", "POL": "Wybierz rok:"},
    "var_or_value": {"ENG": "Choose metric", "POL": "Wybierz metrykę:"},
    "var_and_value":{"ENG": ["Value", "Variance"], "POL": ["Wartość", "Zmiana"]},
    "yoy_or_ytd": {"ENG": "Choose metric", "POL": "Wybierz metrykę:"},
    "yoy_and_ytd":{"ENG": ["YoY", "YTD"], "POL": ["RoR", "RdD"]},
    "expenses": {"ENG": "Overall Spending", "POL": "Ogólne wydatki"},
    "income": {"ENG": "Overall Inflows", "POL": "Ogólne wpłaty"},
    "food_e": {"ENG": "Food Expenses", "POL": "Wydatki - Żywność"},
    "house_e": {"ENG": "House Expenses", "POL": "Wydatki - Dom"},
    "beauty_e": {"ENG": "Beauty Expenses", "POL": "Wydatki - Kosmetyki"},
    "other_e": {"ENG": "Other Expenses", "POL": "Wydatki - Inne"},
    "sel_tags": {"ENG": "Select Tags", "POL": "Wybierz rodzaj"},
    "sel_date": {"ENG": "Select Date Range", "POL": "Wybierz zakres dat"},
    "sel_trans": {"ENG": "Filtered Transactions", "POL": "Wyfiltrowane transakcje"},
    "title_1": {"ENG": "Spending Over Time", "POL": "Wydatki z czasem"},
    "title_2": {"ENG": "Monthly Spending", "POL": "Wydatki miesięczne"},
    "all_year": {"ENG" : "All", "POL":'Wszystkie'}
}

######## Data #############################################################################
if len(os.listdir(f'Data/{st.session_state.role_}/Transactions/Processed')) == 0:
    st.error('In order to see analysis please upload the data', width='stretch')
else:
    df = pd.read_csv(f'Data/{st.session_state.role_}/Transactions/Processed/final_output.csv')

    df['Date'] = pd.to_datetime(df['Date'])
    df["Day"] = df["Date"].dt.day
    df['Month'] = df['Date'].dt.month
    df['Year'] = df['Date'].dt.year
    df['No. trans'] = df['Date'].count()
    df['Year-Month'] = df['Date'].dt.strftime('%Y-%m')
 
    ########################################################################################## Title and Description
    st.title(translations["title"][st.session_state.lang])
    st.write(translations["filtered_title"][st.session_state.lang])

    curr = ["PLN", "EUR", "USD"]
    curr_selection = st.selectbox(
        translations["sel_curr"][st.session_state.lang],
        (curr),
    )

    if curr_selection =="EUR":
        df['Amount'] = df['Amount'] * fx_rates_['PLN_EUR'][0]
        currency_icon = "€"
    elif curr_selection == "USD":
        df['Amount'] = df['Amount'] * fx_rates_['PLN_USD'][0]
        currency_icon = "$"
    else:
        currency_icon = "zł"

    # min year for conditional statements
    min_year = df['Year'].min()
    max_year = df['Year'].max()

    # Variables for year selection

    years = df['Year'].drop_duplicates().tolist()
    years.append(translations["all_year"][st.session_state.lang])

    filter1, filter2, filter3 = st.columns(3)

    with filter1:
        selection = st.selectbox(translations["sel_year"][st.session_state.lang], years)

    with filter2:
        selection_var_value = st.selectbox(translations["var_or_value"][st.session_state.lang], translations["var_and_value"][st.session_state.lang])

    with filter3:
        selection_yoy_ytd = st.selectbox(translations["yoy_or_ytd"][st.session_state.lang], translations["yoy_and_ytd"][st.session_state.lang])

    # Filter the DataFrame
    if selection != translations["all_year"][st.session_state.lang]:
        # Year -1  
        df_ly = df[df['Year'] == (selection-1)].reset_index(drop=True)
        df_ly['Date'] = pd.to_datetime(df_ly['Date'], format="%d.%m.%Y")

        # Year 
        df = df[df['Year'] == selection].reset_index(drop=True)

        # Year-to-Date (YTD)
        startDate = date.today()
        endDate = date(startDate.year -1, startDate.month, startDate.day)
        df_ytd = df_ly[df_ly['Date'].dt.date <= endDate]

    # KPI's - always avialable
    KPI_list = [
        [translations["expenses"][st.session_state.lang], df[df['Tags'] != 'Inflows']['Amount'].sum()],
        [translations["income"][st.session_state.lang], df[df['Tags'] == 'Inflows']['Amount'].sum()],
        [translations["food_e"][st.session_state.lang], df[(df['Tags'] != 'Inflows') & (df['Tags'] == 'Food')]['Amount'].sum()],
        [translations["house_e"][st.session_state.lang], df[(df['Tags'] != 'Inflows') & (df['Tags'] == 'House appliencies')]['Amount'].sum()],
        [translations["beauty_e"][st.session_state.lang], df[(df['Tags'] != 'Inflows') & (df['Tags'] == 'Beauty')]['Amount'].sum()],
        [translations["other_e"][st.session_state.lang], df[(df['Tags'] != 'Inflows') & (df['Tags'] == 'Others')]['Amount'].sum()]
    ]

    # KPI's - always avialable
    KPI_list_CY = [
        df[df['Tags'] != 'Inflows']['Amount'],
        df[df['Tags'] == 'Inflows']['Amount'],
        df[df['Tags'] == 'Food']['Amount'],
        df[df['Tags'] == 'House appliencies']['Amount'],
        df[df['Tags'] == 'Beauty']['Amount'],
        df[df['Tags'] == 'Others']['Amount']
    ]



    try:
        if selection_var_value == "Value" or selection_var_value == "Wartość":
            if (selection_yoy_ytd == "YTD" or selection_yoy_ytd == "RdD") and selection == max_year:
                KPI_list_LY = [
                    round(df_ytd[df_ytd['Tags'] != 'Inflows']['Amount'].sum() - df[df['Tags'] != 'Inflows']['Amount'].sum()),
                    round(df_ytd[df_ytd['Tags'] == 'Inflows']['Amount'].sum() - df[df['Tags'] == 'Inflows']['Amount'].sum()),
                    round(df_ytd[df_ytd['Tags'] == 'Food']['Amount'].sum() - df[df['Tags'] == 'Food']['Amount'].sum()),
                    round(df_ytd[df_ytd['Tags'] == 'House appliencies']['Amount'].sum() - df[df['Tags'] == 'House appliencies']['Amount'].sum()),
                    round(df_ytd[df_ytd['Tags'] == 'Beauty']['Amount'].sum() - df[df['Tags'] == 'Beauty']['Amount'].sum()),
                    round(df_ytd[df_ytd['Tags'] == 'Others']['Amount'].sum() - df[df['Tags'] == 'Others']['Amount'].sum())
                ]
            else:
                KPI_list_LY = [
                    round(df_ly[df_ly['Tags'] != 'Inflows']['Amount'].sum() - df[df['Tags'] != 'Inflows']['Amount'].sum()),
                    round(df_ly[df_ly['Tags'] == 'Inflows']['Amount'].sum() - df[df['Tags'] == 'Inflows']['Amount'].sum()),
                    round(df_ly[df_ly['Tags'] == 'Food']['Amount'].sum() - df[df['Tags'] == 'Food']['Amount'].sum()),
                    round(df_ly[df_ly['Tags'] == 'House appliencies']['Amount'].sum() - df[df['Tags'] == 'House appliencies']['Amount'].sum()),
                    round(df_ly[df_ly['Tags'] == 'Beauty']['Amount'].sum() - df[df['Tags'] == 'Beauty']['Amount'].sum()),
                    round(df_ly[df_ly['Tags'] == 'Others']['Amount'].sum() - df[df['Tags'] == 'Others']['Amount'].sum())
                ]
        else:
            if (selection_yoy_ytd == "YTD" or selection_yoy_ytd == "RdD") and selection == max_year:
                KPI_list_LY = [
                    round(
                        (df[df['Tags'] != 'Inflows']['Amount'].sum() - df_ytd[df_ytd['Tags'] != 'Inflows']['Amount'].sum())
                        / df_ytd[df_ytd['Tags'] != 'Inflows']['Amount'].sum()
                        * 100, 1).astype(str) + " %",
                    round(
                        (df[df['Tags'] == 'Inflows']['Amount'].sum() - df_ytd[df_ytd['Tags'] == 'Inflows']['Amount'].sum())
                        / df_ytd[df_ytd['Tags'] == 'Inflows']['Amount'].sum() 
                        * 100, 1).astype(str) + " %",
                    round(
                        (df[df['Tags'] == 'Food']['Amount'].sum() - df_ytd[df_ytd['Tags'] == 'Food']['Amount'].sum()) 
                        / df_ytd[df_ytd['Tags'] == 'Food']['Amount'].sum() 
                        * 100, 1).astype(str) + " %",
                    round(
                        (df[df['Tags'] == 'House appliencies']['Amount'].sum() - df_ytd[df_ytd['Tags'] == 'House appliencies']['Amount'].sum()) 
                        / df_ytd[df_ytd['Tags'] == 'House appliencies']['Amount'].sum()
                        * 100, 1).astype(str) + " %",
                    round(
                        (df[df['Tags'] == 'Beauty']['Amount'].sum() - df_ytd[df_ytd['Tags'] == 'Beauty']['Amount'].sum())
                        / df_ytd[df_ytd['Tags'] == 'Beauty']['Amount'].sum()
                        * 100, 1).astype(str) + " %",
                    round(
                        (df[df['Tags'] == 'Others']['Amount'].sum() - df_ytd[df_ytd['Tags'] == 'Others']['Amount'].sum())
                        / df_ytd[df_ytd['Tags'] == 'Others']['Amount'].sum()
                        * 100, 1).astype(str) + " %"
                ]
            else:
                KPI_list_LY = [
                    round(
                        (df[df['Tags'] != 'Inflows']['Amount'].sum() - df_ly[df_ly['Tags'] != 'Inflows']['Amount'].sum())
                        / df_ly[df_ly['Tags'] != 'Inflows']['Amount'].sum()
                        * 100, 1).astype(str) + " %",
                    round(
                        (df[df['Tags'] == 'Inflows']['Amount'].sum() - df_ly[df_ly['Tags'] == 'Inflows']['Amount'].sum())
                        / df_ly[df_ly['Tags'] == 'Inflows']['Amount'].sum() 
                        * 100, 1).astype(str) + " %",
                    round(
                        (df[df['Tags'] == 'Food']['Amount'].sum() - df_ly[df_ly['Tags'] == 'Food']['Amount'].sum()) 
                        / df_ly[df_ly['Tags'] == 'Food']['Amount'].sum() 
                        * 100, 1).astype(str) + " %",
                    round(
                        (df[df['Tags'] == 'House appliencies']['Amount'].sum() - df_ly[df_ly['Tags'] == 'House appliencies']['Amount'].sum()) 
                        / df_ly[df_ly['Tags'] == 'House appliencies']['Amount'].sum()
                        * 100, 1).astype(str) + " %",
                    round(
                        (df[df['Tags'] == 'Beauty']['Amount'].sum() - df_ly[df_ly['Tags'] == 'Beauty']['Amount'].sum())
                        / df_ly[df_ly['Tags'] == 'Beauty']['Amount'].sum()
                        * 100, 1).astype(str) + " %",
                    round(
                        (df[df['Tags'] == 'Others']['Amount'].sum() - df_ly[df_ly['Tags'] == 'Others']['Amount'].sum())
                        / df_ly[df_ly['Tags'] == 'Others']['Amount'].sum()
                        * 100, 1).astype(str) + " %"
                ]
    except:
        KPI_list_LY = [0,0,0,0,0,0]

    # KPI's
    row1 = st.columns(3)
    row2 = st.columns(3)

    if selection == min_year or selection == 'All':
        for index, col in enumerate(row1 + row2):
            title = col.container(height=130)
            title.metric(KPI_list[index][0], 
                        str(round(KPI_list[index][1],2)) + " " + currency_icon)
    else:
        for index, col in enumerate(row1 + row2):
            title = col.container(height=130)
            title.metric(KPI_list[index][0],
                        str(round(KPI_list[index][1],2)) + " " + currency_icon, 
                        KPI_list_LY[index], delta_color="inverse")

    # Filters
    categories = st.multiselect(translations["sel_tags"][st.session_state.lang], options=df['Tags'].unique(), default=df['Tags'].unique())
    date_range = st.date_input(translations["sel_date"][st.session_state.lang], [df['Date'].min(), df['Date'].max()])
    start_date, end_date = date_range

    # Convert to datetime for comparison
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)

    # Filter the DataFrame
    dataframe_df = df[(df['Tags'].isin(categories)) & (df['Date'] >= start_date) & (df['Date'] <= end_date)]
    dataframe_df['Date'] = dataframe_df['Date'].dt.date

    # Display the filtered data
    st.write(translations["sel_trans"][st.session_state.lang])
    st.dataframe(dataframe_df[['Date','Desc','Tags','Amount']], use_container_width=True)

    # Line chart - Running balance
    st.write(translations["title_1"][st.session_state.lang])
    df['Week'] = df['Date'].dt.isocalendar().week
    chart_data = df[df['Tags'].isin(categories)].groupby('Week')['Amount'].sum().reset_index()

    area_chart = alt.Chart(chart_data).mark_area().encode(
        x="Week:T",
        y="Amount:Q",
        tooltip=['Week','Amount']
    )

    # Display the chart in Streamlit
    st.altair_chart(area_chart, use_container_width=True)

    # Bar chart 
    st.write(f'### {translations["title_2"][st.session_state.lang]}')
    df['Month'] = df['Date'].dt.month

    # Group by Month and Tags
    if selection != translations["all_year"][st.session_state.lang]: 
        grouped_data = df.groupby(['Month', 'Tags'], as_index=False)['Amount'].sum()
        # Create the bar chart using Altair
        chart = alt.Chart(grouped_data[grouped_data['Tags'].isin(categories)]).mark_bar().encode(
            x=alt.X('Month:O', title='Month'),
            y=alt.Y('Amount:Q', title = None),
            color=alt.Color('Tags:N', title='Tags'),  # Color based on Tags
            tooltip=['Month', 'Tags', 'Amount']  # Add tooltips for interactivity
        )
    else:
        grouped_data = df.groupby(['Year-Month', 'Tags'], as_index=False)['Amount'].sum()
        full_year_months = sorted(df['Year-Month'].unique())
        # Create the bar chart using Altair
        chart = alt.Chart(grouped_data[grouped_data['Tags'].isin(categories)]).mark_bar().encode(
            x=alt.X('Year-Month:O', title='Year-Month', sort=full_year_months),
            y=alt.Y('Amount:Q', title = None),
            color=alt.Color('Tags:N', title='Tags'),  # Color based on Tags
            tooltip=['Year-Month', 'Tags', 'Amount']  # Add tooltips for interactivity
        )

    # Display the chart in Streamlit
    st.altair_chart(chart, use_container_width=True)