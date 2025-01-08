import pandas as pd
import plotly.express as px
import streamlit as st

# Streamlit configuration
st.title("Producción y Fractura de Pozos de Hidrocarburos")

# Load and preprocess the production data
@st.cache_data
def load_and_sort_data(dataset_url):
    try:
        df = pd.read_csv(dataset_url, usecols=[
            'sigla', 'anio', 'mes', 'prod_pet', 'prod_gas', 'prod_agua',
            'tef', 'empresa', 'areayacimiento', 'coordenadax', 'coordenaday',
            'formprod', 'sub_tipo_recurso', 'tipopozo'
        ])
        df['date'] = pd.to_datetime(df['anio'].astype(str) + '-' + df['mes'].astype(str) + '-1')
        df['gas_rate'] = df['prod_gas'] / df['tef']
        df['oil_rate'] = df['prod_pet'] / df['tef']
        df['water_rate'] = df['prod_agua'] / df['tef']
        df['Np'] = df.groupby('sigla')['prod_pet'].cumsum()
        df['Gp'] = df.groupby('sigla')['prod_gas'].cumsum()
        df['Wp'] = df.groupby('sigla')['prod_agua'].cumsum()
        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame()

# URLs for datasets
dataset_url = "http://datos.energia.gob.ar/dataset/c846e79c-026c-4040-897f-1ad3543b407c/resource/b5b58cdc-9e07-41f9-b392-fb9ec68b0725/download/produccin-de-pozos-de-gas-y-petrleo-no-convencional.csv"

# Load the production data
data_sorted = load_and_sort_data(dataset_url)

if data_sorted.empty:
    st.error("Failed to load production data.")
    st.stop()

# Replace company names in production data
replacement_dict = {
    'PAN AMERICAN ENERGY (SUCURSAL ARGENTINA) LLC': 'PAN AMERICAN ENERGY',
    'PAN AMERICAN ENERGY SL': 'PAN AMERICAN ENERGY',
    'VISTA ENERGY ARGENTINA SAU': 'VISTA',
    'Vista Oil & Gas Argentina SA': 'VISTA',
    'VISTA OIL & GAS ARGENTINA SAU': 'VISTA',
    'WINTERSHALL DE ARGENTINA S.A.': 'WINTERSHALL',
    'WINTERSHALL ENERGÍA S.A.': 'WINTERSHALL'
}
data_sorted['empresaNEW'] = data_sorted['empresa'].replace(replacement_dict)

# Aggregate data for plotting (production)
company_summary_aggregated = (
    data_sorted.groupby(['date', 'empresaNEW'])
    .agg(total_gas_rate=('gas_rate', 'sum'), total_oil_rate=('oil_rate', 'sum'))
    .reset_index()
)

# Display production plots
st.subheader("Caudal de Gas por Empresa")
fig_gas_company = px.area(
    company_summary_aggregated,
    x='date', y='total_gas_rate', color='empresaNEW',
    title="Caudal de Gas por Empresa"
)
fig_gas_company.update_layout(
    xaxis_title="Fecha",
    yaxis_title="Caudal de Gas (km³/d)",
    legend_title="Empresa"
)
st.plotly_chart(fig_gas_company)

st.subheader("Caudal de Petróleo por Empresa")
fig_oil_company = px.area(
    company_summary_aggregated,
    x='date', y='total_oil_rate', color='empresaNEW',
    title="Caudal de Petróleo por Empresa"
)
fig_oil_company.update_layout(
    xaxis_title="Fecha",
    yaxis_title="Caudal de Petróleo (m³/d)",
    legend_title="Empresa"
)
st.plotly_chart(fig_oil_company)

# Yearly data aggregation
data_sorted['start_year'] = data_sorted['anio']
yearly_summary = (
    data_sorted.groupby(['date', 'start_year'])
    .agg(total_gas_rate=('gas_rate', 'sum'), total_oil_rate=('oil_rate', 'sum'))
    .reset_index()
)

st.subheader("Caudal de Gas por Año de Puesta en Marcha de Pozo")
fig_gas_year = px.area(
    yearly_summary,
    x='date', y='total_gas_rate', color='start_year',
    title="Caudal de Gas por Año de Puesta en Marcha de Pozo"
)
fig_gas_year.update_layout(
    xaxis_title="Fecha",
    yaxis_title="Caudal de Gas (km³/d)",
    legend_title="Año de Puesta en Marcha de Pozo"
)
st.plotly_chart(fig_gas_year)

st.subheader("Caudal de Petróleo por Año de Puesta en Marcha de Pozo")
fig_oil_year = px.area(
    yearly_summary,
    x='date', y='total_oil_rate', color='start_year',
    title="Caudal de Petróleo por Año de Puesta en Marcha de Pozo"
)
fig_oil_year.update_layout(
    xaxis_title="Fecha",
    yaxis_title="Caudal de Petróleo (m³/d)",
    legend_title="Año de Puesta en Marcha de Pozo"
)
st.plotly_chart(fig_oil_year)
