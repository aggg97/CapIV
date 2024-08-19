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
total_gas_rate = latest_data['gas_rate'].sum()/1000
total_oil_rate = latest_data['oil_rate'].sum()/1000

# Convert oil rate to barrels per day (bpd)
oil_rate_bpd = total_oil_rate * 6.28981

# Round the total rates to one decimal place
total_gas_rate_rounded = round(total_gas_rate, 1)
total_oil_rate_rounded = round(total_oil_rate, 1)
oil_rate_bpd_rounded = round(oil_rate_bpd, 1)

# Load and preprocess data for plotting
company_summary = data_sorted.groupby(['empresa', 'date']).agg(
    total_gas_rate=('gas_rate', 'sum'),
    total_oil_rate=('oil_rate', 'sum')
).reset_index()

# Determine top 10 companies by total oil production
top_companies = company_summary.groupby('empresa')['total_oil_rate'].sum().nlargest(10).index

# Aggregate data for top companies and "Others"
company_summary['empresa'] = company_summary['empresa'].apply(lambda x: x if x in top_companies else 'Others')
company_summary_aggregated = company_summary.groupby(['empresa', 'date']).agg(
    total_gas_rate=('total_gas_rate', 'sum'),
    total_oil_rate=('total_oil_rate', 'sum')
).reset_index()

# Count wells per company
well_count = data_sorted.groupby('empresa')['sigla'].nunique().reset_index()
well_count.columns = ['empresa', 'well_count']

# Determine top 10 companies by number of wells
top_wells_companies = well_count.nlargest(10, 'well_count')['empresa']

# Filter well_count to include only top companies
well_count_top = well_count[well_count['empresa'].isin(top_wells_companies)]

# Filter the dataset to include only rows where the gas rate is not null
non_null_gas_data = data_sorted[data_sorted['gas_rate'] > 0]

# Determine the starting year for each well based on the first non-null gas rate
well_start_year = non_null_gas_data.groupby('sigla')['anio'].min().reset_index()
well_start_year.columns = ['sigla', 'start_year']

# Merge the start year back to the original data
data_with_start_year = pd.merge(data_sorted, well_start_year, on='sigla')

# Group data by start year and date for area plots
yearly_summary = data_with_start_year.groupby(['start_year', 'date']).agg(
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
col1.metric(label=":red[Total Caudal de Gas (MMm³/d)]", value=total_gas_rate_rounded)
col2.metric(label=":green[Total Caudal de Petróleo (km³/d)]", value=total_oil_rate_rounded)
col3.metric(label=":green[Total Caudal de Petróleo (kbpd)]", value=oil_rate_bpd_rounded)

# Area plots for gas and oil rates by top 10 companies + Others
st.subheader("Actividad de las principales empresas")

# Plot for gas rate by company
fig_gas_company = px.area(company_summary_aggregated, x='date', y='total_gas_rate', color='empresa', title="Caudal de Gas por Empresa")
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
    yaxis_title="Caudal de Gas (km³/d)"
)
st.plotly_chart(fig_gas_company, use_container_width=True)

# Plot for oil rate by company
fig_oil_company = px.area(company_summary_aggregated, x='date', y='total_oil_rate', color='empresa', title="Caudal de Petróleo por Empresa")
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

# Treemap for the number of wells per company
st.subheader("Número de Pozos por Empresa")

fig_wells = px.treemap(well_count_top, path=['empresa'], values='well_count', title="Número de Pozos")
fig_wells.update_layout(
    treemapcolorway=['#636EFA', '#EF553B', '#00CC96', '#AB63FA', '#FFA15A', '#19D3F3', '#FF6692', '#B6E880', '#FF97FF', '#FECB52'],
    margin=dict(t=50, l=25, r=25, b=25)
)
st.plotly_chart(fig_wells, use_container_width=True)

# Area plots for gas and oil rates by well start year
st.subheader("Producción por Año de Inicio de Pozo")

# Plot for gas rate by start year
fig_gas_year = px.area(yearly_summary, x='date', y='total_gas_rate', color='start_year', title="Caudal de Gas por Año de Inicio de Pozo")
fig_gas_year.update_layout(
    legend_title_text='Año de Inicio de Pozo',
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

# Plot for oil rate by start year
fig_oil_year = px.area(yearly_summary, x='date', y='total_oil_rate', color='start_year', title="Caudal de Petróleo por Año de Inicio de Pozo")
fig_oil_year.update_layout(
    legend_title_text='Año de Inicio de Pozo',
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
