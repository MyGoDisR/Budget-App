# Libraries
import streamlit as st
import pandas as pd
import altair as alt
import numpy as np
import sys
import os
import utils.web_scrap as web_scrap
from datetime import datetime
import matplotlib.pyplot as plt
import utils.navigation as navigation
import utils.queries as qs
import geopandas as gpd
import altair as alt
import geoplot
import geoplot.crs as gcrs
from streamlit.components.v1 import html

# Security 
if "role_" not in st.session_state:
    st.switch_page("app.py")

# Language
if 'lang' not in st.session_state:
    st.session_state.lang = "ENG"

def webscrap_get(real_estate_user_choice, town_user_choice, user_choice_webscrap):
    df_all = pd.DataFrame()
    info_ = []
    if len(user_choice_webscrap) == 0 or len(user_choice_webscrap) == 3:
        g = web_scrap.gratka(user_choice_option_1=real_estate_user_choice, user_choice_option_3=town_user_choice)
        x = web_scrap.olx(user_choice_option_1=real_estate_user_choice, user_choice_option_3=town_user_choice)
        o = web_scrap.otodom(user_choice_option_1=real_estate_user_choice, user_choice_option_3=town_user_choice)
    else:
        if 'G' in user_choice_webscrap:
            g = web_scrap.gratka(user_choice_option_1=real_estate_user_choice, user_choice_option_3=town_user_choice)
        
        if 'O' in user_choice_webscrap:
            o = web_scrap.otodom(user_choice_option_1=real_estate_user_choice, user_choice_option_3=town_user_choice)
        
        if 'X' in user_choice_webscrap:
            x = web_scrap.olx(user_choice_option_1=real_estate_user_choice, user_choice_option_3=town_user_choice)
    
    if g != None:
        df_all = pd.concat([df_all,g])
        info_.append('Real estates from Gratka has been retrieved')
    if x != None:
        df_all = pd.concat([df_all,x])
        info_.append('Real estates from OLX has been retrieved')
    if o != None:
        df_all = pd.concat([df_all,o])
        info_.append('Real estates from Otodom has been retrieved')

    return df_all
    

# Side bar
navigation.menu()

# This is for translation
translations = {
    "title": {"ENG": "Real Estate analysis", "POL": "Analiza rynku nieruchomości"},
    "description_1": {"ENG": "This page was created to track real estate market in Poland. The datasource right now is just Gratka.pl website but in the future there will be more",
                      "POL": "Ta strona została stworzona aby zbierać dane na temat rynku nieruchomości w Polsce. Na ten moment strona zaciąga dane tylko z Gratka.pl ale w planach jest dodanie nowych źródeł danych"},
    "description_2": {
        "ENG": "Since the website uses web scraping techniques o get the data it can take up to 30min for script to run so be patient everything will be done in he background. Meanwhile user can analyse past data if they are avilable", 
        "POL": "Ponieważ strona używa technik ogólnego w'web scrappingu' nie jest to optymalna metoda daltego niektóre zapytania mogą być procesowane nawet 30min. Jednakże użytkownik może w tym czasie analizować historyczne dane jeżeli są dostępne"},
    "options": {"ENG": ['Flats for rent','Flats for sale','Houses for sale','Lands for sale'], 
                "POL": ["Mieszkania na wynajem",'Mieszkania na sprzedaż','Domy na sprzedaż','Działki na sprzedaż']},
    "which_page": {"ENG": "Below you can find a check list with sources from which data is begin retrieved. Please check from which you would like to get the data from",
                   "POL": "Poniej znajdziesz list z których źródeł zaciągane są dane apropos nieruchomości. Proszę wybrać te które Ciebie interesują"},
    "place": {"ENG": "Town name", "POL": "Miasto"},
    "price_range_low": {"ENG": "Price From:", "POL": "Cena od:"},
    "price_range_high": {"ENG": "Price to:", "POL": "Cena do:"},
    "which_real_estate": {"ENG": "Search:", "POL": "Szukaj:"},
    "kpi_1": {"ENG":"Nummber of offers", "POL":"Ilość ofert:"},
    "kpi_2": {"ENG": "Average price per sqrtm", "POL": "Średnia cena za m2"},
    "kpi_3": {"ENG": "Average price in the area", "POL": "Średnia cena za nieruchomość"},
    "kpi_4": {"ENG": "Average sqrtm", "POL": "Średni metraż nieruchomości"},
    "optimize": {"ENG": "Do you want me to optimize the data?", "POL": "Czy chcesz zoptumalizaować dane?"},
    "optimize_desc": {"ENG":"Optimization of the data means getting rid of outliers and those offers which might have an impact on an overall view of the market in the area", 
                    "POL":"Optymalizacja danych polega na pozbyciu się tych ofert które mają negatywny wpływ na ogólny widok rynku np. znacząco wygórowana cena które zaburza proporcje śrenidej ceny w okolicy"},
    "yes_option": {"ENG": "Yes", "POL": "Tak"},
    "yes_clicked": {"ENG": "Data has been optmized!", "POL": "Dane zostały zoptymalizowane!"},
    "no_option": {"ENG": "No", "POL": "Nie"},
    "no_clicked": {"ENG": "Data hasn't been optmized!", "POL": "Dane nie zostały zoptymalizowane!"},
    "dataframe_2": {"ENG": ['Median price m2','Mean price m2','No. of offers','Location'], "POL": ['Mediana cen za m2','Średnia cena za m2','Liczba ofert','Dzielnica']},
    "button_text":{"ENG":"Submit", "POL":"Wyszukaj"},
    "title_2":{"ENG":"Below you can find historical analysis:", "POL":"Poniej możesz znaleźć historyczne dane:"},
    "no_data_info": {"ENG":"there is no data yet","POL":"Brak danych"},
    "title_3":{"ENG":'Detailed view on flats', "POL":"Szczegółowe dane nieruchomości"},
    "title_4":{"ENG":'Summarization of offers',"POL":"Podsumowanie ofert"},
    "tooltip_map":{"ENG":['Location','Median price m2','Mean price m2', 'No. of offers'], 
                   "POL":['Dzielnica','Mediana cen za m2','Średnia cena za m2','Liczba ofert']}
}

st.title(translations["title"][st.session_state.lang])
st.write(translations["description_1"][st.session_state.lang])
st.write(translations["description_2"][st.session_state.lang])


st.write(translations["which_page"][st.session_state.lang])
gratka = st.checkbox('Gratka.pl')
otodom = st.checkbox('Otodom.pl')
olx = st.checkbox('OLX.pl')

user_choice_webscrap = []

if gratka:
    user_choice_webscrap.append('G')
if otodom:
    user_choice_webscrap.append('O')
if olx:
    user_choice_webscrap.append('X')

st.write('')
st.write('')
# Form to downalod data
dfColumns = st.columns(4)
with dfColumns[0]:
    real_estate_user_choice = st.selectbox(translations['which_real_estate'][st.session_state.lang], translations['options'][st.session_state.lang], key='real_estate_type')
with dfColumns[1]:
    town_user_choice = st.text_input(translations["place"][st.session_state.lang], key='town_')
with dfColumns[2]:
    price_form_user_choice = st.text_input(translations["price_range_low"][st.session_state.lang], key='price_from_')
with dfColumns[3]:
    price_to_user_choice =st.text_input(translations["price_range_high"][st.session_state.lang], key='price_to_')

st.write('')
if st.button(translations["button_text"][st.session_state.lang], width="stretch"):
    st.write(webscrap_get(real_estate_user_choice, town_user_choice, user_choice_webscrap))
#st.write('')
st.write(translations["title_2"][st.session_state.lang])

tab1, tab2, tab3, tab4 = st.tabs(translations["options"][st.session_state.lang])

with tab1:
    st.write(translations["no_data_info"][st.session_state.lang])
with tab2:

    # getting data
    # Checking userbase 
    df = qs.get_flats_for_sale()
    data = gpd.read_file('Data/GeoJsons/krakow-dzielnice.geojson')
    data[['2','3']] = data.name.str.split(' ', expand=True)[[2,3]]
    data['location'] = ''
    for i in range(0,len(data)):
        if data['3'][i] == None:
            data['location'][i] = data['2'][i]
        else:
            data['location'][i] = data['2'][i] + ' ' + data['3'][i]
    data.drop(columns=['2','3'], inplace=True)
    merge = pd.merge(data,df,on='location',how='right')
    merge['one'] = merge['name'].apply(lambda x: 'Unknown' if pd.isna(x) == True else 'Known')
    merge['location'] = merge.apply(lambda row: row['location'] if row.one == 'Known' else 'Unknown', axis=1)
    merge.drop(columns=['cartodb_id','one'],inplace=True)
    merge = merge[merge['sqrmeter']!='Szlak,']
    #merge['sqrmeter'] = merge['sqrmeter'].astype(float)
    
    st.write(translations['optimize_desc'][st.session_state.lang])
    st.write(translations['optimize'][st.session_state.lang])
    new_df = merge
    dfColumns = st.columns(2)
    with dfColumns[0]:
        if st.button(translations['yes_option'][st.session_state.lang]):
            st.write(translations['yes_clicked'][st.session_state.lang])
            new_df = pd.DataFrame()
            for i in merge.location.unique():
                df = merge[merge['location'] == i]

                lower = (df['price_per_m2'].mean()) - (df['price_per_m2'].std() * 3)
                upper = (df['price_per_m2'].mean()) + (df['price_per_m2'].std() * 3)

                df = df[df['price_per_m2'].notna()]
                df = df[(df['price_per_m2'] > lower) & (df['price_per_m2'] < upper)]

                new_df = pd.concat([new_df,df])
    with dfColumns[1]:
        if st.button(translations['no_option'][st.session_state.lang]):
            st.write(translations['no_clicked'][st.session_state.lang])
            new_df = merge.copy()


    KPI_list = [
        [translations["kpi_1"][st.session_state.lang], format(new_df['price'].count(),',') ],
        [translations["kpi_2"][st.session_state.lang], "{:,.0f} PLN".format(int(new_df['price_per_m2'].mean()))],
        [translations["kpi_3"][st.session_state.lang], "{:,.0f} PLN".format(int(new_df['price'].mean()))]
        #,[translations["kpi_4"][st.session_state.lang], "{:} m2".format(int(new_df['sqrmeter'].mean()))]
    ]
    # There will be a KPI's which gives the rough indicator
    row1 = st.columns(2)
    row2 = st.columns(2)

    for index, col in enumerate(row1 + row2):
        title = col.container(height=120)
        title.metric(KPI_list[index][0], KPI_list[index][1])


    st.title(translations["title_3"][st.session_state.lang])
    #st.dataframe(new_df[new_df['price'] > 0].iloc[:,2:], hide_index=True)
    st.dataframe(new_df[new_df['price'] > 0].iloc[:,2:],
        column_config={
            "link": st.column_config.LinkColumn(
                "link", display_text= r"https://.\*?#(.\*)$")
            },
        hide_index=True)
    st.write('')
    st.write('')

    df_ = pd.DataFrame(new_df.groupby(by='location')['price_per_m2'].median().round(2)).join(pd.DataFrame(new_df.groupby(by='location')['price_per_m2'].mean().round(2)),
                      lsuffix='_median', rsuffix='_mean').join(pd.DataFrame(new_df.groupby(by='location')['price'].count())).rename(
                          columns={'price_per_m2_median':translations['dataframe_2'][st.session_state.lang][0],
                                    'price_per_m2_mean':translations['dataframe_2'][st.session_state.lang][1],
                                    'price':translations['dataframe_2'][st.session_state.lang][2]}
                                    )
    
    st.title(translations["title_4"][st.session_state.lang])
    df_map = df_.join(merge[['geometry','location']].set_index('location')).reset_index().rename(columns={'index':translations['dataframe_2'][st.session_state.lang][3]})

    m = gpd.GeoDataFrame(df_map.reset_index()).rename(columns={'location':translations['dataframe_2'][st.session_state.lang][3]}).explore(
        tooltip=translations['tooltip_map'][st.session_state.lang]
        ,style_kwds={"color": "grey", "weight": 2, "fill": True,"fillColor": "transparent","fillOpacity": 0.0
    }
    )

    # Display in Streamlit
    html(m._repr_html_(), height=600)
    #st.dataframe(df_)

with tab3:
    st.write(translations["no_data_info"][st.session_state.lang])
with tab4:
    st.write(translations["no_data_info"][st.session_state.lang])