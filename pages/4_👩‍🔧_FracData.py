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
dataset_url = "http://datos.energia.gob.ar/dataset/71fa2e84-0316-4a1b-af68-7f35e41f58d7/resource/2280ad92-6ed3-403e-a095-50139863ab0d/download/datos-de-fractura-de-pozos-de-hidrocarburos-adjunto-iv-actualizacin-diaria.csv"

# Load the data
df = load_and_sort_data(dataset_url)

# Display the first few rows of the dataframe in Streamlit
st.write("### Data Preview")
st.write(df.head())

# Additional Streamlit elements can be added here, such as charts or images
# Example: Displaying a simple line chart
st.write("### Simple Line Chart")
fig = px.line(df, x='Column1', y='Column2', title='Sample Line Chart')
st.plotly_chart(fig)
