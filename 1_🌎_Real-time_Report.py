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

# Find the last date in the dataset
last_date = data_sorted['date'].max()

# Filter the data for the last date
last_date_data = data_sorted[data_sorted['date'] == last_date]

# Calculate total gas and oil rates for the last date
total_gas_rate = last_date_data['gas_rate'].sum()/1000
total_oil_rate = last_date_data['oil_rate'].sum()/1000

# Convert oil rate to barrels per day (bpd)
oil_rate_bpd = total_oil_rate * 6.28981

# Round the total rates to one decimal place
total_gas_rate_rounded = round(total_gas_rate, 1)
total_oil_rate_rounded = round(total_oil_rate, 1)
oil_rate_bpd_rounded = round(oil_rate_bpd, 1)

# Create Streamlit app layout
st.header(f":blue[Reporte de Producción No Convencional]")

# Display total gas rate and oil rate metrics
col1, col2, col3 = st.columns(3)
col1.metric(label=f":red[Total Caudal de Gas (MMm³/d)]", value=total_gas_rate_rounded)
col2.metric(label=f":green[Total Caudal de Petróleo (km³/d)]", value=total_oil_rate_rounded)
col3.metric(label=f":green[Total Caudal de Petróleo (kbpd)]", value=oil_rate_bpd_rounded)

# Load and preprocess data for plotting
company_summary = data_sorted.groupby(['empresa', 'date']).agg(
    total_gas_rate=('gas_rate', 'sum'),
    total_oil_rate=('oil_rate', 'sum')
).reset_index()

area_summary = data_sorted.groupby(['areayacimiento', 'date']).agg(
    total_gas_rate=('gas_rate', 'sum'),
    total_oil_rate=('oil_rate', 'sum')
).reset_index()

# Determine top 10 companies by total oil production
top_companies = company_summary.groupby('empresa')['total_oil_rate'].sum().nlargest(10).index
company_summary['top_company'] = company_summary['empresa'].apply(lambda x: x if x in top_companies else 'Otros')

# Summarize production data by top companies and "Otros"
top_company_summary = company_summary.groupby(['top_company', 'date']).agg(
    total_gas_rate=('total_gas_rate', 'sum'),
    total_oil_rate=('total_oil_rate', 'sum')
).reset_index()

# Determine top 10 areas by total oil production
top_areas = area_summary.groupby('areayacimiento')['total_oil_rate'].sum().nlargest(10).index
area_summary['top_area'] = area_summary['areayacimiento'].apply(lambda x: x if x in top_areas else 'Otros')

# Summarize production data by top areas and "Otros"
top_area_summary = area_summary.groupby(['top_area', 'date']).agg(
    total_gas_rate=('total_gas_rate', 'sum'),
    total_oil_rate=('total_oil_rate', 'sum')
).reset_index()

# Count wells per company
well_count = data_sorted.groupby('empresa')['sigla'].nunique().reset_index()
well_count.columns = ['empresa', 'well_count']

# Determine top 10 companies by number of wells
top_wells_companies = well_count.nlargest(10, 'well_count')['empresa']
well_count['top_company'] = well_count['empresa'].apply(lambda x: x if x in top_wells_companies else 'Otros')

# Summarize number of wells by top companies and "Otros"
top_well_count = well_count.groupby('top_company')['well_count'].sum().reset_index()

# Group data by year for stacked area plots
year_summary = data_sorted.groupby(['anio', 'date']).agg(
    total_gas_rate=('gas_rate', 'sum'),
    total_oil_rate=('oil_rate', 'sum')
).reset_index()

# Filter data for the last year
last_year = data_sorted['anio'].max()
last_year_wells_count = well_count[well_count['empresa'].isin(top_wells_companies) | (well_count['top_company'] == 'Otros')]


image = Image.open('Vaca Muerta rig.png')
st.sidebar.image(image)
st.sidebar.title("Por favor filtrar aquí:")

# Area plots for gas and oil rates by top 10 companies (non-stacked)
st.subheader("Caudal de Gas y Petróleo por Empresa")

# Plot for gas rate by company (non-stacked)
fig_gas_company = px.area(top_company_summary, x='date', y='total_gas_rate', color='top_company', title="Caudal de Gas por Empresa", line_group='top_company')
fig_gas_company.update_layout(
    legend_title_text='Empresa',
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
    yaxis_title="Caudal de Gas (m³/d)"
)
st.plotly_chart(fig_gas_company, use_container_width=True)

# Summary table for gas rate by company
st.write("Resumen de producción de gas por empresa:")
st.write(top_company_summary.groupby('top_company').agg(total_gas_rate=('total_gas_rate', 'sum')).reset_index())

# Plot for oil rate by company (non-stacked)
fig_oil_company = px.area(top_company_summary, x='date', y='total_oil_rate', color='top_company', title="Caudal de Petróleo por Empresa", line_group='top_company')
fig_oil_company.update_layout(
    legend_title_text='Empresa',
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
st.plotly_chart(fig_oil_company, use_container_width=True)

# Summary table for oil rate by company
st.write("Resumen de producción de petróleo por empresa:")
st.write(top_company_summary.groupby('top_company').agg(total_oil_rate=('total_oil_rate', 'sum')).reset_index())

# Area plots for gas and oil rates by top 10 areas
st.subheader("Caudal de Gas y Petróleo por Área de Yacimiento")

# Plot for gas rate by area
fig_gas_area = px.area(top_area_summary, x='date', y='total_gas_rate', color='top_area', title="Caudal de Gas por Área de Yacimiento")
fig_gas_area.update_layout(
    legend_title_text='Área de Yacimiento',
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
    yaxis_title="Caudal de Gas (m³/d)"
)
st.plotly_chart(fig_gas_area, use_container_width=True)

# Summary table for gas rate by area
st.write("Resumen de producción de gas por área de yacimiento:")
st.write(top_area_summary.groupby('top_area').agg(total_gas_rate=('total_gas_rate', 'sum')).reset_index())

# Plot for oil rate by area
fig_oil_area = px.area(top_area_summary, x='date', y='total_oil_rate', color='top_area', title="Caudal de Petróleo por Área de Yacimiento")
fig_oil_area.update_layout(
    legend_title_text='Área de Yacimiento',
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
st.plotly_chart(fig_oil_area, use_container_width=True)

# Summary table for oil rate by area
st.write("Resumen de producción de petróleo por área de yacimiento:")
st.write(top_area_summary.groupby('top_area').agg(total_oil_rate=('total_oil_rate', 'sum')).reset_index())

# Bar plot of the number of wells per company
st.subheader("Número de Pozos por Empresa")

fig_wells = px.bar(top_well_count, x='top_company', y='well_count', title="Número de Pozos por Empresa", text='well_count')
fig_wells.update_layout(
    xaxis_title="Empresa",
    yaxis_title="Número de Pozos",
    xaxis_tickangle=-45
)
st.plotly_chart(fig_wells, use_container_width=True)

# Summary table for number of wells
st.write("Resumen de número de pozos por empresa:")
st.write(top_well_count)

# Area plots for gas and oil rates by year
st.subheader("Caudal de Gas y Petróleo por Año")

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
    yaxis_title="Caudal de Gas (m³/d)"
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

# Display table for number of wells per company in the last year
st.subheader(f"Número de Pozos por Empresa ({last_year})")

st.write(last_year_wells_count)

# Option to download the filtered data
csv = data_sorted.to_csv(index=False)
st.sidebar.download_button(
    label="Descargar datos",
    data=csv,
    file_name='filtered_data.csv',
    mime='text/csv',
)
