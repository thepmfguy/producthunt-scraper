import streamlit as st

st.title("Product Hunt Leaderboard Scraper")

st.write("Testing if the app works...")

url = st.text_input("Enter Product Hunt Leaderboard URL", 
                    "https://www.producthunt.com/visit-streaks")

if st.button("Test Button"):
    st.write("Button clicked!")
