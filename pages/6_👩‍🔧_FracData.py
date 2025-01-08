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

# Load and preprocess the fracture data
@st.cache_data
def load_and_sort_data_frac(dataset_url):
    try:
        COLUMNS_FRAC = [
            'sigla', 'empresa', 'anio', 'mes', 'yacimiento', 'cantidad_etapas',
            'profundidad', 'fecha_frac', 'prod_frac_gas', 'prod_frac_pet'
        ]
        df_frac = pd.read_csv(dataset_url, usecols=COLUMNS_FRAC)
        df_frac['fecha_frac'] = pd.to_datetime(df_frac['fecha_frac'])
        return df_frac
    except Exception as e:
        st.error(f"Error loading fracture data: {e}")
        return pd.DataFrame()

# URLs for datasets
dataset_url = "http://datos.energia.gob.ar/dataset/c846e79c-026c-4040-897f-1ad3543b407c/resource/b5b58cdc-9e07-41f9-b392-fb9ec68b0725/download/produccin-de-pozos-de-gas-y-petrleo-no-convencional.csv"
dataset_frac_url = "http://datos.energia.gob.ar/dataset/71fa2e84-0316-4a1b-af68-7f35e41f58d7/resource/2280ad92-6ed3-403e-a095-50139863ab0d/download/datos-de-fractura-de-pozos-de-hidrocarburos-adjunto-iv-actualizacin-diaria.csv"

# Load the production data
data_sorted = load_and_sort_data(dataset_url)

if data_sorted.empty:
    st.error("Failed to load production data.")
    st.stop()

# Load the fracture data
data_frac = load_and_sort_data_frac(dataset_frac_url)

if data_frac.empty:
    st.error("Failed to load fracture data.")
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

# Display fracture data summary
st.subheader("Fractura de Pozos")
st.dataframe(data_frac.head())

# Fracture data visualization (example)
frac_summary = (
    data_frac.groupby(['fecha_frac', 'empresa'])
    .agg(total_etapas=('cantidad_etapas', 'sum'))
    .reset_index()
)
fig_frac = px.bar(
    frac_summary,
    x='fecha_frac', y='total_etapas', color='empresa',
    title="Número de Etapas de Fractura por Empresa"
)
fig_frac.update_layout(
    xaxis_title="Fecha de Fractura",
    yaxis_title="Número de Etapas",
    legend_title="Empresa"
)
st.plotly_chart(fig_frac)
