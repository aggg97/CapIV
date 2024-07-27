import streamlit as st
import pandas as pd
import plotly.express as px
from PIL import Image

# Define the columns for the dataset
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

# Define the column names for the dataset
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

# Load and sort the data
@st.cache(allow_output_mutation=True)
def load_and_sort_data(dataset_url):
    df = pd.read_csv(dataset_url, usecols=COLUMNS)
    data_sorted = df.sort_values(by=['sigla', 'fecha_data'], ascending=True)
    data_sorted = data_sorted[COLUMNS]
    return data_sorted

# URL of the dataset
dataset_url = "http://datos.energia.gob.ar/dataset/c846e79c-026c-4040-897f-1ad3543b407c/resource/b5b58cdc-9e07-41f9-b392-fb9ec68b0725/download/produccin-de-pozos-de-gas-y-petrleo-no-convencional.csv"

# Load and sort the data using the cached function
data_sorted = load_and_sort_data(dataset_url)

# Add a new column "date" by combining year and month
data_sorted['date'] = pd.to_datetime(data_sorted['anio'].astype(str) + '-' + data_sorted['mes'].astype(str) + '-1')

# Summarize production data by company and block
summary_df = data_sorted.groupby(['empresa', 'areayacimiento', 'date']).agg(
    total_prod_pet=('prod_pet', 'sum'),
    total_prod_gas=('prod_gas', 'sum')
).reset_index()

# Sidebar filters
st.header(f":blue[Análisis de Producción No Convencional]")
image = Image.open('Vaca Muerta rig.png')
st.sidebar.image(image)
st.sidebar.title("Por favor filtrar aquí:")

# Create a multiselect list for companies
selected_companies = st.sidebar.multiselect("Seleccionar empresas", summary_df['empresa'].unique())

# Create a multiselect list for blocks
selected_blocks = st.sidebar.multiselect("Seleccionar áreas de yacimiento", summary_df['areayacimiento'].unique())

# Filter data based on selections
filtered_data = summary_df[
    (summary_df['empresa'].isin(selected_companies)) & 
    (summary_df['areayacimiento'].isin(selected_blocks))
]

# Plot total oil production by company and block over time
oil_fig = px.line(
    filtered_data, 
    x='date', 
    y='total_prod_pet', 
    color='empresa',
    line_group='areayacimiento',
    title="Producción Total de Petróleo por Empresa y Área de Yacimiento",
    labels={"total_prod_pet": "Producción de Petróleo (m3)"}
)

# Display the oil production plot
st.plotly_chart(oil_fig)

# Plot total gas production by company and block over time
gas_fig = px.line(
    filtered_data, 
    x='date', 
    y='total_prod_gas', 
    color='empresa',
    line_group='areayacimiento',
    title="Producción Total de Gas por Empresa y Área de Yacimiento",
    labels={"total_prod_gas": "Producción de Gas (km3)"}
)

# Display the gas production plot
st.plotly_chart(gas_fig)
