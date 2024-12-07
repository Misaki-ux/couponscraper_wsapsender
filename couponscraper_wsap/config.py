"""Configuration settings for the coupon scraper."""

# Scraping settings
BASE_URL = "https://www.real.discount"
RATE_LIMIT_DELAY = 2  # seconds between requests

# Category mappings with WhatsApp group numbers
CATEGORIES = {
    'personal_development': {
        'keywords': ['personal development', 'soft skills', 'leadership', 'communication'],
        'group_id': 'PERSONAL_DEV_GROUP'
    },
    'cybersecurity': {
        'keywords': ['cybersecurity', 'security', 'ethical hacking', 'penetration testing', 'cyber'],
        'group_id': 'CYBERSEC_GROUP'
    },
    'crypto': {
        'keywords': ['cryptocurrency', 'blockchain', 'bitcoin', 'crypto', 'web3'],
        'group_id': 'CRYPTO_GROUP'
    },
    'marketing': {
        'keywords': ['marketing', 'digital marketing', 'social media marketing'],
        'group_id': 'MARKETING_GROUP'
    },
    'backend': {
        'keywords': ['backend', 'python', 'java', 'nodejs', 'php', 'database'],
        'group_id': 'BACKEND_GROUP'
    },
    'web_design': {
        'keywords': ['web design', 'html', 'css', 'ui design'],
        'group_id': 'WEBDESIGN_GROUP'
    },
    'design': {
        'keywords': ['graphic design', 'photoshop', 'illustrator', 'figma'],
        'group_id': 'DESIGN_GROUP'
    },
    'fullstack': {
        'keywords': ['full stack', 'fullstack', 'mern', 'mean', 'web development'],
        'group_id': 'FULLSTACK_GROUP'
    },
    'app_development': {
        'keywords': ['application development', 'software development', 'app development'],
        'group_id': 'APPDEV_GROUP'
    },
    'mobile': {
        'keywords': ['mobile development', 'android', 'ios', 'flutter', 'react native'],
        'group_id': 'MOBILE_GROUP'
    },
    'cloud': {
        'keywords': ['cloud computing', 'aws', 'azure', 'google cloud', 'devops'],
        'group_id': 'CLOUD_GROUP'
    },
    'quantum': {
        'keywords': ['quantum computing', 'quantum', 'quantum mechanics'],
        'group_id': 'QUANTUM_GROUP'
    },
    'seo': {
        'keywords': ['seo', 'search engine optimization', 'google analytics'],
        'group_id': 'SEO_GROUP'
    },
    'software': {
        'keywords': ['software', 'tools', 'applications', 'productivity'],
        'group_id': 'SOFTWARE_GROUP'
    }
}

# WhatsApp message template
MESSAGE_TEMPLATE = """🎓 *New {category} Courses*

{courses}

🔍 More deals at: real.discount"""

COURSE_TEMPLATE = """
📚 *{title}*
💰 Original Price: {original_price}
🏷️ Coupon: {coupon_code}
⏰ Expires: {expiry_date}
🔗 {url}
"""

# Schedule settings
SCHEDULE_INTERVAL = 24  # hours

# Selenium settings
SELENIUM_TIMEOUT = 10  # seconds
SCROLL_PAUSE_TIME = 1  # seconds

# File paths
CACHE_FILE = "cache/processed_courses.json"

# WhatsApp settings
WHATSAPP_WAIT_TIME = 30  # seconds to wait for WhatsApp Web to load
DELAY_BETWEEN_MESSAGES = 20  # seconds between messages to avoid spam detection
