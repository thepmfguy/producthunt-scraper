import streamlit as st
import pandas as pd
from scraper import ProductHuntScraper

# Basic page setup
st.title("Product Hunt Leaderboard Scraper")

# Input field
url = st.text_input("Enter Product Hunt Leaderboard URL", 
                    value="https://www.producthunt.com/visit-streaks")

# Scrape button
if st.button("Start Scraping"):
    try:
        # Show status
        status = st.empty()
        status.write("Starting scraper...")
        
        # Initialize scraper
        scraper = ProductHuntScraper()
        
        # Run scraper
        status.write("Scraping in progress... This may take a few minutes.")
        df = scraper.scrape_leaderboard(url)
        
        # Show results
        status.write("Scraping completed!")
        st.dataframe(df)
        
        # Add download button
        st.download_button(
            "Download CSV",
            df.to_csv(index=False),
            "producthunt_leaderboard.csv",
            "text/csv"
        )
        
    except Exception as e:
        st.error(f"Error: {str(e)}")
