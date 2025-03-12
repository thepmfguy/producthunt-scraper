import streamlit as st
import pandas as pd
from scraper import ProductHuntScraper
import time

# Page config
st.set_page_config(page_title="Product Hunt Leaderboard Scraper", layout="wide")

# Title
st.title("Product Hunt Leaderboard Scraper")

# Description
st.write("Scrape user profiles and social media links from Product Hunt's leaderboard")

# Input
url = st.text_input("Enter Product Hunt Leaderboard URL", 
                    value="https://www.producthunt.com/visit-streaks")

if st.button("Start Scraping"):
    if url:
        try:
            # Show progress
            progress_text = st.empty()
            progress_text.text("Starting scraper...")
            
            # Initialize scraper
            scraper = ProductHuntScraper()
            
            # Start scraping
            progress_text.text("Scraping in progress... This may take several minutes...")
            df = scraper.scrape_leaderboard(url)
            
            # Show success message
            progress_text.text("Scraping completed!")
            
            # Display results
            st.write(f"Found {len(df)} users")
            st.dataframe(df)
            
            # Download options
            st.download_button(
                "Download CSV",
                df.to_csv(index=False).encode('utf-8'),
                "producthunt_leaderboard.csv",
                "text/csv"
            )
            
            # Excel/Google Sheets format
            buffer = pd.ExcelWriter('producthunt_leaderboard.xlsx', engine='openpyxl')
            df.to_excel(buffer, index=False)
            buffer.close()
            
            with open('producthunt_leaderboard.xlsx', 'rb') as f:
                st.download_button(
                    "Download for Google Sheets",
                    f,
                    "producthunt_leaderboard.xlsx",
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
    else:
        st.warning("Please enter a valid URL")
