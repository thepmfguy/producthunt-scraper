from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import pandas as pd
import time

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
        
    def scroll_page(self):
        try:
            last_height = self.driver.execute_script('return document.body.scrollHeight')
            while True:
                self.driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
                time.sleep(2)
                new_height = self.driver.execute_script('return document.body.scrollHeight')
                if new_height == last_height:
                    break
                last_height = new_height
        except Exception as e:
            print(f'Error while scrolling: {str(e)}')
            
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
                        elif 'http' in href and not any(domain in href for domain in ['producthunt.com', 'twitter', 'linkedin', 'facebook']):
                            social_links['website'] = href
                except:
                    continue
        except Exception as e:
            print(f'Error getting social links: {str(e)}')
            
        return social_links
        
    def scrape_leaderboard(self, url):
        try:
            self.setup_driver()
            self.driver.get(url)
            time.sleep(5)
            
            while True:
                self.scroll_page()
                
                users = self.driver.find_elements(By.CSS_SELECTOR, '[data-test="leaderboard-user"]')
                
                for user in users:
                    try:
                        name = user.find_element(By.CSS_SELECTOR, '[data-test="user-name"]').text
                        profile_url = user.find_element(By.CSS_SELECTOR, 'a').get_attribute('href')
                        
                        if not any(d['Profile URL'] == profile_url for d in self.data):
                            social_links = self.get_social_links(profile_url)
                            
                            self.data.append({
                                'Name': name,
                                'Profile URL': profile_url,
                                'Twitter': social_links['twitter'],
                                'LinkedIn': social_links['linkedin'],
                                'Facebook': social_links['facebook'],
                                'Website': social_links['website']
                            })
                    except Exception as e:
                        print(f'Error processing user: {str(e)}')
                        continue
                
                try:
                    next_button = self.driver.find_element(By.CSS_SELECTOR, '[data-test="pagination-next"]')
                    if not next_button.is_enabled():
                        break
                    next_button.click()
                    time.sleep(2)
                except:
                    break
                    
        except Exception as e:
            print(f'Error in scraping: {str(e)}')
        finally:
            if self.driver:
                self.driver.quit()
                
        return pd.DataFrame(self.data)
