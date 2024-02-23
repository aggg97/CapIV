import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from tabulate import tabulate

st.title("IPR Calculation")

# Definition of the quadratic curve equation (Inflow Performance Relationship - IPR)
def curve_IPR(Q, a, b, Pws):
    return np.sqrt(-a * Q ** 2 - b * Q + Pws**2)

# Function to collect input data
def collect_data():
    data = []
    Pws = st.number_input("Enter reservoir pressure (in bar): ")

    # Create a list to store data entry forms
    forms = []

    # Define a function to add a new data entry form
    def add_data_entry():
        with st.form(key=f"form_{len(forms)}"):
            st.write("Enter test data:")
            date = st.text_input("Enter date:")
            comment = st.text_input("Enter comment:")
            Pwf = st.number_input("Enter flowing bottomhole pressure (in bar):")
            Q = st.number_input("Enter rate (in km3/d):")
            submit_button = st.form_submit_button(label="Add Data")
            if submit_button:
                data.append((date, comment, Pwf, Q))
            st.write("\n")
        return submit_button

    # Display initial data entry form
    add_data_entry()

    # Allow users to add more data entry forms dynamically
    while st.button("Add More Data"):
        if add_data_entry():
            forms.append(True)
    
    # Print data as a table
    st.write("\nInput Data:")
    headers = ["Date", "Comment", "Pwf (bar)", "Rate (km3/d)"]
    st.table(data)
    return data, Pws

# Collect test data
data, Pws = collect_data()

# Convert data into arrays
Q_data = np.array([d[3] for d in data])
P_data = np.array([d[2] for d in data])

# Perform curve fitting
initial_guess = [3.75e-9, 4.17e-4]  # Initial guess for the parameters a, b, and c
bounds = ([0, 0], [np.inf, np.inf])  # Bounds for the parameters
params, _ = curve_fit(curve_IPR, Q_data, P_data, p0=initial_guess, bounds=bounds)
a_fit, b_fit = params

st.write("\n\nFitted Parameters:")
st.write(f"a: {a_fit:.2f} bar2/(Sm3/day)2")
st.write(f"b: {b_fit:.2f} bar2/(Sm3/day)")
st.write(f"Reservoir Pressure: {Pws:.2f} bar")

# AOF Calculation
# Bhaskara’s formula to find positive root
discriminant = b_fit ** 2 + 4 * a_fit * Pws ** 2
if discriminant >= 0:
    AOF = (-b_fit + np.sqrt(discriminant)) / (2 * a_fit)
    st.write(f"AOF: {AOF/1000:.2f} km3/d")
else:
    st.write("No real roots exist.")

# Range of points for extrapolation of the curve
Q_range = np.linspace(0, AOF, 500)
Pwf_fit = curve_IPR(Q_range, a_fit, b_fit, Pws)

# Test points
plt.scatter(Q_data, P_data, color='red', label='Test Data')
# Fitted curve
plt.plot(Q_range, Pwf_fit, color='blue', label='Fitted Curve')

# Set the limits for both x and y axes
plt.xlim(0, plt.xlim()[1])  # x-axis minimum to 0
plt.ylim(0, plt.ylim()[1])  # y-axis minimum to 0

plt.xlabel('Rate (km$^3$/ d)')
plt.ylabel('Pressure (bar)')
plt.title('Pressure vs Rate')
plt.legend()
plt.grid(True)
st.pyplot(plt)
