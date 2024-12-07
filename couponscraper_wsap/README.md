# Real.Discount Coupon Scraper with WhatsApp Integration

This script scrapes coupon codes from Real.discount and sends them via WhatsApp using Twilio's API.

## Features

- Scrapes course coupons from Real.discount
- Categorizes courses automatically
- Sends formatted updates via WhatsApp
- Runs on a scheduled basis
- Avoids duplicate entries
- Includes error handling and rate limiting

## Setup Instructions

1. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Create a .env file with your Twilio credentials:
   ```
   TWILIO_ACCOUNT_SID=your_account_sid
   TWILIO_AUTH_TOKEN=your_auth_token
   TWILIO_PHONE_NUMBER=your_twilio_whatsapp_number
   TARGET_PHONE_NUMBER=target_whatsapp_number
   ```

3. Configure the settings in config.py:
   - Adjust scheduling intervals
   - Modify category mappings
   - Update rate limiting settings

## Usage

Run the main script:
```bash
python main.py
```

The script will:
1. Start scraping Real.discount for coupon codes
2. Categorize the courses
3. Send formatted WhatsApp messages
4. Run continuously based on the schedule

## Maintenance

- Check the logs regularly for any errors
- Update user agents in config.py if needed
- Monitor rate limits and adjust as necessary
- Keep dependencies updated using requirements.txt
