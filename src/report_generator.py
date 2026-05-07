"""
Report generation module - Creates CSV reports of email sending activity
"""

import csv
import logging
from datetime import datetime
from typing import List, Dict
import os

logger = logging.getLogger(__name__)


def generate_email_report(results: List[Dict], output_dir: str = 'outputs') -> str:
    """
    Generate CSV report of email sending results
    
    Args:
        results: List of result dictionaries from send_reminders
        output_dir: Directory to save the report
    
    Returns:
        Path to generated report file
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate filename with timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"email_report_{timestamp}.csv"
    filepath = os.path.join(output_dir, filename)
    
    try:
        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['contact_name', 'contact_email', 'reminder_title', 
                         'status', 'message', 'timestamp']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            writer.writerows(results)
        
        logger.info(f"📊 Report generated: {filepath}")
        
        # Print summary
        success_count = sum(1 for r in results if r['status'] == 'Success')
        failed_count = len(results) - success_count
        
        print("\n" + "="*50)
        print("📊 EMAIL SENDING SUMMARY")
        print("="*50)
        print(f"Total emails attempted: {len(results)}")
        print(f"✅ Successful: {success_count}")
        print(f"❌ Failed: {failed_count}")
        print(f"Success rate: {(success_count/len(results)*100):.1f}%")
        print(f"📁 Report saved to: {filepath}")
        print("="*50 + "\n")
        
        return filepath
        
    except Exception as e:
        logger.error(f"Failed to generate report: {e}")
        return ""


def generate_system_summary() -> Dict:
    """
    Generate summary of system activity
    
    Returns:
        Dictionary with system statistics
    """
    summary = {
        'total_sent': 0,
        'total_failed': 0,
        'active_reminders': 0,
        'last_run': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    # Count sent emails
    try:
        with open('logs/sent_emails.log', 'r') as f:
            summary['total_sent'] = len(f.readlines())
    except FileNotFoundError:
        pass
    
    # Count failed emails
    try:
        with open('logs/failed_emails.log', 'r') as f:
            summary['total_failed'] = len(f.readlines())
    except FileNotFoundError:
        pass
    
    return summary