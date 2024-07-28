import streamlit as st
import pandas as pd
import plotly.express as px

# Define the columns for the first dataset
COLUMNS_FRAC = [
    'sigla',  # atemporal
    'longitud_rama_horizontal_m',
    'cantidad_fracturas',
    'tipo_terminacion',
    'arena_bombeada_nacional_tn',
    'arena_bombeada_importada_tn'    
]

# Load and preprocess the fracture data
@st.cache_data
def load_and_sort_data_frac(dataset_url):
    df_frac = pd.read_csv(dataset_url, usecols=COLUMNS_FRAC)
    return df_frac

# URL of the fracture dataset
dataset_frac_url = "http://datos.energia.gob.ar/dataset/71fa2e84-0316-4a1b-af68-7f35e41f58d7/resource/2280ad92-6ed3-403e-a095-50139863ab0d/download/datos-de-fractura-de-pozos-de-hidrocarburos-adjunto-iv-actualizacin-diaria.csv"

# Load the fracture data
df_frac = load_and_sort_data_frac(dataset_frac_url)

# Display the first few rows of the fracture dataframe in Streamlit
st.write("### Fracture Data Preview")
st.write(df_frac.head())

# Define the columns for the second dataset
COLUMNS = [
    'sigla',  # well identifier
    'anio',  # year
    'mes',  # month
    'prod_pet',  # oil production
    'prod_gas',  # gas production
    'prod_agua',  # water production
    'iny_gas',  # gas injection
    'tef',  # effective time
    'tipoextraccion',  # extraction type
    'tipopozo',  # well type
    'empresa',  # company
    'formacion',  # formation
    'areayacimiento',  # field area
    'fecha_data'  # data date
]

# Load and preprocess the production data
@st.cache_data
def load_and_sort_data_prod(dataset_url):
    df_prod = pd.read_csv(dataset_url, usecols=COLUMNS)
    df_prod['date'] = pd.to_datetime(df_prod['anio'].astype(str) + '-' + df_prod['mes'].astype(str) + '-1')
    data_sorted = df_prod.sort_values(by=['sigla', 'fecha_data'], ascending=True)
    return data_sorted

# URL of the production dataset
dataset_prod_url = "http://datos.energia.gob.ar/dataset/c846e79c-026c-4040-897f-1ad3543b407c/resource/b5b58cdc-9e07-41f9-b392-fb9ec68b0725/download/produccin-de-pozos-de-gas-y-petrleo-no-convencional.csv"

# Load the production data
data_sorted = load_and_sort_data_prod(dataset_prod_url)

# Display the first few rows of the production dataframe in Streamlit
st.write("### Production Data Preview")
st.write(data_sorted.head())

# Merge the dataframes on 'sigla'
df_merged = pd.merge(df_frac, data_sorted[['sigla', 'anio']], on='sigla', how='left').drop_duplicates()

# Plot the length of fracture
st.write("### Length of Fracture")
fig_length = px.bar(df_merged.groupby('anio')['longitud_rama_horizontal_m'].sum().reset_index(),
                    x='anio', y='longitud_rama_horizontal_m',
                    labels={'longitud_rama_horizontal_m': 'Total Length of Fracture (m)', 'anio': 'Year'},
                    title='Total Length of Fracture by Year')
st.plotly_chart(fig_length)

# Plot the number of fractures
st.write("### Number of Fractures")
fig_fractures = px.bar(df_merged.groupby('anio')['cantidad_fracturas'].sum().reset_index(),
                       x='anio', y='cantidad_fracturas',
                       labels={'cantidad_fracturas': 'Number of Fractures', 'anio': 'Year'},
                       title='Total Number of Fractures by Year')
st.plotly_chart(fig_fractures)
