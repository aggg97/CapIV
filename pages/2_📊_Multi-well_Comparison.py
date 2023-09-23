import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from PIL import Image

# Define a function to load and sort the data
@st.cache(allow_output_mutation=True)
def load_and_sort_data(dataset_url):
    df = pd.read_csv(dataset_url)
    data_sorted = df.sort_values(by='fecha_data', ascending=True)
    return data_sorted

# URL of the dataset
dataset_url = "http://datos.energia.gob.ar/dataset/c846e79c-026c-4040-897f-1ad3543b407c/resource/b5b58cdc-9e07-41f9-b392-fb9ec68b0725/download/produccin-de-pozos-de-gas-y-petrleo-no-convencional.csv"

# Load and sort the data using the cached function
data_sorted = load_and_sort_data(dataset_url)

# Add a new column "date" by combining year and month
data_sorted['date'] = pd.to_datetime(data_sorted['anio'].astype(str) + '-' + data_sorted['mes'].astype(str) + '-1')
# Convert the "date" column to datetime format
data_sorted['date'] = pd.to_datetime(data_sorted['date'])

# Calculate gas rate for the filtered data
data_sorted['gas_rate'] = data_sorted['prod_gas'] / data_sorted['tef']

# Calculate oil rate and water rate for the filtered data
data_sorted['oil_rate'] = data_sorted['prod_pet'] / data_sorted['tef']
data_sorted['water_rate'] = data_sorted['prod_agua'] / data_sorted['tef']

# Calculate max peak rates for the selected_sigla
max_gas_rate = data_sorted['gas_rate'].max()
max_oil_rate = data_sorted['oil_rate'].max()

# Check the conditions to determine the fluid type
if max_oil_rate == 0 or (max_gas_rate / max_oil_rate) > 3000:
    fluid_type = 'Gas'
else:
    fluid_type = 'Petróleo'

# Add the calculated values to the DataFrame as new columns
data_sorted['GOR'] = max_gas_rate / max_oil_rate if max_oil_rate != 0 else 0
data_sorted['Tipo de Fluido según McCain'] = fluid_type

st.header(f":blue[Capítulo IV Dataset - Producción No Convencional]")
image = Image.open('Vaca Muerta rig.png')
st.sidebar.image(image)
st.sidebar.title("Por favor filtrar aquí: ")

# Create a multiselect widget for 'tipo pozo'
tipos_pozo = data_sorted['tipopozo'].unique()
selected_tipos_pozo = st.sidebar.multiselect("Seleccionar tipo de pozo:", tipos_pozo)

# Create a dropdown list for 'empresa'
empresas = data_sorted['empresa'].unique()
selected_empresa = st.sidebar.selectbox("Seleccionar operadora:", empresas)

# Filter data based on selected 'tipo pozo' and 'empresa'
matching_data = data_sorted[
    (data_sorted['tipopozo'].isin(selected_tipos_pozo)) &
    (data_sorted['empresa'] == selected_empresa)
]

# Get unique 'sigla' values based on selected 'empresa' and 'tipo pozo'
siglas_for_selected_empresa = matching_data['sigla'].unique()

# Create a dropdown list for 'sigla'
selected_sigla = st.sidebar.selectbox("Seleccionar sigla del pozo", siglas_for_selected_empresa)

# Filter data for matching 'empresa' and 'sigla'
matching_data = matching_data[matching_data['sigla'] == selected_sigla]

# Now, you can proceed with the rest of your code below.

# Display the filtered data table
if st.button(f"Ver datos históricos del pozo: {selected_sigla}"):
    st.write("Filtered Data:")
    st.write(matching_data)

# Calculate max peak rates for the selected_sigla
max_gas_rate = matching_data['gas_rate'].max()
max_oil_rate = matching_data['oil_rate'].max()
max_water_rate = matching_data['water_rate'].max()

# Round the maximum rates to one decimal place
max_gas_rate_rounded = round(max_gas_rate, 1)
max_oil_rate_rounded = round(max_oil_rate, 1)
max_water_rate_rounded = round(max_water_rate, 1)

st.header(selected_sigla)
col1, col2, col3 = st.columns(3)
col1.metric(label=f":red[Caudal Máximo de Gas (km3/d)]", value=max_gas_rate_rounded)
col2.metric(label=f":green[Caudal Máximo de Petróleo (m3/d)]", value=max_oil_rate_rounded)
col3.metric(label=f":blue[Caudal Máximo de Agua (m3/d)]", value=max_water_rate_rounded)

# Plot gas rate using Plotly
gas_rate_fig = go.Figure()
gas_rate_fig.add_trace(
    go.Scatter(
        x=matching_data['counter'],
        y=matching_data['gas_rate'],
        mode='lines+markers',
        name='Gas Rate',
        line=dict(color='red')
    )
)
gas_rate_fig.update_layout(
    title=f"Historia de Producción de Gas del pozo: {selected_sigla}",
    xaxis_title="Meses",
    yaxis_title="Caudal de Gas (km3/d)"
)
gas_rate_fig.update_yaxes(range=[0, None])
st.plotly_chart(gas_rate_fig)

# Plot oil rate using Plotly
oil_rate_fig = go.Figure()
oil_rate_fig.add_trace(
    go.Scatter(
        x=matching_data['counter'],
        y=matching_data['oil_rate'],
        mode='lines+markers',
        name='Oil Rate',
        line=dict(color='green')
    )
)
oil_rate_fig.update_layout(
    title=f"Historia de Producción de Petróleo del pozo: {selected_sigla}",
    xaxis_title="Meses",
    yaxis_title="Caudal de Petróleo (m3/d)"
)
oil_rate_fig.update_yaxes(rangemode='tozero')
st.plotly_chart(oil_rate_fig)

# Plot water rate using Plotly
water_rate_fig = go.Figure()
water_rate_fig.add_trace(
    go.Scatter(
        x=matching_data['counter'],
        y=matching_data['water_rate'],
        mode='lines+markers',
        name='Water Rate',
        line=dict(color='blue')
    )
)
water_rate_fig.update_layout(
    title=f"Historia de Producción de Agua del pozo: {selected_sigla}",
    xaxis_title="Meses",
    yaxis_title="Caudal de Agua (m3/d)"
)
water_rate_fig.update_yaxes(range=[0, None])
st.plotly_chart(water_rate_fig)
