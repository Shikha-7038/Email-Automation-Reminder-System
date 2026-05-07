"""
Email sending module - Handles SMTP communication
Personalizes templates and sends emails to recipients
"""

import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import Dict, Tuple
from src.config import EmailConfig

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/email_system.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def personalize_template(template: str, contact: Dict) -> str:
    """
    Replace placeholders in template with actual contact data
    
    Args:
        template: Email template with {{placeholders}}
        contact: Dictionary with contact information
    
    Returns:
        Personalized email content
    """
    personalized = template
    for key, value in contact.items():
        placeholder = f"{{{{{key}}}}}"
        personalized = personalized.replace(placeholder, str(value))
    return personalized


def send_single_email(recipient_email: str, subject: str, body: str) -> Tuple[bool, str]:
    """
    Send a single email using SMTP
    
    Args:
        recipient_email: Email address of recipient
        subject: Email subject line
        body: Email body content (HTML or plain text)
    
    Returns:
        Tuple of (success_status, message)
    """
    if EmailConfig.DRY_RUN:
        logger.info(f"[DRY RUN] Would send to: {recipient_email}")
        logger.info(f"[DRY RUN] Subject: {subject}")
        return True, "Dry run - email not actually sent"
    
    if not EmailConfig.is_configured():
        error_msg = "Email not configured. Set SENDER_EMAIL and SENDER_PASSWORD in .env"
        logger.error(error_msg)
        return False, error_msg
    
    try:
        # Create message
        msg = MIMEMultipart()
        msg['From'] = EmailConfig.SENDER_EMAIL
        msg['To'] = recipient_email
        msg['Subject'] = subject
        
        # Attach body
        msg.attach(MIMEText(body, 'html'))
        
        # Connect and send
        with smtplib.SMTP(EmailConfig.SMTP_SERVER, EmailConfig.SMTP_PORT) as server:
            server.starttls()  # Enable TLS encryption
            server.login(EmailConfig.SENDER_EMAIL, EmailConfig.SENDER_PASSWORD)
            server.send_message(msg)
        
        logger.info(f"✅ Email sent successfully to: {recipient_email}")
        return True, "Email sent successfully"
        
    except smtplib.SMTPAuthenticationError:
        error_msg = "Authentication failed. Check your email and app password"
        logger.error(error_msg)
        return False, error_msg
    except smtplib.SMTPRecipientsRefused:
        error_msg = f"Recipient refused: {recipient_email}"
        logger.error(error_msg)
        return False, error_msg
    except Exception as e:
        error_msg = f"Failed to send to {recipient_email}: {str(e)}"
        logger.error(error_msg)
        return False, error_msg


def send_reminders(contacts: list, reminder: Dict, template: str) -> list:
    """
    Send reminders to all contacts
    
    Args:
        contacts: List of contact dictionaries
        reminder: Reminder information dictionary
        template: Email template string
    
    Returns:
        List of results for each contact
    """
    results = []
    subject = reminder.get('subject', 'Reminder')
    
    for contact in contacts:
        # Personalize template for this contact
        personalized_body = personalize_template(template, contact)
        
        # Send email
        success, message = send_single_email(contact['email'], subject, personalized_body)
        
        results.append({
            'contact_name': contact['name'],
            'contact_email': contact['email'],
            'reminder_title': reminder['title'],
            'status': 'Success' if success else 'Failed',
            'message': message,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
        
        # Log individual results
        log_file = 'logs/sent_emails.log' if success else 'logs/failed_emails.log'
        with open(log_file, 'a') as f:
            f.write(f"{datetime.now()} - {contact['name']} ({contact['email']}) - {reminder['title']}\n")
    
    return results