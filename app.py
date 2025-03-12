import streamlit as st
import pandas as pd
from scraper import ProductHuntScraper
import time

# Page config
st.set_page_config(
    page_title="Product Hunt Leaderboard Scraper",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS
st.markdown("""
    <style>
        /* Main container */
        .main {
            padding: 2rem;
        }
        
        /* Header */
        .header {
            background-color: #da552f;
            color: white;
            padding: 2rem;
            border-radius: 10px;
            margin-bottom: 2rem;
        }
        
        /* Table styles */
        .styled-table {
            width: 100%;
            border-collapse: collapse;
            margin: 25px 0;
            font-size: 0.9em;
            font-family: sans-serif;
            box-shadow: 0 0 20px rgba(0, 0, 0, 0.15);
            border-radius: 10px;
            overflow: hidden;
        }
        
        .styled-table thead tr {
            background-color: #da552f;
            color: white;
            text-align: left;
        }
        
        .styled-table th,
        .styled-table td {
            padding: 12px 15px;
        }
        
        .styled-table tbody tr {
            border-bottom: 1px solid #dddddd;
        }
        
        .styled-table tbody tr:nth-of-type(even) {
            background-color: #f3f3f3;
        }
        
        .styled-table tbody tr:last-of-type {
            border-bottom: 2px solid #da552f;
        }
        
        /* Social links */
        .social-link {
            display: inline-block;
            padding: 5px 10px;
            margin: 2px;
            border-radius: 5px;
            color: white;
            text-decoration: none;
            font-size: 0.8em;
        }
        
        .twitter { background-color: #1DA1F2; }
        .linkedin { background-color: #0077B5; }
        .facebook { background-color: #4267B2; }
        .website { background-color: #333333; }
        
        /* Input and button styling */
        .stTextInput>div>div>input {
            border-radius: 5px;
        }
        
        .stButton>button {
            background-color: #da552f;
            color: white;
            border: none;
            border-radius: 5px;
            padding: 0.5rem 1rem;
            font-weight: bold;
        }
        
        /* Status messages */
        .status-message {
            padding: 1rem;
            border-radius: 5px;
            margin: 1rem 0;
        }
        
        .success { background-color: #d4edda; color: #155724; }
        .error { background-color: #f8d7da; color: #721c24; }
        .info { background-color: #cce5ff; color: #004085; }
    </style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
    <div class="header">
        <h1 style='font-size: 2.5rem; font-weight: bold;'>Product Hunt Leaderboard Scraper</h1>
        <p style='font-size: 1.2rem; margin-top: 1rem;'>Track the most active community members and their social presence</p>
    </div>
""", unsafe_allow_html=True)

# Input section
url = st.text_input("Enter Product Hunt Leaderboard URL", 
                    value="https://www.producthunt.com/visit-streaks",
                    help="Enter the URL of the Product Hunt leaderboard page")

if st.button("Start Scraping"):
    if url:
        try:
            # Show progress
            status = st.empty()
            status.markdown("""
                <div class="status-message info">
                    <p>🔄 Scraping in progress... Please wait...</p>
                </div>
            """, unsafe_allow_html=True)
            
            # Initialize scraper and get data
            scraper = ProductHuntScraper()
            df = scraper.scrape_leaderboard(url)
            
            # Success message
            status.markdown("""
                <div class="status-message success">
                    <p>✅ Scraping completed successfully!</p>
                </div>
            """, unsafe_allow_html=True)
            
            # Create table HTML
            table_html = """
                <table class="styled-table">
                    <thead>
                        <tr>
                            <th>Rank</th>
                            <th>Name</th>
                            <th>Streak Days</th>
                            <th>Social Links</th>
                        </tr>
                    </thead>
                    <tbody>
            """
            
            # Add rows to table
            for idx, row in df.iterrows():
                social_links = ""
                if row['Twitter']:
                    social_links += f'<a href="{row["Twitter"]}" target="_blank" class="social-link twitter">Twitter</a>'
                if row['LinkedIn']:
                    social_links += f'<a href="{row["LinkedIn"]}" target="_blank" class="social-link linkedin">LinkedIn</a>'
                if row['Facebook']:
                    social_links += f'<a href="{row["Facebook"]}" target="_blank" class="social-link facebook">Facebook</a>'
                if row['Website']:
                    social_links += f'<a href="{row["Website"]}" target="_blank" class="social-link website">Website</a>'
                
                table_html += f"""
                    <tr>
                        <td>{idx + 1}</td>
                        <td>
                            <a href="{row['Profile URL']}" target="_blank" style="color: #da552f; text-decoration: none; font-weight: bold;">
                                {row['Name']}
                            </a>
                        </td>
                        <td>{row['Streak Days']} days</td>
                        <td>{social_links}</td>
                    </tr>
                """
            
            table_html += """
                    </tbody>
                </table>
            """
            
            # Display table
            st.markdown(table_html, unsafe_allow_html=True)
            
            # Add download buttons
            col1, col2 = st.columns(2)
            with col1:
                csv = df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    "📥 Download CSV",
                    data=csv,
                    file_name="producthunt_leaderboard.csv",
                    mime="text/csv"
                )
            with col2:
                excel_buffer = pd.ExcelWriter('producthunt_leaderboard.xlsx', engine='openpyxl')
                df.to_excel(excel_buffer, index=False)
                excel_buffer.close()
                with open('producthunt_leaderboard.xlsx', 'rb') as f:
                    st.download_button(
                        "📥 Download Excel",
                        data=f,
                        file_name="producthunt_leaderboard.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
                
        except Exception as e:
            st.markdown(f"""
                <div class="status-message error">
                    <p>❌ Error: {str(e)}</p>
                </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown("""
            <div class="status-message error">
                <p>⚠️ Please enter a valid URL</p>
            </div>
        """, unsafe_allow_html=True)
