import streamlit as st
import pandas as pd

st.header('st.multiselect')

options = st.multiselect(
     'What are your favorite colors',
     ['Green', 'Yellow', 'Red', 'Blue'],
     ['Yellow', 'Red'])

st.write('You selected:', options)

# Generate random numbers
data = pd.DataFrame({'Random Numbers': [1, 2, 3, 4, 5]})

# Display table
st.write('Random Numbers Table')
st.dataframe(data)