"""
Scheduling module - Checks which reminders need to be sent
Manages time-based scheduling and recurrence
"""

import csv
from datetime import datetime, timedelta
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)


def parse_time(time_str: str) -> datetime:
    """
    Parse time string to datetime object
    Supports format: YYYY-MM-DD HH:MM
    """
    return datetime.strptime(time_str, '%Y-%m-%d %H:%M')


def is_due(reminder_time: str, current_time: datetime = None) -> bool:
    """
    Check if a reminder is due to be sent
    
    Args:
        reminder_time: Time string in format 'YYYY-MM-DD HH:MM'
        current_time: Current datetime (defaults to now)
    
    Returns:
        True if reminder time is now or in the past
    """
    if current_time is None:
        current_time = datetime.now()
    
    reminder_dt = parse_time(reminder_time)
    return reminder_dt <= current_time


def get_due_reminders(reminders_file: str) -> List[Dict]:
    """
    Read reminders CSV and return only due reminders
    
    Args:
        reminders_file: Path to reminders CSV file
    
    Returns:
        List of due reminder dictionaries
    """
    due_reminders = []
    current_time = datetime.now()
    
    try:
        with open(reminders_file, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                # Check if reminder is due
                if is_due(row['send_datetime'], current_time):
                    # Check if already sent today (prevent duplicates)
                    if not was_sent_today(row['title']):
                        due_reminders.append(row)
                        logger.info(f"📅 Reminder due: {row['title']} at {row['send_datetime']}")
                    else:
                        logger.info(f"⏭️ Skipping {row['title']} - already sent today")
    
    except FileNotFoundError:
        logger.error(f"Reminders file not found: {reminders_file}")
    except Exception as e:
        logger.error(f"Error reading reminders: {e}")
    
    return due_reminders


def was_sent_today(reminder_title: str) -> bool:
    """
    Check if a reminder was already sent today
    
    Args:
        reminder_title: Title of the reminder
    
    Returns:
        True if sent today
    """
    today = datetime.now().strftime('%Y-%m-%d')
    
    try:
        with open('logs/sent_emails.log', 'r') as f:
            content = f.read()
            return today in content and reminder_title in content
    except FileNotFoundError:
        return False


def update_sent_status(reminders_file: str, sent_reminders: List[str]):
    """
    Update reminders file to mark sent reminders
    Creates a new file with sent status column
    """
    updated_rows = []
    
    with open(reminders_file, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        fieldnames = reader.fieldnames + ['status', 'sent_at'] if 'status' not in reader.fieldnames else reader.fieldnames
        
        for row in reader:
            if row['title'] in sent_reminders:
                row['status'] = 'sent'
                row['sent_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            else:
                row['status'] = row.get('status', 'pending')
                row['sent_at'] = row.get('sent_at', '')
            updated_rows.append(row)
    
    # Write back to file
    with open(reminders_file, 'w', encoding='utf-8', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(updated_rows)
    
    logger.info(f"Updated status for {len(sent_reminders)} reminders")