import streamlit as st
from scraper import ProductHuntScraper
import pandas as pd

st.title('Product Hunt Leaderboard Scraper')

# URL input
url = st.text_input(
    'Enter Product Hunt Leaderboard URL',
    value='https://www.producthunt.com/leaderboard',
    help='Enter the URL of the Product Hunt leaderboard you want to scrape'
)

# User limit input with explanation
user_limit = st.number_input(
    'Number of profiles to scrape (0 for unlimited)',
    min_value=0,
    value=20,
    help='Enter how many profiles you want to scrape. Set to 0 to scrape all profiles.'
)

if st.button('Start Scraping'):
    if url:
        try:
            scraper = ProductHuntScraper()
            # Convert user_limit to None if it's 0
            limit = None if user_limit == 0 else user_limit
            
            st.write(f"Starting scraper with {'unlimited' if limit is None else limit} profiles...")
            df = scraper.scrape_leaderboard(url, user_limit=limit)
            
            if not df.empty:
                st.write("Scraping completed!")
                st.dataframe(df)
                
                # Download button for CSV
                csv = df.to_csv(index=False)
                st.download_button(
                    label="Download data as CSV",
                    data=csv,
                    file_name="producthunt_data.csv",
                    mime="text/csv"
                )
            else:
                st.error("No data was scraped. Please try again.")
                
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
    else:
        st.error("Please enter a valid URL")