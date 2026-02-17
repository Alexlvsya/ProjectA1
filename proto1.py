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


#ANALISIS FUNDAMENTAL
@st.cache_data(ttl=3600)
def get_asset_data(symbol, start_date, end_date):
    ticker = yf.Ticker(symbol)
    
    data = yf.download(symbol, start=start_date, end=end_date)['Close']
    
    fast_info = ticker.fast_info   # MUCHÍSIMO más ligero
    full_info = ticker.info        # solo una vez
    
    return data, fast_info, full_info
def accion(symbol, start_date, end_date):
    try:
        asset_data, fast_info, asset_info = get_asset_data(symbol, start_date, end_date)
        
        if asset_data.empty:
            st.error("No data found for this symbol.")
            return

        normalized_price = asset_data / asset_data.iloc[0] * 100

        # Market Cap usando fast_info
        last_price = asset_data.iloc[-1]
        shares_outstanding = fast_info.get("sharesOutstanding", None)

        marketCap = last_price * shares_outstanding if shares_outstanding else None

        pe_ratio = asset_info.get('trailingPE', None)
        pb_ratio = asset_info.get('priceToBook', None)

  #market cap = asset's last price * number of outstanding shares
  #se utiliza iloc para acceder al último elemento de la lista (asset_data) por medio de su
  #indice, no del nombre de la fila

  st.subheader("\nBasic Information:")

  st.write(f"Name: {asset_info.get('longName', 'Not Available')}")

  st.write(f"Sector: {asset_info.get('sector', 'Not Available')}")

  st.write(f"Industry: {asset_info.get('industry', 'Not Available')}")

  st.write(f"Country: {asset_info.get('country', 'Not Available')}")

  st.write(f'{symbol}´s approximate market capitalization is ${marketCap.iloc[0]}')
  st.write("Market Capitalization is the total market value of the company's outstanding shares")

  st.write(f'{symbol}´s P/E ratio is {pe_ratio}')
  st.write('''Obtained with the following formula: price per share / earnings per share; it shows
   how much investors are willing to pay for each dollar of  the company's profit''')

  st.write(f'{symbol}´s P/B ratio is {pb_ratio}')
  st.write('''Obtained with the following formula: price per share / book value per share; it measures
   how much investors are willing to pay for each dollar of a company's assets. If P/B ratio is 1, the company´s 
   market value is the same as its book value, if P/B ratio <1 the company is possibly undervaluated, if 
   P/B>1, there could be additional value that is not into accounting books.''')

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

#COMPARACION DE ACTIVOS 
def asset_comparisson(symbols, start_date, end_date):
  normalized_data = pd.DataFrame()
  for s in symbols: 
    asset_dta = yf.download(s, start = start_date, end = end_date)['Close']
    normalized_data[s] = asset_dta / asset_dta.iloc[0] *100

#graficar comparación
  st.line_chart(normalized_data)

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
  st.subheader('\nMetric Comparisson between the assets')
  st.write(df_metrics)

#ASSET ANALYSIS
# Función para calcular el CVaR
def calculate_cvar(returns, alpha=0.05):
    var = np.percentile(returns, 100 * alpha)
    cvar = returns[returns <= var].mean()  # Media de los valores menores que el VaR
    return cvar

# Descargar y analizar datos de activos
def asset_analysis(etfs, start_date, end_date):
    data = yf.download(etfs, start=start_date, end=end_date)['Close']
    risk_free_rate = 0.00116 / 252  # Tasa libre de riesgo diaria
    daily_returns = data.pct_change()  # Rendimientos diarios en términos porcentuales

    # Diccionario para almacenar las métricas
    metrics = {}

    st.subheader("Análisis de activos")
    for etf in etfs:
        etf_returns = daily_returns[etf].dropna()

        if etf_returns.empty:
            st.warning(f"No se encontraron datos para {etf} en el rango de fechas proporcionado.")
            continue

        # Calcular métricas
        mean = etf_returns.mean()
        skewness = etf_returns.skew()
        kurtosis = etf_returns.kurtosis()
        var = np.percentile(etf_returns, 5)
        cvar = calculate_cvar(etf_returns)
        sharpe_ratio = (mean - risk_free_rate) / etf_returns.std()
        downside_returns = etf_returns[etf_returns < 0]
        sortino_ratio = (mean - risk_free_rate) / downside_returns.std()

        # Guardar métricas en el diccionario
        metrics[etf] = {
            "Mean": mean,
            "Skewness": skewness,
            "Excess Kurtosis": kurtosis,
            "VaR (95%)": var,
            "CVaR (95%)": cvar,
            "Sharpe Ratio": sharpe_ratio,
            "Sortino Ratio": sortino_ratio
        }

        # Mostrar gráfico de retornos diarios
        st.subheader(f"Gráfico de VaR/CVaR para {etf}")
        plt.figure(figsize=(12, 6))
        plt.plot(etf_returns.index, etf_returns, color="#2C3E50", label=f'Rendimientos diarios - {etf}')
        plt.fill_between(etf_returns.index, etf_returns, color='#2C3E50', alpha=0.1)
        plt.axhline(y=var, color='red', linestyle='--', linewidth=1.5, label=f'VaR (95%): {var:.2%}')
        plt.axhline(y=cvar, color='green', linestyle='--', linewidth=1.5, label=f'CVaR (95%): {cvar:.2%}')
        plt.title(f'VaR y CVaR para {etf}', fontsize=16)
        plt.xlabel('Fecha', fontsize=14)
        plt.ylabel('Retorno', fontsize=14)
        plt.legend(loc="upper left", frameon=True, shadow=True)
        plt.grid(color='gray', linestyle='--', linewidth=0.5, alpha=0.7)
        plt.tight_layout()
        st.pyplot(plt)

    # Mostrar métricas en una tabla interactiva de Streamlit
    if metrics:
        metrics_df = pd.DataFrame(metrics).T.round(4)
        st.subheader("Métricas calculadas")
        st.dataframe(metrics_df)

#CONFIGURACIÓN STREAMLIT

# Configuración de la página
st.set_page_config(
    page_title="Project A1 (Prototype 1)",
    page_icon="📈",
    layout="wide",
)

# Título principal
st.title("Project A1 (Prototype 1)")
st.write("Created by Alejandro Ramirez Camacho, Actuarial Science´s Student, Universidad Nacional Autónoma de México")
st.write("Created for educational purposes, invest under your own risk :) ")

# Opciones para la selección
graph_options = [
    "About the Author",
    "Fundamental Analysis",
    "Asset Comparisson",
    "Asset Analysis",
    "Portfolio Analysis Using Black-Litterman Model"
]
selected_option = st.sidebar.selectbox('What are we doing today?', graph_options)

if selected_option == "About the Author":
    st.title("Message from the Author")
    
    # URL de la imagen (repositorio de GitHub o cualquier otro enlace público)
    image_url = "https://raw.githubusercontent.com/Alexlvsya/ProjectA1/main/IMG_8831.JPEG"
    # Mostrar imagen centrada
    st.image(
        image_url, 
        caption="Alejandro Ramirez  - Author", 
          # Evita que la imagen se expanda a todo el ancho
        width=120  # Ajusta este valor según el tamaño real de la imagen
    )
    
    # Información adicional sobre el autor
    st.write("""
  Hello! My name is Alejandro, and I am an 8th-semester student of Actuarial Sciences
    at Universidad Nacional Autónoma de México (UNAM). I have recently 
    completed an exchange semester at University of Helsinki, and with the knowledge 
    I've gained over the past three years, I am developing a Streamlit app focused
    on Asset Allocation and Portfolio Management.
             
    The goal of this prototype application is to provide basic yet valuable insights 
    into various assets available in the stock market and explain this information in 
    a simple and accessible way for users. I am thrilled to see how far this project can go, 
    and my aspiration is that, over time, this application will become a helpful tool for
    investors to identify suitable assets and maximize their profits in the stock market.

    I am particularly interested in pursuing a career in quantitative finance.

    To gather live data for the app, I am using the yfinance API for Python, and all the source 
    code is hosted on GitHub.

    Feel free to contact me via email with any questions or suggestions you may have.
                
    """)
    st.markdown("[Alejandro's LinkedIn Profile ](https://www.linkedin.com/in/alejandro-ramirez-camacho-7b4b28247)")
    st.write("e-mail : alexramca@icloud.com")

elif selected_option == "Fundamental Analysis":
    symbol = st.text_input("Ingrese el símbolo de la acción:", "AAPL")
    st.write("Las fechas deben estar en formato YYYY-MM-DD")

    start_date = st.date_input("Ingrese la fecha de inicio:").strftime('%Y-%m-%d')
    end_date = st.date_input("Ingrese la fecha de finalización:").strftime('%Y-%m-%d')

    if st.button("Analizar"):
        if symbol and start_date and end_date:
            accion(symbol, start_date, end_date)
        else:
            st.warning("Por favor, complete todos los campos antes de continuar.")
elif selected_option == "Asset Comparisson":
   st.subheader("Asset Comparisson")

   symbols = st.text_input("Ingrese los simbolos de las acciones separadas por comas")
   symbols = [s.strip() for s in symbols.split(',') if s.strip()]
   st.write("Las fechas deben estar en formato YYYY-MM-DD")

   start_date = st.date_input("Ingrese la fecha de inicio:").strftime('%Y-%m-%d')
   end_date = st.date_input("Ingrese la fecha de finalización:").strftime('%Y-%m-%d')
   if st.button("Analize"):
      if symbols and start_date and end_date:
          asset_comparisson(symbols, start_date, end_date)
      else:
          st.warning("Por favor, complete todos los campos antes de continuar.")
elif selected_option == "Asset Analysis":
  st.subheader("Asset Analysis")

  etfs = st.text_input("Ingrese los símbolos de las acciones a comparar, separados por comas:")

  start_date = st.date_input("Ingrese la fecha de inicio:").strftime('%Y-%m-%d')
  end_date = st.date_input("Ingrese la fecha de finalización:").strftime('%Y-%m-%d')
  if st.button("Analizar"):
    if etfs and start_date and end_date:
        etfs_list = [etf.strip() for etf in etfs.split(",") if etf.strip()]
        if etfs_list:
            asset_analysis(etfs_list, start_date, end_date)
        else:
            st.warning("Por favor, ingrese al menos un símbolo válido.")
    else:
        st.warning("Por favor, complete todos los campos antes de continuar.")
else:
   st.write('Under Construction...')
