"""Main script for the Real.discount coupon scraper."""
import os
import time
from datetime import datetime
from typing import Dict, List
import json
import pywhatkit
import schedule
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.os_manager import ChromeType
from dotenv import load_dotenv

from config import *
from utils import (
    get_random_user_agent,
    load_cache,
    save_cache,
    categorize_course,
    format_whatsapp_message,
    parse_expiry_date
)

class CouponScraper:
    def __init__(self):
        """Initialize the scraper with necessary configurations."""
        load_dotenv()  # Load WhatsApp group IDs
        self.setup_selenium()
        self.cache = load_cache()
        
        # Load WhatsApp group IDs from environment variables
        self.group_ids = {}
        for category in CATEGORIES:
            env_key = CATEGORIES[category]['group_id']
            group_id = os.getenv(env_key)
            if group_id:
                self.group_ids[category] = group_id

    def setup_selenium(self):
        """Set up Selenium WebDriver with Chrome."""
        try:
            # Set up Chrome options
            chrome_options = Options()
            chrome_options.add_argument('--headless=new')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument(f'user-agent={get_random_user_agent()}')
            chrome_options.add_argument('--dns-prefetch-disable')
            chrome_options.add_argument('--disable-extensions')
            chrome_options.add_argument('--proxy-server="direct://"')
            chrome_options.add_argument('--proxy-bypass-list=*')
            chrome_options.add_argument('--ignore-certificate-errors')
            
            # Initialize ChromeDriverManager with specific version and location
            driver_path = ChromeDriverManager(chrome_type=ChromeType.GOOGLE).install()
            
            # Make sure we're using the correct chromedriver executable
            if not driver_path.endswith('.exe'):
                driver_dir = os.path.dirname(driver_path)
                driver_path = os.path.join(driver_dir, 'chromedriver.exe')
            
            print(f"ChromeDriver path: {driver_path}")
            
            if not os.path.exists(driver_path):
                raise FileNotFoundError(f"ChromeDriver not found at {driver_path}")
            
            # Create service with specific executable path
            service = Service(driver_path)
            
            # Create the driver with the service and options
            self.driver = webdriver.Chrome(
                service=service,
                options=chrome_options
            )
            
            # Set page load timeout
            self.driver.set_page_load_timeout(30)
            print("Chrome WebDriver setup successful!")
            
        except Exception as e:
            print(f"Failed to setup Chrome WebDriver: {str(e)}")
            if hasattr(self, 'driver'):
                self.driver.quit()
            raise

    def scrape_courses(self) -> List[Dict]:
        """Scrape course information from Real.discount."""
        courses = []
        try:
            print(f"Accessing {BASE_URL}...")
            self.driver.get(BASE_URL)
            
            # Scroll to load dynamic content
            print("Starting page scroll to load dynamic content...")
            last_height = self.driver.execute_script("return document.body.scrollHeight")
            scroll_count = 0
            while True:
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(SCROLL_PAUSE_TIME)
                new_height = self.driver.execute_script("return document.body.scrollHeight")
                scroll_count += 1
                print(f"Scroll {scroll_count}: Height changed from {last_height} to {new_height}")
                if new_height == last_height or scroll_count >= 5:  # Limit scrolls to 5
                    break
                last_height = new_height

            print("Parsing page content...")
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            
            # Find all course elements - look for li elements containing course information
            course_elements = soup.find_all('li')
            print(f"\nFound {len(course_elements)} potential course elements")
            
            for element in course_elements:
                # Check if this li contains a course
                if element.find('a') and element.find(['h3', 'h4', 'h5']):
                    course = self.parse_course_element(element)
                    if course:
                        if course['url'] not in self.cache:
                            print(f"New course found: {course['title']}")
                            courses.append(course)
                            self.cache[course['url']] = datetime.now().isoformat()
                        else:
                            print(f"Course already in cache: {course['url']}")

            print(f"\nTotal new courses found: {len(courses)}")
            save_cache(self.cache)
            return courses

        except Exception as e:
            print(f"Error scraping courses: {str(e)}")
            return []

    def parse_course_element(self, element) -> Dict:
        """Parse a course element and extract relevant information."""
        try:
            # Find title - look for headings
            title_elem = element.find(['h3', 'h4', 'h5'])
            if not title_elem:
                return None
            title = title_elem.text.strip()
            
            # Find the main link element
            link_elem = element.find('a')
            if not link_elem:
                return None
                
            # Get the coupon URL
            coupon_url = link_elem.get('href', '').strip()
            if not coupon_url:
                return None
            if not coupon_url.startswith('http'):
                coupon_url = 'https://real.discount' + coupon_url
            
            # Find description for categorization
            desc_elem = (
                element.find('p', class_='description') or
                element.find(class_=lambda x: x and 'description' in str(x).lower()) or
                element.find('p') or
                element.find('div', class_=lambda x: x and any(word in str(x).lower() for word in ['desc', 'about', 'info']))
            )
            description = desc_elem.text.strip() if desc_elem else title

            # Visit the coupon page to get the Udemy URL
            try:
                print(f"Visiting coupon page: {coupon_url}")
                # Add error handling for DNS resolution
                try:
                    self.driver.get(coupon_url)
                except Exception as e:
                    if "ERR_NAME_NOT_RESOLVED" in str(e):
                        print("DNS resolution failed, retrying with alternative URL...")
                        # Try alternative domain
                        coupon_url = coupon_url.replace('real.discount', 'www.real.discount')
                        self.driver.get(coupon_url)
                    else:
                        raise e
                
                time.sleep(2)  # Wait for page to load
                
                # Find the Udemy URL - look for any link to udemy.com
                soup = BeautifulSoup(self.driver.page_source, 'html.parser')
                udemy_link = soup.find('a', href=lambda x: x and 'udemy.com' in x)
                if udemy_link:
                    udemy_url = udemy_link['href']
                    print(f"Found Udemy URL: {udemy_url}")
                else:
                    print(f"No Udemy URL found for: {title}")
                    udemy_url = None
            except Exception as e:
                print(f"Error getting Udemy URL: {str(e)}")
                udemy_url = None
            
            # Find price - look for elements containing price information
            price_elem = element.find(string=lambda x: x and ('$' in x or 'free' in str(x).lower()))
            original_price = price_elem.strip() if price_elem else 'N/A'
            
            # Determine course category
            category = categorize_course(title, description, CATEGORIES)
            
            # Extract coupon code from Udemy URL if available
            coupon_code = None
            if udemy_url:
                coupon_param = 'couponCode='
                if coupon_param in udemy_url:
                    coupon_code = udemy_url.split(coupon_param)[1].split('&')[0]
            
            # Find expiry date
            expiry_elem = (
                element.find('span', class_='expiry-date') or
                element.find(class_=lambda x: x and any(word in str(x).lower() for word in ['expiry', 'expires', 'valid'])) or
                element.find(string=lambda x: x and any(word in str(x).lower() for word in ['expires', 'valid until']))
            )
            expiry_date = parse_expiry_date(expiry_elem.text.strip()) if expiry_elem else None
            
            return {
                'title': title,
                'description': description,
                'url': udemy_url or coupon_url,  # Use udemy_url if available, otherwise coupon_url
                'udemy_url': udemy_url,
                'original_price': original_price,
                'coupon_code': coupon_code,
                'expiry_date': expiry_date,
                'category': category  # Add category to the returned dictionary
            }
            
        except Exception as e:
            print(f"Error parsing course element: {str(e)}")
            return None

    def send_whatsapp_message(self, message: str, group_id: str):
        """Send a WhatsApp message using pywhatkit."""
        try:
            # Use pywhatkit to send message to WhatsApp group
            pywhatkit.sendwhatmsg_to_group(
                group_id=group_id,
                message=message,
                time_hour=datetime.now().hour,
                time_min=datetime.now().minute + 1
            )
            time.sleep(DELAY_BETWEEN_MESSAGES)
        except Exception as e:
            print(f"Error sending WhatsApp message: {str(e)}")

    def process_and_send_courses(self):
        """Main function to scrape courses and send WhatsApp messages."""
        courses = self.scrape_courses()
        if not courses:
            return

        # Group courses by category
        categorized_courses = {}
        for course in courses:
            category = course['category']
            if category not in categorized_courses:
                categorized_courses[category] = []
            categorized_courses[category].append(course)

        # Send a message for each category to its corresponding WhatsApp group
        for category, category_courses in categorized_courses.items():
            if category in self.group_ids:
                message = format_whatsapp_message(
                    category_courses,
                    category,
                    MESSAGE_TEMPLATE
                )
                self.send_whatsapp_message(message, self.group_ids[category])
                time.sleep(DELAY_BETWEEN_MESSAGES)

    def run_scheduled(self):
        """Run the scraper on a schedule."""
        schedule.every(SCHEDULE_INTERVAL).hours.do(self.process_and_send_courses)
        
        while True:
            schedule.run_pending()
            time.sleep(1)

    def cleanup(self):
        """Clean up resources."""
        self.driver.quit()

if __name__ == "__main__":
    scraper = CouponScraper()
    try:
        # Run once immediately
        scraper.process_and_send_courses()
        # Then start the schedule
        scraper.run_scheduled()
    except KeyboardInterrupt:
        print("\nStopping scraper...")
    finally:
        scraper.cleanup()
