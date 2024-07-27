import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from PIL import Image

# Load and preprocess the data
@st.cache_data
def load_and_sort_data(dataset_url):
    df = pd.read_csv(dataset_url)
    return df

# URL of the dataset
dataset_url = "https://datos.gob.ar/dataset/energia-datos-fractura-pozos-hidrocarburos-adjunto-iv/archivo/energia_2280ad92-6ed3-403e-a095-50139863ab0d.csv"

# Load the data
data_sorted = load_and_sort_data(dataset_url)


