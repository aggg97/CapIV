import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from PIL import Image
import plotly.express as px  # Import Plotly Express for bar plots

COLUMNS = [
    'sigla',  # atemporal
    'anio',  # temporal
    'mes',  # temporal
    'prod_pet',  # temporal
    'prod_gas',  # temporal
    'prod_agua',  # temporal
    'iny_gas',  # temporal
    'tef',  # temporal
    'tipoextraccion',  # atemporal
    'tipopozo',  # atemporal
    'empresa',  # atemporal
    'formacion',  # atemporal
    'areayacimiento',  # atemporal
    'fecha_data'  # temporal
]

COLUMNS_NAMES = [
    'Sigla',
    'Año',
    'Mes',
    'Producción de Petróleo (m3)',
    'Producción de Gas (km3)',
    'Producción de Agua (m3)',
    'Inyección de Gas (km3)',
    'TEF',
    'Tipo de Extracción',
    'Tipo de Pozo',
    'Empresa',
    'Formación',
    'Área yacimiento',
    'Fecha de Datos'
]

# Define palettes for Gas Rate and Gp, Oil Rate and Np, and Water Rate and Wp
gas_gp_palette = ['#FF0000', '#FFA07A', '#FA8072', '#E9967A', '#F08080', '#CD5C5C', '#DC143C', '#B22222', '#8B0000']
oil_np_palette = ['#008000', '#006400', '#90EE90', '#98FB98', '#8FBC8F', '#3CB371', '#2E8B57', '#808000', '#556B2F', '#6B8E23']
water_wp_palette = ['#0000FF', '#0000CD', '#00008B', '#000080', '#191970', '#7B68EE', '#6A5ACD', '#483D8B', '#B0E0E6', '#ADD8E6', '#87CEFA', '#87CEEB', '#00BFFF', '#B0C4DE', '#1E90FF', '#6495ED']

# Reorder and rename the columns in the DataFrame
@st.cache_data
def load_and_sort_data(dataset_url):
    df = pd.read_csv(dataset_url, usecols=COLUMNS)
    data_sorted = df.sort_values(by=['sigla', 'fecha_data'], ascending=True)
    data_sorted = data_sorted[COLUMNS]
    data_sorted['gas_rate'] = data_sorted['prod_gas'] / data_sorted['tef']
    data_sorted['oil_rate'] = data_sorted['prod_pet'] / data_sorted['tef']
    data_sorted['water_rate'] = data_sorted['prod_agua'] / data_sorted['tef']
    data_sorted['Np'] = data_sorted.groupby('sigla')['prod_pet'].cumsum()
    data_sorted['Gp'] = data_sorted.groupby('sigla')['prod_gas'].cumsum()
    data_sorted['Wp'] = data_sorted.groupby('sigla')['prod_agua'].cumsum()
    return data_sorted

def calculate_max_rates(group):
    return group[['gas_rate', 'oil_rate']].max()

# URL of the dataset
dataset_url = "http://datos.energia.gob.ar/dataset/c846e79c-026c-4040-897f-1ad3543b407c/resource/b5b58cdc-9e07-41f9-b392-fb9ec68b0725/download/produccin-de-pozos-de-gas-y-petrleo-no-convencional.csv"

# Load and sort the data using the cached function
data_sorted = load_and_sort_data(dataset_url)

# Add a new column "date" by combining year and month
data_sorted['date'] = pd.to_datetime(data_sorted['anio'].astype(str) + '-' + data_sorted['mes'].astype(str) + '-1')
data_sorted['date'] = pd.to_datetime(data_sorted['date'])

# Filter data_sorted to exclude wells with tef values between 0.01 and 1
data_sorted_filtered = data_sorted[(data_sorted['tef'] == 0) | ((data_sorted['tef'] > 1) | (data_sorted['tef'] < 0.01))]

# Create a Pivot Table to Calculate Maximum Oil and Gas Rates and TEF for Each Well
pivot_table = data_sorted_filtered.pivot_table(
    values=['gas_rate', 'oil_rate', 'water_rate', 'tef'],  # Include 'tef' here
    index=['sigla'],
    aggfunc={'gas_rate': 'max', 'oil_rate': 'max', 'water_rate': 'max', 'tef': 'min'}  # Include 'tef' here
)

# Step 2: Create a New DataFrame with Maximum Oil and Gas Rates and TEF
max_rates_df = pivot_table.reset_index()
max_rates_df['GOR'] = (max_rates_df['gas_rate']*1000) / max_rates_df['oil_rate']
max_rates_df['GOR'] = max_rates_df['GOR'].fillna(100000)

# Add a new column "Fluido McCain" based on conditions
max_rates_df['Fluido McCain'] = max_rates_df.apply(
    lambda row: 'Gas' if row['oil_rate'] == 0 or row['GOR'] > 15000 else 'Petróleo',
    axis=1
)

# Filter max_rates_df to exclude wells with max oil and gas rates above 10,000,000
max_rates_df_filtered = max_rates_df[
    (max_rates_df['oil_rate'] <= 10000000) &
    (max_rates_df['gas_rate'] <= 10000000)
]

# Get the top 10 petroleo wells
top_petroleo_wells = max_rates_df_filtered[max_rates_df_filtered['Fluido McCain'] == 'Petróleo'].nlargest(10, 'oil_rate')

# Get the top 10 gas wells
top_gas_wells = max_rates_df_filtered[max_rates_df_filtered['Fluido McCain'] == 'Gas'].nlargest(10, 'gas_rate')

# Create a bar plot for the top gas wells
st.subheader("Top 10 pozos de gas")
fig_gas = px.bar(top_gas_wells, x='sigla', y='gas_rate', color='sigla', title="Según Caudales máximos de gas")
fig_gas.update_yaxes(title="Caudal de Gas (km3/d)")  # Set y-axis label
st.plotly_chart(fig_gas)

# Create a bar plot for the top petroleo wells
st.subheader("Top 10 pozos de petróleo")
fig_oil = px.bar(top_petroleo_wells, x='sigla', y='oil_rate', color='sigla', title="Según Caudales máximos de petróleo")
fig_oil.update_yaxes(title="Caudal de Petróleo (m3/d)")  # Set y-axis label
st.plotly_chart(fig_oil)

# Aggregate production by company
company_production = data_sorted_filtered.groupby('empresa').agg({
    'prod_pet': 'sum',
    'prod_gas': 'sum',
    'prod_agua': 'sum'
}).reset_index()

# Get the top 10 companies by total production
company_production['total_production'] = company_production[['prod_pet', 'prod_gas', 'prod_agua']].sum(axis=1)
top_companies = company_production.nlargest(10, 'total_production')

# Create a bar plot for the top companies
st.subheader("Top 10 empresas por producción total")
fig_companies = px.bar(top_companies, x='empresa', y='total_production', color='empresa', title="Producción total por empresa")
fig_companies.update_yaxes(title="Producción total (m3 y km3)")
st.plotly_chart(fig_companies)

# Compute correlation matrix
correlation_matrix = data_sorted_filtered[['prod_pet', 'prod_gas', 'prod_agua', 'tef', 'oil_rate', 'gas_rate', 'water_rate']].corr()

# Create a heatmap for the correlation matrix
st.subheader("Mapa de calor de correlaciones")
fig_corr = px.imshow(correlation_matrix, title="Mapa de calor de correlaciones entre métricas de producción")
st.plotly_chart(fig_corr)
