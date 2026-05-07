#!/usr/bin/env python3
"""
Email Automation & Reminder System
Windows-Compatible Version - No Emojis
"""

import os
import csv
import smtplib
import logging
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# ============================================
# SETUP LOGGING (Windows compatible)
# ============================================
os.makedirs('logs', exist_ok=True)

# Fix for Windows console encoding
import sys
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/email_system.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# ============================================
# AUTO-CREATE MISSING FILES
# ============================================
def auto_create_files():
    """Automatically create all necessary files if they don't exist"""
    
    # Create folders
    os.makedirs('data', exist_ok=True)
    os.makedirs('templates', exist_ok=True)
    os.makedirs('outputs', exist_ok=True)
    
    # Create contacts.csv if missing
    if not os.path.exists('data/contacts.csv'):
        logger.info("[INFO] Creating sample contacts.csv...")
        contacts = [
            ['name', 'email', 'role', 'company'],
            ['Alice Johnson', 'alice@example.com', 'Team Lead', 'Tech Corp'],
            ['Bob Smith', 'bob@example.com', 'Developer', 'Innovate Inc'],
            ['Carol Davis', 'carol@example.com', 'Project Manager', 'Global Solutions'],
            ['David Wilson', 'david@example.com', 'Sales Executive', 'Growth Dynamics'],
            ['Emma Brown', 'emma@example.com', 'HR Specialist', 'People First']
        ]
        with open('data/contacts.csv', 'w', newline='', encoding='utf-8') as f:
            csv.writer(f).writerows(contacts)
        logger.info("[SUCCESS] Created data/contacts.csv with 5 sample contacts")
    
    # Create reminders.csv if missing
    if not os.path.exists('data/reminders.csv'):
        logger.info("[INFO] Creating sample reminders.csv...")
        
        # Create reminders for today and tomorrow
        today = datetime.now()
        reminder1_time = (today + timedelta(minutes=5)).strftime('%Y-%m-%d %H:%M')
        reminder2_time = (today + timedelta(hours=1)).strftime('%Y-%m-%d %H:%M')
        reminder3_time = (today + timedelta(days=1)).strftime('%Y-%m-%d 10:00')
        
        reminders = [
            ['title', 'subject', 'send_datetime', 'recurring'],
            ['Test Reminder Now', 'Test Reminder for {{name}}', reminder1_time, 'No'],
            ['Team Meeting', 'Weekly Team Sync: {{name}}', reminder2_time, 'No'],
            ['Project Deadline', 'Project Update Required - {{name}}', reminder3_time, 'No']
        ]
        with open('data/reminders.csv', 'w', newline='', encoding='utf-8') as f:
            csv.writer(f).writerows(reminders)
        logger.info("[SUCCESS] Created data/reminders.csv with sample reminders")
    
    # Create email template if missing
    if not os.path.exists('templates/meeting_reminder.txt'):
        logger.info("[INFO] Creating email template...")
        template = """Dear {{name}},

REMINDER: {{subject}}

Your Details:
-------------
- Role: {{role}}
- Company: {{company}}
-------------

This is an automated reminder. Please take necessary action.

Best regards,
Email Automation System
---
Sent at: """ + datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        with open('templates/meeting_reminder.txt', 'w', encoding='utf-8') as f:
            f.write(template)
        logger.info("[SUCCESS] Created templates/meeting_reminder.txt")

# ============================================
# LOAD DATA
# ============================================
def load_contacts():
    """Load contacts from CSV"""
    contacts = []
    try:
        with open('data/contacts.csv', 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            contacts = list(reader)
        logger.info(f"[INFO] Loaded {len(contacts)} contacts")
    except Exception as e:
        logger.error(f"[ERROR] Failed to load contacts: {e}")
    return contacts

def load_reminders():
    """Load reminders from CSV and return only due ones"""
    reminders = []
    current_time = datetime.now()
    
    try:
        with open('data/reminders.csv', 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    reminder_time = datetime.strptime(row['send_datetime'], '%Y-%m-%d %H:%M')
                    if reminder_time <= current_time:
                        reminders.append(row)
                        logger.info(f"[SCHEDULE] Due reminder: {row['title']} at {row['send_datetime']}")
                except ValueError as e:
                    logger.warning(f"[WARNING] Invalid date format for {row.get('title', 'unknown')}: {row.get('send_datetime', 'N/A')}")
    except Exception as e:
        logger.error(f"[ERROR] Failed to load reminders: {e}")
    
    return reminders

def load_template():
    """Load email template"""
    try:
        with open('templates/meeting_reminder.txt', 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        logger.error(f"[ERROR] Failed to load template: {e}")
        return "Dear {{name}},\n\nREMINDER: {{subject}}\n\nBest regards"

# ============================================
# EMAIL SENDING
# ============================================
def send_email(to_email, subject, body, dry_run=False):
    """Send email via SMTP or simulate if dry_run"""
    
    if dry_run:
        logger.info(f"[DRY RUN] To: {to_email}")
        logger.info(f"[DRY RUN] Subject: {subject}")
        return True, "Dry run - no email sent"
    
    # Actual email sending
    smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
    smtp_port = int(os.getenv('SMTP_PORT', 587))
    sender_email = os.getenv('SENDER_EMAIL')
    sender_password = os.getenv('SENDER_PASSWORD')
    
    if not sender_email or not sender_password:
        logger.error("[ERROR] Email not configured. Set SENDER_EMAIL and SENDER_PASSWORD in .env")
        return False, "Configuration missing"
    
    try:
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))
        
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)
        
        logger.info(f"[SUCCESS] Sent to: {to_email}")
        return True, "Success"
        
    except smtplib.SMTPAuthenticationError:
        error_msg = "Authentication failed - Check your email/app password"
        logger.error(f"[ERROR] {error_msg}")
        return False, error_msg
    except Exception as e:
        logger.error(f"[ERROR] Failed to {to_email}: {str(e)}")
        return False, str(e)

# ============================================
# PERSONALIZE TEMPLATE
# ============================================
def personalize_template(template, contact, reminder):
    """Replace placeholders with actual data"""
    personalized = template
    personalized = personalized.replace('{{name}}', contact.get('name', ''))
    personalized = personalized.replace('{{role}}', contact.get('role', ''))
    personalized = personalized.replace('{{company}}', contact.get('company', ''))
    personalized = personalized.replace('{{subject}}', reminder.get('subject', ''))
    return personalized

# ============================================
# GENERATE REPORT
# ============================================
def generate_report(results):
    """Create CSV report of all sending activities"""
    if not results:
        print("\n[INFO] No results to report")
        return None
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'outputs/email_report_{timestamp}.csv'
    
    try:
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['contact', 'email', 'reminder', 'status', 'message', 'time'])
            writer.writeheader()
            writer.writerows(results)
        
        # Print summary
        success = sum(1 for r in results if r['status'] == 'Success')
        failed = len(results) - success
        
        print("\n" + "="*50)
        print("EMAIL SENDING SUMMARY")
        print("="*50)
        print(f"Total emails: {len(results)}")
        print(f"Successful: {success}")
        print(f"Failed: {failed}")
        if len(results) > 0:
            print(f"Success rate: {(success/len(results)*100):.1f}%")
        print(f"Report saved: {filename}")
        print("="*50)
        
        return filename
    except Exception as e:
        logger.error(f"[ERROR] Failed to generate report: {e}")
        return None

# ============================================
# DISPLAY BANNER
# ============================================
def display_banner():
    """Display application banner without emojis"""
    banner = """
    ================================================
         EMAIL AUTOMATION & REMINDER SYSTEM
    ================================================
    """
    print(banner)

# ============================================
# MAIN FUNCTION
# ============================================
def main():
    """Main execution function"""
    
    # Display banner
    display_banner()
    print(f"Current time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*50 + "\n")
    
    # Auto-create files
    auto_create_files()
    
    # Check for dry run
    dry_run = True  # Default to safe mode
    
    # Check if .env is configured
    sender_email = os.getenv('SENDER_EMAIL')
    if not sender_email or sender_email == 'your_email@gmail.com':
        print("\n[WARNING] EMAIL NOT CONFIGURED")
        print("To send real emails, create .env file with:")
        print("  SENDER_EMAIL=your_real_email@gmail.com")
        print("  SENDER_PASSWORD=your_app_password")
        print("\n[INFO] Running in DRY RUN mode (no emails will be sent)\n")
        dry_run = True
    else:
        # Ask user
        response = input("\nSend REAL emails? (yes/no) [default: no]: ").lower()
        dry_run = response != 'yes'
        if dry_run:
            print("[INFO] Running in DRY RUN mode\n")
        else:
            print("[INFO] Running in REAL EMAIL mode\n")
    
    # Load data
    contacts = load_contacts()
    if not contacts:
        print("[ERROR] No contacts found. Exiting.")
        return
    
    reminders = load_reminders()
    if not reminders:
        print("[INFO] No reminders due at this time.")
        print("   Check reminders.csv for scheduled dates.")
        print("\nTIP: To test immediately, edit data/reminders.csv and set send_datetime to a past time.\n")
        return
    
    template = load_template()
    
    # Process each reminder
    all_results = []
    
    for reminder in reminders:
        print(f"\n[PROCESSING] Reminder: {reminder['title']}")
        print(f"   Scheduled: {reminder['send_datetime']}")
        
        for contact in contacts:
            # Personalize
            personalized_body = personalize_template(template, contact, reminder)
            subject = reminder['subject'].replace('{{name}}', contact['name'])
            
            # Send email
            success, message = send_email(contact['email'], subject, personalized_body, dry_run)
            
            # Record result
            all_results.append({
                'contact': contact['name'],
                'email': contact['email'],
                'reminder': reminder['title'],
                'status': 'Success' if success else 'Failed',
                'message': message,
                'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            })
    
    # Generate report
    generate_report(all_results)
    
    print("\n[COMPLETE] System execution completed!\n")

# ============================================
# RUN
# ============================================
if __name__ == "__main__":
    main()