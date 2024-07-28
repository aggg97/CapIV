import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from PIL import Image

st.caption("Coming soon...")

COLUMNS_FRAC= [
    'sigla',  # atemporal
    'longitud_rama_horizontal_m',
    'cantidad_fracturas',
    'tipo_terminacion',
    'arena_bombeada_nacional_tn',
    'arena_bombeada_importada_tn'    
]

# Load and preprocess the data
@st.cache_data
def load_and_sort_data(dataset_url):
    df_frac = pd.read_csv(dataset_url, usecols=COLUMNS_FRAC)
    return df_frac

# URL of the dataset
dataset_frac_url = "http://datos.energia.gob.ar/dataset/71fa2e84-0316-4a1b-af68-7f35e41f58d7/resource/2280ad92-6ed3-403e-a095-50139863ab0d/download/datos-de-fractura-de-pozos-de-hidrocarburos-adjunto-iv-actualizacin-diaria.csv"

# Load the data
df_frac= load_and_sort_data(dataset_frac_url)

# Display the first few rows of the dataframe in Streamlit
st.write("### Data Preview")
st.write(df_frac.head())

