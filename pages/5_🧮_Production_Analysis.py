import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from PIL import Image
import plotly.express as px

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

# Load and sort the data
@st.cache_data
def load_and_sort_data(dataset_url):
    df = pd.read_csv(dataset_url, usecols=COLUMNS)
    df['date'] = pd.to_datetime(df['anio'].astype(str) + '-' + df['mes'].astype(str) + '-1')
    df['gas_rate'] = df['prod_gas'] / df['tef']
    df['oil_rate'] = df['prod_pet'] / df['tef']
    data_sorted = df.sort_values(by=['sigla', 'fecha_data'], ascending=True)
    return data_sorted

# URL of the dataset
dataset_url = "http://datos.energia.gob.ar/dataset/c846e79c-026c-4040-897f-1ad3543b407c/resource/b5b58cdc-9e07-41f9-b392-fb9ec68b0725/download/produccin-de-pozos-de-gas-y-petrleo-no-convencional.csv"

# Load and sort the data using the cached function
data_sorted = load_and_sort_data(dataset_url)

# Sidebar filters
st.header(f":blue[Análisis de Producción No Convencional]")
image = Image.open('Vaca Muerta rig.png')
st.sidebar.image(image)
st.sidebar.title("Por favor filtrar aquí:")

# Create a multiselect menu for companies
selected_companies = st.sidebar.multiselect(
    "Seleccione las empresas",
    options=data_sorted['empresa'].unique(),
    default=data_sorted['empresa'].unique()
)

# Create a dropdown menu for year
selected_year = st.sidebar.selectbox(
    "Seleccione el año",
    options=data_sorted['anio'].unique()
)

# Filter data based on the selected companies and year
filtered_data = data_sorted[
    (data_sorted['empresa'].isin(selected_companies)) & 
    (data_sorted['anio'] == selected_year)
]

# Summarize production data by company
summary_df = filtered_data.groupby(['empresa', 'date']).agg(
    total_gas_rate=('gas_rate', 'sum'),
    total_oil_rate=('oil_rate', 'sum')
).reset_index()

# Plot total oil production by company over time using area plot
oil_rate_fig = go.Figure()

color_palette = px.colors.qualitative.Set3  # Use a distinct color palette

for i, company in enumerate(summary_df['empresa'].unique()):
    company_data = summary_df[summary_df['empresa'] == company]
    oil_rate_fig.add_trace(
        go.Scatter(
            x=company_data['date'],
            y=company_data['total_oil_rate'],
            mode='lines',
            name=f'{company} - Oil Rate',
            fill='tonexty',
            line=dict(color=color_palette[i % len(color_palette)]),
            hovertemplate='Fecha: %{x}<br>Caudal de Petróleo: %{y:.2f} m3/d'
        )
    )

oil_rate_fig.update_layout(
    title="Producción Total de Petróleo por Empresa",
    xaxis_title="Fecha",
    yaxis_title="Caudal de Petróleo (m3/d)",
    hovermode='x unified',
    legend_title="Empresa"
)

# Display the oil production plot
st.plotly_chart(oil_rate_fig, use_container_width=True)

# Plot total gas production by company over time using area plot
gas_rate_fig = go.Figure()

for i, company in enumerate(summary_df['empresa'].unique()):
    company_data = summary_df[summary_df['empresa'] == company]
    gas_rate_fig.add_trace(
        go.Scatter(
            x=company_data['date'],
            y=company_data['total_gas_rate'],
            mode='lines',
            name=f'{company} - Gas Rate',
            fill='tonexty',
            line=dict(color=color_palette[i % len(color_palette)]),
            hovertemplate='Fecha: %{x}<br>Caudal de Gas: %{y:.2f} km3/d'
        )
    )

gas_rate_fig.update_layout(
    title="Producción Total de Gas por Empresa",
    xaxis_title="Fecha",
    yaxis_title="Caudal de Gas (km3/d)",
    hovermode='x unified',
    legend_title="Empresa"
)

# Display the gas production plot
st.plotly_chart(gas_rate_fig, use_container_width=True)

# Identify top 10 wells for gas and oil based on the maximum production rates for the selected companies and year
top_10_gas_wells = filtered_data.sort_values(by='gas_rate', ascending=False).head(10)['sigla'].unique()
top_10_oil_wells = filtered_data.sort_values(by='oil_rate', ascending=False).head(10)['sigla'].unique()

# Plot top 10 wells production profile for gas
top_gas_fig = go.Figure()

for i, well in enumerate(top_10_gas_wells):
    well_data = filtered_data[filtered_data['sigla'] == well]
    top_gas_fig.add_trace(
        go.Scatter(
            x=well_data['date'],
            y=well_data['gas_rate'],
            mode='lines+markers',
            name=f'{well} - Gas Rate',
            line=dict(color=color_palette[i % len(color_palette)]),
            hovertemplate='Fecha: %{x}<br>Caudal de Gas: %{y:.2f} km3/d'
        )
    )

top_gas_fig.update_layout(
    title=f"Top 10 Pozos por Perfil de Producción de Gas en {selected_year}",
    xaxis_title="Fecha",
    yaxis_title="Caudal de Gas (km3/d)",
    hovermode='x unified',
    legend_title="Pozos"
)

# Display the top 10 wells gas production plot
st.plotly_chart(top_gas_fig, use_container_width=True)

# Plot top 10 wells production profile for oil
top_oil_fig = go.Figure()

for i, well in enumerate(top_10_oil_wells):
    well_data = filtered_data[filtered_data['sigla'] == well]
    top_oil_fig.add_trace(
        go.Scatter(
            x=well_data['date'],
            y=well_data['oil_rate'],
            mode='lines+markers',
            name=f'{well} - Oil Rate',
            line=dict(color=color_palette[i % len(color_palette)]),
            hovertemplate='Fecha: %{x}<br>Caudal de Petróleo: %{y:.2f} m3/d'
        )
    )

top_oil_fig.update_layout(
    title=f"Top 10 Pozos por Perfil de Producción de Petróleo en {selected_year}",
    xaxis_title="Fecha",
    yaxis_title="Caudal de Petróleo (m3/d)",
    hovermode='x unified',
    legend_title="Pozos"
)

# Display the top 10 wells oil production plot
st.plotly_chart(top_oil_fig, use_container_width=True)

# Option to download the filtered data
csv = filtered_data.to_csv(index=False)
st.sidebar.download_button(
    label="Descargar datos filtrados",
    data=csv,
    file_name='filtered_data.csv',
    mime='text/csv',
)

# Optionally add plot smoothing
st.sidebar.title("Opciones de Suavizado")
smoothing = st.sidebar.checkbox("Activar suavizado de la curva")
if smoothing:
    from scipy.ndimage import gaussian_filter1d
    
    oil_rate_fig_smooth = go.Figure()
    gas_rate_fig_smooth = go.Figure()
    
    for i, company in enumerate(summary_df['empresa'].unique()):
        company_data = summary_df[summary_df['empresa'] == company]
        oil_rate_fig_smooth.add_trace(
            go.Scatter(
                x=company_data['date'],
                y=gaussian_filter1d(company_data['total_oil_rate'], sigma=2),
                mode='lines',
                name=f'{company} - Oil Rate (Suavizado)',
                fill='tonexty',
                line=dict(color=color_palette[i % len(color_palette)]),
                hovertemplate='Fecha: %{x}<br>Caudal de Petróleo: %{y:.2f} m3/d'
            )
        )
        gas_rate_fig_smooth.add_trace(
            go.Scatter(
                x=company_data['date'],
                y=gaussian_filter1d(company_data['total_gas_rate'], sigma=2),
                mode='lines',
                name=f'{company} - Gas Rate (Suavizado)',
                fill='tonexty',
                line=dict(color=color_palette[i % len(color_palette)]),
                hovertemplate='Fecha: %{x}<br>Caudal de Gas: %{y:.2f} km3/d'
            )
        )
    
    oil_rate_fig_smooth.update_layout(
        title="Producción Total de Petróleo por Empresa (Suavizado)",
        xaxis_title="Fecha",
        yaxis_title="Caudal de Petróleo (m3/d)",
        hovermode='x unified',
        legend_title="Empresa"
    )
    gas_rate_fig_smooth.update_layout(
        title="Producción Total de Gas por Empresa (Suavizado)",
        xaxis_title="Fecha",
        yaxis_title="Caudal de Gas (km3/d)",
        hovermode='x unified',
        legend_title="Empresa"
    )
    
    st.plotly_chart(oil_rate_fig_smooth, use_container_width=True)
    st.plotly_chart(gas_rate_fig_smooth, use_container_width=True)
