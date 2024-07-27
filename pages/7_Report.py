import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from PIL import Image

# Load and preprocess the data
@st.cache_data
def load_and_sort_data(dataset_url):
    df = pd.read_csv(dataset_url, usecols=[
        'sigla', 'anio', 'mes', 'prod_pet', 'prod_gas', 'tef', 'empresa', 'areayacimiento', 'fecha_data'
    ])
    df['date'] = pd.to_datetime(df['anio'].astype(str) + '-' + df['mes'].astype(str) + '-1')
    df['gas_rate'] = df['prod_gas'] / df['tef']
    df['oil_rate'] = df['prod_pet'] / df['tef']
    return df

# URL of the dataset
dataset_url = "http://datos.energia.gob.ar/dataset/c846e79c-026c-4040-897f-1ad3543b407c/resource/b5b58cdc-9e07-41f9-b392-fb9ec68b0725/download/produccin-de-pozos-de-gas-y-petrleo-no-convencional.csv"

# Load the data
data_sorted = load_and_sort_data(dataset_url)

# Group data by company and date
company_summary = data_sorted.groupby(['empresa', 'date']).agg(
    total_gas_rate=('gas_rate', 'sum'),
    total_oil_rate=('oil_rate', 'sum')
).reset_index()

# Group data by area and date
area_summary = data_sorted.groupby(['areayacimiento', 'date']).agg(
    total_gas_rate=('gas_rate', 'sum'),
    total_oil_rate=('oil_rate', 'sum')
).reset_index()

# Determine top 5 areas by total oil production
top_areas = area_summary.groupby('areayacimiento')['total_oil_rate'].sum().nlargest(5).index
area_summary['top_area'] = area_summary['areayacimiento'].apply(lambda x: x if x in top_areas else 'Other')

# Summarize production data by top areas and "Other"
top_area_summary = area_summary.groupby(['top_area', 'date']).agg(
    total_gas_rate=('total_gas_rate', 'sum'),
    total_oil_rate=('total_oil_rate', 'sum')
).reset_index()

# Count wells per company
well_count = data_sorted.groupby('empresa')['sigla'].nunique().reset_index()
well_count.columns = ['empresa', 'well_count']

# Group data by year for stacked area plots
year_summary = data_sorted.groupby(['anio', 'date']).agg(
    total_gas_rate=('gas_rate', 'sum'),
    total_oil_rate=('oil_rate', 'sum')
).reset_index()

# Create Streamlit app layout
st.header(f":blue[Reporte de Producción No Convencional]")

image = Image.open('Vaca Muerta rig.png')
st.sidebar.image(image)
st.sidebar.title("Por favor filtrar aquí:")

# Area plots for gas and oil rates by company
st.subheader("Caudal de Gas y Petróleo por Empresa")

fig_gas_company = px.area(company_summary, x='date', y='total_gas_rate', color='empresa', title="Caudal de Gas por Empresa")
st.plotly_chart(fig_gas_company, use_container_width=True)

fig_oil_company = px.area(company_summary, x='date', y='total_oil_rate', color='empresa', title="Caudal de Petróleo por Empresa")
st.plotly_chart(fig_oil_company, use_container_width=True)

# Area plots for gas and oil rates by top areas
st.subheader("Caudal de Gas y Petróleo por Área de Yacimiento")

fig_gas_area = px.area(top_area_summary, x='date', y='total_gas_rate', color='top_area', title="Caudal de Gas por Área de Yacimiento")
st.plotly_chart(fig_gas_area, use_container_width=True)

fig_oil_area = px.area(top_area_summary, x='date', y='total_oil_rate', color='top_area', title="Caudal de Petróleo por Área de Yacimiento")
st.plotly_chart(fig_oil_area, use_container_width=True)

# Bar plot for number of wells per company
st.subheader("Número de Pozos por Empresa")

fig_well_count = px.bar(well_count, x='empresa', y='well_count', title="Número de Pozos por Empresa")
st.plotly_chart(fig_well_count, use_container_width=True)

# Stacked area plots for gas and oil rates by year
st.subheader("Caudal de Gas y Petróleo por Año")

fig_gas_year = px.area(year_summary, x='date', y='total_gas_rate', color='anio', title="Caudal de Gas por Año")
st.plotly_chart(fig_gas_year, use_container_width=True)

fig_oil_year = px.area(year_summary, x='date', y='total_oil_rate', color='anio', title="Caudal de Petróleo por Año")
st.plotly_chart(fig_oil_year, use_container_width=True)

# Option to download the filtered data
csv = data_sorted.to_csv(index=False)
st.sidebar.download_button(
    label="Descargar datos",
    data=csv,
    file_name='filtered_data.csv',
    mime='text/csv',
)

