import streamlit as st
import pandas as pd
from scraper import ProductHuntScraper

# Page config
st.set_page_config(
    page_title="Product Hunt Leaderboard Scraper",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS
st.markdown("""
    <style>
        .main {
            padding: 2rem;
        }
        
        .header {
            background-color: #da552f;
            color: white;
            padding: 1.5rem;
            border-radius: 10px;
            margin-bottom: 2rem;
        }
        
        .styled-table {
            width: 100%;
            border-collapse: collapse;
            margin: 25px 0;
            font-size: 0.9em;
            box-shadow: 0 0 20px rgba(0, 0, 0, 0.15);
            border-radius: 8px;
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
            background-color: #f8f8f8;
        }
        
        .social-link {
            display: inline-block;
            padding: 4px 8px;
            margin: 2px;
            border-radius: 4px;
            color: white;
            text-decoration: none;
            font-size: 0.8em;
        }
        
        .twitter { background-color: #1DA1F2; }
        .linkedin { background-color: #0077B5; }
        .facebook { background-color: #4267B2; }
        .website { background-color: #333333; }
        
        .stButton>button {
            background-color: #da552f;
            color: white;
            border: none;
            border-radius: 5px;
            padding: 0.5rem 1rem;
            font-weight: bold;
        }
    </style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
    <div class="header">
        <h1 style='font-size: 2rem; font-weight: bold;'>Product Hunt Leaderboard Scraper</h1>
        <p style='font-size: 1.1rem; margin-top: 0.5rem;'>Track the most active community members and their social presence</p>
    </div>
""", unsafe_allow_html=True)

# Input section
url = st.text_input("Enter Product Hunt Leaderboard URL", 
                    value="https://www.producthunt.com/visit-streaks")

if st.button("Start Scraping"):
    if url:
        try:
            with st.spinner('Scraping in progress... Please wait...'):
                # Initialize scraper and get data
                scraper = ProductHuntScraper()
                df = scraper.scrape_leaderboard(url)
                
                # Success message
                st.success('✅ Scraping completed successfully!')
                
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
                    buffer = io.BytesIO()
                    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                        df.to_excel(writer, index=False)
                    excel_data = buffer.getvalue()
                    st.download_button(
                        "📥 Download Excel",
                        data=excel_data,
                        file_name="producthunt_leaderboard.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
                    
        except Exception as e:
            st.error(f'❌ Error: {str(e)}')
    else:
        st.warning('⚠️ Please enter a valid URL')
