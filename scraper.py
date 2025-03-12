from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import pandas as pd
import time
import re

class ProductHuntScraper:
    def __init__(self):
        self.driver = None
        self.data = []
        
    def setup_driver(self):
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920,1080')
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=options)
        
    def extract_streak_days(self, streak_text):
        match = re.search(r'(\d+)\s*day streak', streak_text)
        return int(match.group(1)) if match else 0
        
    def get_social_links(self, profile_url):
        """Visit user profile and extract social media links"""
        social_links = {
            'twitter': '',
            'linkedin': '',
            'facebook': '',
            'website': ''
        }
        
        try:
            self.driver.get(profile_url)
            time.sleep(2)  # Wait for page load
            
            # Look for social links in the profile
            links = self.driver.find_elements(By.TAG_NAME, 'a')
            for link in links:
                try:
                    href = link.get_attribute('href')
                    if href:
                        if 'twitter.com' in href:
                            social_links['twitter'] = href
                        elif 'linkedin.com' in href:
                            social_links['linkedin'] = href
                        elif 'facebook.com' in href:
                            social_links['facebook'] = href
                        elif href.startswith('http') and not any(domain in href for domain in ['producthunt.com', 'twitter.com', 'linkedin.com', 'facebook.com']):
                            social_links['website'] = href
                except:
                    continue
                    
            print(f"Found social links for profile: {profile_url}")
            print(social_links)
            
        except Exception as e:
            print(f"Error getting social links for {profile_url}: {str(e)}")
            
        return social_links
        
    def scroll_to_load_all(self):
        """Scroll page to load all users"""
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        while True:
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height
            print("Scrolling to load more users...")
        
    def scrape_leaderboard(self, url="https://www.producthunt.com/visit-streaks"):
        try:
            print("Setting up web driver...")
            self.setup_driver()
            
            print(f"Navigating to {url}")
            self.driver.get(url)
            time.sleep(5)  # Wait for initial load
            
            print("Scrolling to load all users...")
            self.scroll_to_load_all()
            
            print("Finding user entries...")
            user_entries = self.driver.find_elements(By.CSS_SELECTOR, 'div[role="listitem"]')
            total_users = len(user_entries)
            print(f"Found {total_users} users")
            
            for index, entry in enumerate(user_entries, 1):
                try:
                    # Get user name and profile link
                    user_link = entry.find_element(By.TAG_NAME, 'a')
                    name = user_link.text.strip()
                    profile_url = user_link.get_attribute('href')
                    
                    # Get streak information
                    streak_text = entry.text
                    streak_days = self.extract_streak_days(streak_text)
                    
                    print(f"Processing user {index}/{total_users}: {name}")
                    
                    # Get social links from profile
                    social_links = self.get_social_links(profile_url)
                    
                    self.data.append({
                        'Name': name,
                        'Streak Days': streak_days,
                        'Profile URL': profile_url,
                        'Twitter': social_links['twitter'],
                        'LinkedIn': social_links['linkedin'],
                        'Facebook': social_links['facebook'],
                        'Website': social_links['website']
                    })
                    
                    print(f"Successfully processed {name}")
                    
                except Exception as e:
                    print(f"Error processing user entry: {str(e)}")
                    continue
                    
        except Exception as e:
            print(f"Error in scraping: {str(e)}")
        finally:
            if self.driver:
                self.driver.quit()
                
        return pd.DataFrame(self.data)
