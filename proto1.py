#requirements
import yfinance as yf
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import datetime as dt
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st 

def accion(symbol,start_date,end_date):
  asset_data = yf.download(symbol, start = start_date, end = end_date)['Close']
  asset_info = yf.Ticker(symbol).info
  normalized_price = asset_data / asset_data.iloc[0] * 100
 #estimating market cap
  marketCap = asset_data.iloc[-1] * yf.Ticker(symbol).info['sharesOutstanding']
  pe_ratio = asset_info.get('trailingPE', None)
  pb_ratio = asset_info.get('priceToBook', None)
  #market cap = asset's last price * number of outstanding shares
  '''se utiliza iloc para acceder al último elemento de la lista (asset_data) por medio de su
  indice, no del nombre de la fila'''

  st.subheader("\nBasic Information:")

  st.write(f"Name: {asset_info.get('longName', 'Not Available')}")

  st.write(f"Sector: {asset_info.get('sector', 'Not Available')}")

  st.write(f"Industry: {asset_info.get('industry', 'Not Available')}")

  st.write(f"Country: {asset_info.get('country', 'Not Available')}")

  st.write(f'{symbol}´s approximate market capitalization is ${marketCap.iloc[0]}')

  st.write(f'{symbol}´s P/E ratio is {pe_ratio}')

  st.write(f'{symbol}´s P/B ratio is {pb_ratio}')

  #price plot
  st.subheader(f'{symbol}´s price over time') 
  fig, ax =plt.subplots()
  ax.plot(asset_data.index, asset_data.values, color = 'b')
  ax.set_xlabel('Date')
  ax.set_ylabel('Price')
  ax.set_title(f'{symbol}´s Price Over Time')
  st.pyplot(fig)

  #return plot
  st.subheader(f'{symbol}´s Return over the selected period')
  fig, ax = plt.subplots()
  ax.plot(normalized_price.index, normalized_price.values, color = 'g')
  ax.set_xlabel('Date')
  ax.set_ylabel('Return %')
  ax.set_title(f'{symbol}´s Return Over the Selected Period of Time')
  ax.grid(True)
  st.pyplot(fig)


def asset_comparisson(symbols):
  normalized_data = pd.DataFrame()
  for s in symbols: 
    asset_dta = yf.download(s, start = start_date, end = end_date)['Close']
    normalized_data[s] = asset_dta / asset_dta.iloc[0] *100

#graficar comparación
  plt.figure(figsize = (12, 6))
  normalized_data.plot(title = 'Return Comparisson')
  plt.xlabel('Date')
  plt.ylabel('Return %')
  plt.legend(symbols)
  plt.grid(True)
  plt.show()

  metrics = {
        'P/E Ratio': [],
        'P/B Ratio': [],
        'Market Cap in Billions': [],
        'Dividend Yield':[]
    }
  for s in symbols:
    asset_ifo = yf.Ticker(s).info
    metrics['P/E Ratio'].append(asset_ifo.get('trailingPE', None))
    metrics['P/B Ratio'].append(asset_ifo.get('priceToBook', None))
    metrics['Market Cap in Billions'].append(asset_ifo.get('marketCap', 0) / 1e9)
    metrics['Dividend Yield'].append(asset_ifo.get('dividendYield', 0) * 100 if asset_ifo.get('dividendYield', 0) else None)
    
  df_metrics = pd.DataFrame(metrics, index = symbols) #el indice de cada fila sera el simbolo de cada accion
  print('\nMetric Comparisson between the assets')
  print(df_metrics)

symbol = input(str("Ingrese el símbolo de la acción: "))
print("Las fechas deben estar en formato YYYY/MM/DD")
#getting the dates (period)
start_date = input(str("Ingrese la fecha de inicio: "))
end_date = input(str("Ingrese la fecha de finalización: "))
accion(symbol, start_date, end_date)
 
symbols = input(str("Ingrese los símbolos de las acciones a comparar, separados por comas: ")).split(',')
asset_comparisson(symbols)


# Configuración de la página de Streamlit
title = "Project A1 (Prototype 1)"
st.set_page_config(page_title=title, layout="wide")
st.title(title)

# Opciones para la selección
graph_options = [
    "Fundamental Analysis",
    "Asset Comparisson",
    "Asset Analysis",
    "Portfolio Analysis Using Black-Litterman Model"
]
selected_option = st.sidebar.selectbox('What are we doing today?', graph_options)

if selected_option == "Fundamental Analysis":
    symbol = st.text_input("Ingrese el símbolo de la acción:", "AAPL")
    st.write("Las fechas deben estar en formato YYYY-MM-DD")

    start_date = st.date_input("Ingrese la fecha de inicio:").strftime('%Y-%m-%d')
    end_date = st.date_input("Ingrese la fecha de finalización:").strftime('%Y-%m-%d')

    if st.button("Analizar"):
        if symbol and start_date and end_date:
            accion(symbol, start_date, end_date)
        else:
            st.warning("Por favor, complete todos los campos antes de continuar.")
else:
   st.write('Under Construction...')