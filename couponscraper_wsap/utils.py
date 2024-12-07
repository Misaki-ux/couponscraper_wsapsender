"""Utility functions for the coupon scraper."""
import json
import os
from datetime import datetime
from fake_useragent import UserAgent
from typing import Dict, List, Optional

def get_random_user_agent() -> str:
    """Generate a random user agent string."""
    ua = UserAgent()
    return ua.random

def load_cache() -> Dict:
    """Load the cache of processed courses."""
    if os.path.exists('cache/processed_courses.json'):
        with open('cache/processed_courses.json', 'r') as f:
            return json.load(f)
    return {}

def save_cache(cache: Dict) -> None:
    """Save the cache of processed courses."""
    os.makedirs('cache', exist_ok=True)
    with open('cache/processed_courses.json', 'w') as f:
        json.dump(cache, f)

def categorize_course(title: str, description: str, categories: Dict) -> str:
    """Categorize a course based on its title and description."""
    title_desc = (title + ' ' + description).lower()
    
    # Check each category's keywords
    for category, data in categories.items():
        if any(keyword in title_desc for keyword in data['keywords']):
            return category
            
    # If no match is found, try to find partial matches
    for category, data in categories.items():
        if any(any(word in keyword for word in title_desc.split()) 
               for keyword in data['keywords']):
            return category
            
    return 'other'

def format_whatsapp_message(courses: List[Dict], category: str, template: str) -> str:
    """Format courses into a WhatsApp message."""
    formatted_courses = []
    for course in courses:
        course_text = template.format(
            title=course['title'],
            original_price=course.get('original_price', 'N/A'),
            coupon_code=course.get('coupon_code', 'N/A'),
            expiry_date=course.get('expiry_date', 'N/A'),
            url=course['url']
        )
        formatted_courses.append(course_text)
    
    return template.format(
        category=category.replace('_', ' ').title(),
        courses='\n'.join(formatted_courses[:10])  # Limit to 10 courses per message
    )

def parse_expiry_date(date_str: Optional[str]) -> Optional[str]:
    """Parse and format expiry date string."""
    if not date_str:
        return None
    try:
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        return date_obj.strftime('%B %d, %Y')
    except ValueError:
        return date_str
