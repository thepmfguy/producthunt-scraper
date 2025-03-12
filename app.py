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
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=options)
        
    def extract_streak_days(self, streak_text):
        match = re.search(r'(\d+)\s*day streak', streak_text)
        return int(match.group(1)) if match else 0
        
    def get_social_links(self, profile_url):
        social_links = {
            'twitter': '',
            'linkedin': '',
            'facebook': '',
            'website': ''
        }
        
        try:
            self.driver.get(profile_url)
            time.sleep(2)
            
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
                        elif href.startswith('http') and not any(domain in href for domain in ['producthunt.com', 'twitter', 'linkedin', 'facebook']):
                            social_links['website'] = href
                except:
                    continue
        except Exception as e:
            print(f'Error getting social links: {str(e)}')
            
        return social_links
        
    def scrape_leaderboard(self, url="https://www.producthunt.com/visit-streaks"):
        try:
            self.setup_driver()
            self.driver.get(url)
            time.sleep(5)
            
            user_entries = self.driver.find_elements(By.CSS_SELECTOR, 'div[role="listitem"]')
            
            for entry in user_entries:
                try:
                    user_link = entry.find_element(By.TAG_NAME, 'a')
                    name = user_link.text.strip()
                    profile_url = user_link.get_attribute('href')
                    
                    streak_text = entry.text
                    streak_days = self.extract_streak_days(streak_text)
                    
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
                    
                except Exception as e:
                    print(f'Error processing user: {str(e)}')
                    continue
                    
        except Exception as e:
            print(f'Error in scraping: {str(e)}')
        finally:
            if self.driver:
                self.driver.quit()
                
        return pd.DataFrame(self.data)
