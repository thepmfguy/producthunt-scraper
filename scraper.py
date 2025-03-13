from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import time
import re
import streamlit as st

class ProductHuntScraper:
    def __init__(self):
        self.driver = None
        self.data = []
        
    def setup_driver(self):
        try:
            options = Options()
            options.add_argument('--start-maximized')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            
            # Use default Chrome installation
            service = Service()
            self.driver = webdriver.Chrome(options=options)
            
        except Exception as e:
            st.error(f"Error setting up driver: {str(e)}")
            raise e
    
    def get_social_links(self, profile_url):
        """Extract social media links from user profile"""
        social_links = {
            'twitter': '',
            'facebook': '',
            'linkedin': '',
            'other_links': []
        }
        
        try:
            self.driver.get(profile_url)
            # Wait for page load with shorter timeout
            wait = WebDriverWait(self.driver, 5)
            
            # Try to find the links div
            try:
                links_div = wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'div[class*="styles_links"]'))
                )
                
                links = links_div.find_elements(By.TAG_NAME, 'a')
                
                for link in links:
                    href = link.get_attribute('href')
                    if href:
                        if 'twitter.com' in href:
                            social_links['twitter'] = href
                        elif 'facebook.com' in href:
                            social_links['facebook'] = href
                        elif 'linkedin.com' in href:
                            social_links['linkedin'] = href
                        else:
                            social_links['other_links'].append(href)
                            
            except:
                # If we can't find the links div, just return empty social links
                st.write(f"No social links found for profile: {profile_url}")
                return None
                
        except Exception as e:
            st.write(f"Error accessing profile: {profile_url}")
            return None
            
        return social_links
    
    def scroll_to_bottom(self, user_limit=None):
        """Scroll until no new content loads or user limit is reached"""
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        no_change_count = 0
        max_no_change = 3  # Number of attempts before deciding we're at the bottom
        
        while True:
            # Check if we've reached the user limit
            current_users = len(self.driver.find_elements(By.CSS_SELECTOR, 'div[data-sentry-component="VisitStreak"]'))
            if user_limit and current_users >= user_limit:
                st.write(f"Reached user limit of {user_limit}")
                break
            
            # Scroll down
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            
            # Calculate new scroll height
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            
            if new_height == last_height:
                no_change_count += 1
                if no_change_count >= max_no_change:
                    if user_limit is None:
                        st.write("Reached the bottom of the page")
                    break
            else:
                no_change_count = 0
                
            last_height = new_height
            st.write(f"Found {current_users} users so far...")
            
    def scrape_leaderboard(self, url, user_limit=None):
        try:
            self.setup_driver()
            self.driver.get(url)
            
            # Wait for initial load
            wait = WebDriverWait(self.driver, 10)
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div[data-sentry-component="VisitStreak"]')))
            
            # Scroll to load users
            st.write("Scrolling to load users...")
            self.scroll_to_bottom(user_limit)
            
            # Find all visit streak elements
            user_entries = wait.until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div[data-sentry-component="VisitStreak"]'))
            )
            
            if user_limit:
                user_entries = user_entries[:user_limit]
                
            st.write(f"Processing {len(user_entries)} users")
            
            progress_bar = st.progress(0)
            
            # Store user data first
            users_data = []
            for entry in user_entries:
                try:
                    name_element = entry.find_element(By.CSS_SELECTOR, 'div[class*="text-16 font-semibold"]')
                    name = name_element.text.strip()
                    
                    profile_link = entry.find_element(By.TAG_NAME, 'a')
                    profile_url = profile_link.get_attribute('href')
                    if not profile_url.startswith('http'):
                        profile_url = f"https://producthunt.com{profile_url}"
                    
                    streak_element = entry.find_element(By.CSS_SELECTOR, 'div[class*="text-14 font-normal"]')
                    streak_text = streak_element.text
                    streak_days = re.search(r'(\d+)\s*day streak', streak_text)
                    streak_count = int(streak_days.group(1)) if streak_days else 0
                    
                    users_data.append({
                        'name': name,
                        'profile_url': profile_url,
                        'streak_count': streak_count
                    })
                    
                except Exception as e:
                    st.error(f"Error collecting user data: {str(e)}")
                    continue
            
            # Now process social links for each user
            for index, user in enumerate(users_data):
                try:
                    st.write(f"Getting social links for {user['name']}...")
                    social_links = self.get_social_links(user['profile_url'])
                    
                    # Skip if no social links found
                    if social_links is None:
                        st.write(f"Skipping {user['name']} - no social links available")
                        continue
                    
                    self.data.append({
                        'Name': user['name'],
                        'Profile URL': user['profile_url'],
                        'Streak Days': user['streak_count'],
                        'Twitter': social_links['twitter'],
                        'Facebook': social_links['facebook'],
                        'LinkedIn': social_links['linkedin'],
                        'Other Links': ', '.join(social_links['other_links'])
                    })
                    
                    # Update progress
                    progress = (index + 1) / len(users_data)
                    progress_bar.progress(progress)
                    st.write(f"Processed {index + 1}/{len(users_data)}: {user['name']}")
                    
                except Exception as e:
                    st.write(f"Skipping {user['name']} due to error")
                    continue
                    
        except Exception as e:
            st.error(f"Error in scraping: {str(e)}")
        finally:
            if self.driver:
                self.driver.quit()
                
        return pd.DataFrame(self.data)
