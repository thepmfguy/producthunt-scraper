import streamlit as st
import os

# Force the port to 8505
os.environ["STREAMLIT_SERVER_PORT"] = "8505"

st.write("Hello World!")
