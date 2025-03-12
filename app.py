import streamlit as st
import pandas as pd
from scraper import ProductHuntScraper
import time
import io

st.set_page_config(page_title='Product Hunt Leaderboard Scraper', layout='wide')

st.title('Product Hunt Leaderboard Scraper')

st.markdown('''
    <style>
    .stButton>button {
        width: 100%;
        background-color: #da552f;
        color: white;
    }
    .stProgress > div > div > div > div {
        background-color: #da552f;
    }
    </style>
''', unsafe_allow_html=True)

url = st.text_input('Enter Product Hunt Leaderboard URL', 
                    'https://www.producthunt.com/leaderboard')

if st.button('Start Scraping'):
    if url:
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        scraper = ProductHuntScraper()
        
        try:
            status_text.text('Scraping in progress... This may take several minutes.')
            df = scraper.scrape_leaderboard(url)
            
            st.success('Scraping completed!')
            st.dataframe(df)
            
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label='Download CSV',
                data=csv,
                file_name='producthunt_leaderboard.csv',
                mime='text/csv'
            )
            
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                df.to_excel(writer, index=False)
            excel_data = buffer.getvalue()
            
            st.download_button(
                label='Download for Google Sheets',
                data=excel_data,
                file_name='producthunt_leaderboard.xlsx',
                mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            
        except Exception as e:
            st.error(f'An error occurred: {str(e)}')
            
    else:
        st.warning('Please enter a valid URL')
