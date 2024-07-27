import streamlit as st
import pandas as pd
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

# Determine top 10 companies by total oil production
top_companies = company_summary.groupby('empresa')['total_oil_rate'].sum().nlargest(10).index
company_summary['top_company'] = company_summary['empresa'].apply(lambda x: x if x in top_companies else 'Other')

# Summarize production data by top companies and "Other"
top_company_summary = company_summary.groupby(['top_company', 'date']).agg(
    total_gas_rate=('total_gas_rate', 'sum'),
    total_oil_rate=('total_oil_rate', 'sum')
).reset_index()

# Determine top 10 areas by total oil production
top_areas = area_summary.groupby('areayacimiento')['total_oil_rate'].sum().nlargest(10).index
area_summary['top_area'] = area_summary['areayacimiento'].apply(lambda x: x if x in top_areas else 'Other')

# Summarize production data by top areas and "Other"
top_area_summary = area_summary.groupby(['top_area', 'date']).agg(
    total_gas_rate=('total_gas_rate', 'sum'),
    total_oil_rate=('total_oil_rate', 'sum')
).reset_index()

# Count wells per company
well_count = data_sorted.groupby('empresa')['sigla'].nunique().reset_index()
well_count.columns = ['empresa', 'well_count']

# Determine top 10 companies by number of wells
top_wells_companies = well_count.nlargest(10, 'well_count')['empresa']
well_count['top_company'] = well_count['empresa'].apply(lambda x: x if x in top_wells_companies else 'Other')

# Summarize number of wells by top companies and "Other"
top_well_count = well_count.groupby('top_company')['well_count'].sum().reset_index()

# Group data by year for stacked area plots
year_summary = data_sorted.groupby(['anio', 'date']).agg(
    total_gas_rate=('gas_rate', 'sum'),
    total_oil_rate=('oil_rate', 'sum')
).reset_index()

# Filter data for the last year
last_year = data_sorted['anio'].max()
last_year_wells_count = well_count[well_count['empresa'].isin(top_wells_companies) | (well_count['top_company'] == 'Other')]

# Create Streamlit app layout
st.header(f":blue[Reporte de Producción No Convencional]")

image = Image.open('Vaca Muerta rig.png')
st.sidebar.image(image)
st.sidebar.title("Por favor filtrar aquí:")

# Area plots for gas and oil rates by top 10 companies
st.subheader("Caudal de Gas y Petróleo por Empresa (Top 10 y Otros)")

fig_gas_company = px.area(top_company_summary, x='date', y='total_gas_rate', color='top_company', title="Caudal de Gas por Empresa")
fig_gas_company.update_layout(
    legend_title_text='Empresa',
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=-0.3,  # Adjust this value as needed
        xanchor="center",
        x=0.5
    )
)
st.plotly_chart(fig_gas_company, use_container_width=True)

fig_oil_company = px.area(top_company_summary, x='date', y='total_oil_rate', color='top_company', title="Caudal de Petróleo por Empresa")
fig_oil_company.update_layout(
    legend_title_text='Empresa',
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=-0.3,  # Adjust this value as needed
        xanchor="center",
        x=0.5
    )
)
st.plotly_chart(fig_oil_company, use_container_width=True)

# Area plots for gas and oil rates by top 10 areas
st.subheader("Caudal de Gas y Petróleo por Área de Yacimiento (Top 10 y Otros)")

fig_gas_area = px.area(top_area_summary, x='date', y='total_gas_rate', color='top_area', title="Caudal de Gas por Área de Yacimiento")
fig_gas_area.update_layout(
    legend_title_text='Área de Yacimiento',
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=-0.3,  # Adjust this value as needed
        xanchor="center",
        x=0.5
    )
)
st.plotly_chart(fig_gas_area, use_container_width=True)

fig_oil_area = px.area(top_area_summary, x='date', y='total_oil_rate', color='top_area', title="Caudal de Petróleo por Área de Yacimiento")
fig_oil_area.update_layout(
    legend_title_text='Área de Yacimiento',
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=-0.3,  # Adjust this value as needed
        xanchor="center",
        x=0.5
    )
)
st.plotly_chart(fig_oil_area, use_container_width=True)

# Bar plot for number of wells per top 10 companies
st.subheader("Número de Pozos por Empresa (Top 10 y Otros)")

fig_well_count = px.bar(top_well_count, x='top_company', y='well_count', title="Número de Pozos por Empresa")
fig_well_count.update_layout(
    xaxis_title="Empresa",
    yaxis_title="Número de Pozos",
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=-0.3,  # Adjust this value as needed
        xanchor="center",
        x=0.5
    )
)
st.plotly_chart(fig_well_count, use_container_width=True)

# Stacked area plots for gas and oil rates by year
st.subheader("Caudal de Gas y Petróleo por Año")

fig_gas_year = px.area(year_summary, x='date', y='total_gas_rate', color='anio', title="Caudal de Gas por Año")
fig_gas_year.update_layout(
    legend_title_text='Año',
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=-0.3,  # Adjust this value as needed
        xanchor="center",
        x=0.5
    )
)
st.plotly_chart(fig_gas_year, use_container_width=True)

fig_oil_year = px.area(year_summary, x='date', y='total_oil_rate', color='anio', title="Caudal de Petróleo por Año")
fig_oil_year.update_layout(
    legend_title_text='Año',
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=-0.3,  # Adjust this value as needed
        xanchor="center",
        x=0.5
    )
)
st.plotly_chart(fig_oil_year, use_container_width=True)

# Display table for number of wells per company in the last year
st.subheader(f"Número de Pozos por Empresa ({last_year})")

last_year_wells_count = last_year_wells_count[last_year_wells_count['empresa'].isin(top_wells_companies) | (last_year_wells_count['top_company'] == 'Other')]
st.write(last_year_wells_count)

# Option to download the filtered data
csv = data_sorted.to_csv(index=False)
st.sidebar.download_button(
    label="Descargar datos",
    data=csv,
    file_name='filtered_data.csv',
    mime='text/csv',
)
