import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from PIL import Image

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
@st.cache(allow_output_mutation=True)
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

# URL of the dataset
dataset_url = "http://datos.energia.gob.ar/dataset/c846e79c-026c-4040-897f-1ad3543b407c/resource/b5b58cdc-9e07-41f9-b392-fb9ec68b0725/download/produccin-de-pozos-de-gas-y-petrleo-no-convencional.csv"

# Load and sort the data using the cached function
data_sorted = load_and_sort_data(dataset_url)

# Add a new column "date" by combining year and month
data_sorted['date'] = pd.to_datetime(data_sorted['anio'].astype(str) + '-' + data_sorted['mes'].astype(str) + '-1')
data_sorted['date'] = pd.to_datetime(data_sorted['date'])

# Create a Pivot Table to Calculate Maximum Oil and Gas Rates for Each Well
pivot_table = data_sorted.pivot_table(
    values=['gas_rate', 'oil_rate', 'water_rate'],
    index=['sigla'],
    aggfunc={'gas_rate': 'max', 'oil_rate': 'max', 'water_rate': 'max'}
)

# Step 2: Create a New DataFrame with Maximum Oil and Gas Rates
max_rates_df = pivot_table.reset_index()
max_rates_df['GOR'] = max_rates_df['gas_rate'] / max_rates_df['oil_rate']
max_rates_df['GOR'] = max_rates_df['GOR'].fillna(100000)

# Add a new column "Fluido McCain" based on conditions
max_rates_df['Fluido McCain'] = max_rates_df.apply(
    lambda row: 'Gas' if row['oil_rate'] == 0 or row['GOR'] > 3000 else 'Petróleo',
    axis=1
)

st.header(f":blue[Capítulo IV Dataset - Producción No Convencional]")
image = Image.open('Vaca Muerta rig.png')
st.sidebar.image(image)
st.sidebar.title("Por favor filtrar aquí: ")

# Create a dropdown list for "Fluido McCain"
selected_fluido = st.sidebar.selectbox("Seleccionar tipo de fluido según McCain:", max_rates_df['Fluido McCain'].unique())

# Get unique years from the dataset and sort them in decreasing order
unique_years = sorted(data_sorted['anio'].unique(), reverse=True)

# Create a multiselect list for 'anio' (years) in decreasing order
selected_years = st.sidebar.multiselect("Seleccionar año", unique_years)

# Filter data based on selected years
filtered_data_by_year = data_sorted[data_sorted['anio'].isin(selected_years)]

# Filter wells where the first value of Np different from zero appears on the selected year
wells_with_non_zero_Np = filtered_data_by_year.groupby('sigla')['Np'].transform('idxmax')
filtered_data_by_year = filtered_data_by_year.loc[wells_with_non_zero_Np]

# Get unique wells (sigla) based on the filtered data
unique_wells_filtered_by_year = filtered_data_by_year['sigla'].unique()

# Create a multiselect list for 'sigla' based on the filtered wells
selected_sigla_filtered_by_year = st.sidebar.multiselect("Seleccionar siglas de los pozos a comparar (Filtrados por año)", unique_wells_filtered_by_year)

# Filter data for matching 'sigla' based on the selection
filtered_data_filtered_by_year = filtered_data_by_year[
    (filtered_data_by_year['sigla'].isin(selected_sigla_filtered_by_year))
]

# Create a multiselect list for 'sigla'
selected_sigla = st.sidebar.multiselect("Seleccionar siglas de los pozos a comparar", max_rates_df['sigla'])

# Filter data for matching 'sigla'
filtered_data = data_sorted[
    (data_sorted['sigla'].isin(selected_sigla))
]


# Plot gas rate using Plotly
gas_rate_fig = go.Figure()

for i, sigla in enumerate(selected_sigla):
    filtered_well_data = filtered_data[filtered_data['sigla'] == sigla]
    
    # Filter data to start when 'Np' is different from zero
    filtered_well_data = filtered_well_data[filtered_well_data['Gp'] != 0]
    
    # Add a counter column to the filtered data
    filtered_well_data['counter'] = range(1, len(filtered_well_data) + 1)
    
    gas_rate_fig.add_trace(
        go.Scatter(
            x=filtered_well_data['counter'],  # Use the counter as x-axis
            y=filtered_well_data['gas_rate'],
            mode='lines+markers',
            name=f'Gas Rate - {sigla}',
            line=dict(color=gas_gp_palette[i % len(gas_gp_palette)]),  # Use the Gas Rate and Gp palette
        )
    )

gas_rate_fig.update_layout(
    title="Historia de Producción de Gas",
    xaxis_title="Meses",
    yaxis_title="Caudal de Gas (km3/d)",
)

# Display the gas rate Plotly figure in the Streamlit app
st.plotly_chart(gas_rate_fig)

# Define a list of specific colors for oil rate plots
oil_color_list = ['#008000', '#006400', '#90EE90', '#98FB98', '#8FBC8F', '#3CB371', '#2E8B57', '#808000', '#556B2F', '#6B8E23']

oil_rate_fig = go.Figure()

for i, sigla in enumerate(selected_sigla):
    filtered_well_data = filtered_data[filtered_data['sigla'] == sigla]
    
    # Filter data to start when 'Np' is different from zero
    filtered_well_data = filtered_well_data[filtered_well_data['Gp'] != 0]
    
    # Add a counter column to the filtered data
    filtered_well_data['counter'] = range(1, len(filtered_well_data) + 1)
    
    oil_rate_fig.add_trace(
        go.Scatter(
            x=filtered_well_data['counter'],  # Use the counter as x-axis
            y=filtered_well_data['oil_rate'],
            mode='lines+markers',
            name=f'Oil Rate - {sigla}',
            line=dict(color=oil_np_palette[i % len(oil_np_palette)]),  # Use the Oil Rate and Np palette
        )
    )

oil_rate_fig.update_layout(
    title="Historia de Producción de Petróleo",
    xaxis_title="Meses",
    yaxis_title="Caudal de Petróleo (m3/d)",
)

# Display the oil rate Plotly figure in the Streamlit app
st.plotly_chart(oil_rate_fig)

# Define a list of specific colors for water rate plots
water_color_list = ['#0000FF', '#0000CD', '#00008B', '#000080', '#191970', '#7B68EE', '#6A5ACD', '#483D8B', '#B0E0E6', '#ADD8E6', '#87CEFA', '#87CEEB', '#00BFFF', '#B0C4DE', '#1E90FF', '#6495ED']

water_rate_fig = go.Figure()

for i, sigla in enumerate(selected_sigla):
    filtered_well_data = filtered_data[filtered_data['sigla'] == sigla]
    
    # Filter data to start when 'Np' is different from zero
    filtered_well_data = filtered_well_data[filtered_well_data['Gp'] != 0]
    
    # Add a counter column to the filtered data
    filtered_well_data['counter'] = range(1, len(filtered_well_data) + 1)
    
    water_rate_fig.add_trace(
        go.Scatter(
            x=filtered_well_data['counter'],  # Use the counter as x-axis
            y=filtered_well_data['water_rate'],
            mode='lines+markers',
            name=f'Water Rate - {sigla}',
            line=dict(color=water_wp_palette[i % len(water_wp_palette)]),  # Use the Water Rate and Wp palette
        )
    )

water_rate_fig.update_layout(
    title="Historia de Producción de Agua",
    xaxis_title="Meses",
    yaxis_title="Caudal de Agua (m3/d)",
)

# Display the water rate Plotly figure in the Streamlit app
st.plotly_chart(water_rate_fig)

# Create separate figures for Gp, Np, and Wp
gp_fig = go.Figure()
np_fig = go.Figure()
wp_fig = go.Figure()

for i, sigla in enumerate(selected_sigla):
    filtered_well_data = filtered_data[filtered_data['sigla'] == sigla]
    
    # Filter data to start when 'Np' is different from zero
    filtered_well_data = filtered_well_data[filtered_well_data['Gp'] != 0]
    
    # Add a counter column to the filtered data
    filtered_well_data['counter'] = range(1, len(filtered_well_data) + 1)
    
    # Plot Gp
    gp_fig.add_trace(
        go.Scatter(
            x=filtered_well_data['counter'],  # Use the counter as x-axis
            y=filtered_well_data['Gp'],
            mode='lines+markers',
            name=f'Gp - {sigla}',
            line=dict(color=gas_gp_palette[i % len(gas_gp_palette)]),  # Use the Gas Rate and Gp palette
        )
    )

    # Plot Np
    np_fig.add_trace(
        go.Scatter(
            x=filtered_well_data['counter'],  # Use the counter as x-axis
            y=filtered_well_data['Np'],
            mode='lines+markers',
            name=f'Np - {sigla}',
            line=dict(color=oil_np_palette[i % len(oil_np_palette)]),  # Use the Oil Rate and Np palette
        )
    )

    # Plot Wp
    wp_fig.add_trace(
        go.Scatter(
            x=filtered_well_data['counter'],  # Use the counter as x-axis
            y=filtered_well_data['Wp'],
            mode='lines+markers',
            name=f'Wp - {sigla}',
            line=dict(color=water_wp_palette[i % len(water_wp_palette)]),  # Use the Water Rate and Wp palette
        )
    )

gp_fig.update_layout(
    title="Acumulada de Gas (km3)",
    xaxis_title="Meses",
    yaxis_title="Gp (km3)",
)

np_fig.update_layout(
    title="Acumulada de Petróleo (m3)",
    xaxis_title="Meses",
    yaxis_title="Np (m3)",
)

wp_fig.update_layout(
    title="Acumulada de Agua (m3)",
    xaxis_title="Meses",
    yaxis_title="Wp(m3)",
)

# Display the Gp, Np, and Wp Plotly figures in the Streamlit app
st.plotly_chart(gp_fig)
st.plotly_chart(np_fig)
st.plotly_chart(wp_fig)
