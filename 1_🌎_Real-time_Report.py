import streamlit as st
import pandas as pd
import plotly.express as px
from PIL import Image

# Load and preprocess the data
@st.cache_data
def load_and_sort_data(dataset_url):
    try:
        df = pd.read_csv(dataset_url, usecols=[
            'sigla', 'anio', 'mes', 'prod_pet', 'prod_gas', 'tef', 'empresa', 'areayacimiento', 'fecha_data'
        ])
        df['date'] = pd.to_datetime(df['anio'].astype(str) + '-' + df['mes'].astype(str) + '-1')
        df['gas_rate'] = df['prod_gas'] / df['tef']
        df['oil_rate'] = df['prod_pet'] / df['tef']
        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame()  # Return an empty DataFrame in case of error

# URL of the dataset
dataset_url = "http://datos.energia.gob.ar/dataset/c846e79c-026c-4040-897f-1ad3543b407c/resource/b5b58cdc-9e07-41f9-b392-fb9ec68b0725/download/produccin-de-pozos-de-gas-y-petrleo-no-convencional.csv"

# Load the data
data_sorted = load_and_sort_data(dataset_url)

if data_sorted.empty:
    st.stop()  # Stop execution if data failed to load

# Filter out rows where tef is zero for calculating metrics
data_filtered = data_sorted[data_sorted['tef'] > 0]

# Find the latest date in the dataset
latest_date = data_filtered['date'].max()

# Filter the dataset to include only rows from the latest date
latest_data = data_filtered[data_filtered['date'] == latest_date]

# Calculate total gas and oil rates for the latest date
total_gas_rate = latest_data['gas_rate'].sum()
total_oil_rate = latest_data['oil_rate'].sum()

# Convert oil rate to barrels per day (bpd)
oil_rate_bpd = total_oil_rate * 6.28981

# Round the total rates to one decimal place
total_gas_rate_rounded = round(total_gas_rate, 1)
total_oil_rate_rounded = round(total_oil_rate, 1)
oil_rate_bpd_rounded = round(oil_rate_bpd, 1)

# Count wells per company
well_count = data_sorted.groupby('empresa')['sigla'].nunique().reset_index()
well_count.columns = ['empresa', 'well_count']

# Determine top 10 companies by number of wells
top_wells_companies = well_count.nlargest(10, 'well_count')['empresa']

# Filter well_count to include only top companies
well_count_top = well_count[well_count['empresa'].isin(top_wells_companies)]

# Group data by year for stacked area plots
year_summary = data_sorted.groupby(['anio', 'date']).agg(
    total_gas_rate=('gas_rate', 'sum'),
    total_oil_rate=('oil_rate', 'sum')
).reset_index()

# Create Streamlit app layout
st.header(":blue[Reporte de Producción No Convencional]")

image = Image.open('Vaca Muerta rig.png')
st.sidebar.image(image)
st.sidebar.title("Por favor filtrar aquí:")

# Display total gas rate and oil rate metrics
col1, col2, col3 = st.columns(3)
col1.metric(label=":red[Total Caudal de Gas (km³/d)]", value=total_gas_rate_rounded)
col2.metric(label=":green[Total Caudal de Petróleo (m³/d)]", value=total_oil_rate_rounded)
col3.metric(label=":green[Total Caudal de Petróleo (bpd)]", value=oil_rate_bpd_rounded)

# Bar plot of the number of wells per company
st.subheader("Número de Pozos por Empresa")

fig_wells = px.bar(well_count_top, x='empresa', y='well_count', color='empresa', title="Número de Pozos")
fig_wells.update_layout(
    showlegend=False,
    xaxis_title="Empresa",
    yaxis_title="Número de Pozos",
    xaxis_tickangle=-45
)
st.plotly_chart(fig_wells, use_container_width=True)

# Area plots for gas and oil rates by year
st.subheader("Producción por Año")

# Plot for gas rate by year
fig_gas_year = px.area(year_summary, x='date', y='total_gas_rate', color='anio', title="Caudal de Gas por Año")
fig_gas_year.update_layout(
    legend_title_text='Año',
    legend=dict(
        orientation="h",
        yanchor="top",
        y=-0.3,  # Adjust this value to avoid overlapping
        xanchor="center",
        x=0.5,
        font=dict(size=10)  # Adjust the font size to fit the space
    ),
    margin=dict(b=100),  # Increase the bottom margin to make space for the legend
    xaxis_title="Fecha",
    yaxis_title="Caudal de Gas (km³/d)"
)
st.plotly_chart(fig_gas_year, use_container_width=True)

# Plot for oil rate by year
fig_oil_year = px.area(year_summary, x='date', y='total_oil_rate', color='anio', title="Caudal de Petróleo por Año")
fig_oil_year.update_layout(
    legend_title_text='Año',
    legend=dict(
        orientation="h",
        yanchor="top",
        y=-0.3,  # Adjust this value to avoid overlapping
        xanchor="center",
        x=0.5,
        font=dict(size=10)  # Adjust the font size to fit the space
    ),
    margin=dict(b=100),  # Increase the bottom margin to make space for the legend
    xaxis_title="Fecha",
    yaxis_title="Caudal de Petróleo (m³/d)"
)
st.plotly_chart(fig_oil_year, use_container_width=True)

# Option to download the filtered data
csv = data_sorted.to_csv(index=False)
st.sidebar.download_button(
    label="Descargar datos",
    data=csv,
    file_name='filtered_data.csv',
    mime='text/csv',
)
