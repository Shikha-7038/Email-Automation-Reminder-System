# dashboard.py - COMPLETE NO-PANDAS VERSION
# Copy this entire file exactly as shown

import streamlit as st
import csv
import os
import subprocess
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="Email Automation System",
    page_icon="📧",
    layout="wide"
)

# Helper functions (no pandas needed!)
def read_csv_file(filepath):
    """Read CSV and return list of dictionaries"""
    if not os.path.exists(filepath):
        return []
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            return list(reader)
    except Exception as e:
        st.error(f"Error reading {filepath}: {e}")
        return []

def write_csv_file(filepath, data, fieldnames):
    """Write list of dictionaries to CSV"""
    try:
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)
        return True
    except Exception as e:
        st.error(f"Error writing {filepath}: {e}")
        return False

# Title
st.title("📧 Email Automation & Reminder System")
st.markdown("---")

# Sidebar navigation
st.sidebar.header("Navigation")
page = st.sidebar.selectbox(
    "Select Page",
    ["🏠 Dashboard Overview", "👥 Contacts", "⏰ Reminders", "📊 Reports", "⚙️ Run System"]
)

# ============================================
# PAGE 1: DASHBOARD OVERVIEW
# ============================================
if page == "🏠 Dashboard Overview":
    st.header("Dashboard Overview")
    
    # Create columns for metrics
    col1, col2, col3, col4 = st.columns(4)
    
    # Load data
    contacts = read_csv_file('data/contacts.csv')
    reminders = read_csv_file('data/reminders.csv')
    
    # Count reports
    reports_count = 0
    if os.path.exists('outputs'):
        reports_count = len([f for f in os.listdir('outputs') if f.endswith('.csv')])
    
    # Display metrics
    col1.metric("Total Contacts", len(contacts))
    col2.metric("Total Reminders", len(reminders))
    col3.metric("Reports Generated", reports_count)
    col4.metric("System Status", "Active" if contacts else "Setup Needed")
    
    st.markdown("---")
    
    # Quick actions
    st.subheader("Quick Actions")
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("▶️ Run Dry Run Test", use_container_width=True):
            st.info("Running dry-run mode...")
            result = subprocess.run(["python", "main.py", "--dry-run"], capture_output=True, text=True)
            if result.returncode == 0:
                st.success("✅ Dry run completed successfully!")
                with st.expander("View Output"):
                    st.code(result.stdout[-2000:])
            else:
                st.error("Dry run failed. Check logs.")
    
    with col2:
        st.warning("⚠️ Configure .env file to send real emails")
    
    # Recent activity
    st.markdown("---")
    st.subheader("Recent Activity Log")
    
    if os.path.exists('logs/email_system.log'):
        with open('logs/email_system.log', 'r', encoding='utf-8') as f:
            lines = f.readlines()
            # Show last 15 lines
            recent_lines = lines[-15:] if len(lines) > 15 else lines
            for line in recent_lines:
                st.text(line.strip())
    else:
        st.info("No logs yet. Run the system first.")

# ============================================
# PAGE 2: CONTACTS
# ============================================
elif page == "👥 Contacts":
    st.header("Contact Management")
    
    # Tabs for view and add
    tab1, tab2 = st.tabs(["📋 View Contacts", "➕ Add Contact"])
    
    with tab1:
        contacts = read_csv_file('data/contacts.csv')
        if contacts:
            # Display as simple table
            st.markdown("### Contact List")
            
            # Convert to list of lists for display
            headers = list(contacts[0].keys())
            data = [[c.get(h, '') for h in headers] for c in contacts]
            
            # Display using st.dataframe (which doesn't need pandas for simple dicts)
            import json
            st.write("Total contacts:", len(contacts))
            st.table(data)
            
            # Delete option
            st.markdown("---")
            st.subheader("Delete Contact")
            contact_names = [c.get('name', 'Unknown') for c in contacts]
            if contact_names:
                to_delete = st.selectbox("Select contact to delete", contact_names)
                if st.button("Delete Contact", type="primary"):
                    contacts = [c for c in contacts if c.get('name') != to_delete]
                    write_csv_file('data/contacts.csv', contacts, ['name', 'email', 'role', 'company'])
                    st.success(f"Deleted {to_delete}")
                    st.rerun()
        else:
            st.info("No contacts found. Run main.py first or add contacts using the form below.")
    
    with tab2:
        st.markdown("### Add New Contact")
        with st.form("add_contact_form"):
            name = st.text_input("Full Name *")
            email = st.text_input("Email Address *")
            role = st.text_input("Role/Position")
            company = st.text_input("Company")
            
            submitted = st.form_submit_button("Add Contact")
            
            if submitted:
                if not name or not email:
                    st.error("Name and email are required!")
                else:
                    # Load existing contacts
                    contacts = read_csv_file('data/contacts.csv')
                    
                    # Add new contact
                    new_contact = {
                        'name': name,
                        'email': email,
                        'role': role if role else "Not specified",
                        'company': company if company else "Not specified"
                    }
                    contacts.append(new_contact)
                    
                    # Save
                    if write_csv_file('data/contacts.csv', contacts, ['name', 'email', 'role', 'company']):
                        st.success(f"✅ Added {name} successfully!")
                        st.balloons()

# ============================================
# PAGE 3: REMINDERS
# ============================================
elif page == "⏰ Reminders":
    st.header("Reminder Management")
    
    tab1, tab2 = st.tabs(["📅 View Reminders", "➕ Schedule Reminder"])
    
    with tab1:
        reminders = read_csv_file('data/reminders.csv')
        if reminders:
            st.markdown("### Scheduled Reminders")
            
            # Display
            headers = list(reminders[0].keys())
            data = [[r.get(h, '') for h in headers] for r in reminders]
            st.table(data)
            
            # Delete option
            st.markdown("---")
            st.subheader("Delete Reminder")
            reminder_titles = [r.get('title', 'Unknown') for r in reminders]
            if reminder_titles:
                to_delete = st.selectbox("Select reminder to delete", reminder_titles)
                if st.button("Delete Reminder", type="primary"):
                    reminders = [r for r in reminders if r.get('title') != to_delete]
                    write_csv_file('data/reminders.csv', reminders, ['title', 'subject', 'send_datetime', 'recurring'])
                    st.success(f"Deleted {to_delete}")
                    st.rerun()
        else:
            st.info("No reminders found. Schedule some using the form!")
    
    with tab2:
        st.markdown("### Schedule New Reminder")
        st.info("💡 Tip: Use {{name}} in subject for personalization")
        
        with st.form("add_reminder_form"):
            title = st.text_input("Reminder Title *")
            subject = st.text_input("Email Subject * (use {{name}} for recipient's name)")
            
            col1, col2 = st.columns(2)
            with col1:
                send_date = st.date_input("Send Date", datetime.now())
            with col2:
                send_time = st.time_input("Send Time", datetime.now().time())
            
            recurring = st.selectbox("Recurring", ["No", "Daily", "Weekly"])
            
            submitted = st.form_submit_button("Schedule Reminder")
            
            if submitted:
                if not title or not subject:
                    st.error("Title and subject are required!")
                else:
                    send_datetime = f"{send_date} {send_time}"
                    
                    reminders = read_csv_file('data/reminders.csv')
                    new_reminder = {
                        'title': title,
                        'subject': subject,
                        'send_datetime': send_datetime,
                        'recurring': recurring if recurring != "No" else ""
                    }
                    reminders.append(new_reminder)
                    
                    if write_csv_file('data/reminders.csv', reminders, ['title', 'subject', 'send_datetime', 'recurring']):
                        st.success(f"✅ Scheduled '{title}' for {send_datetime}!")
                        st.info("Reminder will be sent when you run the system at that time.")

# ============================================
# PAGE 4: REPORTS
# ============================================
elif page == "📊 Reports":
    st.header("Email Reports")
    
    if os.path.exists('outputs'):
        reports = [f for f in os.listdir('outputs') if f.endswith('.csv')]
        reports.sort(reverse=True)  # Newest first
        
        if reports:
            selected_report = st.selectbox("Select Report", reports)
            
            if selected_report:
                # Read and display report
                with open(f'outputs/{selected_report}', 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    rows = list(reader)
                
                if rows:
                    # Summary stats
                    st.markdown("### Report Summary")
                    col1, col2, col3 = st.columns(3)
                    
                    total = len(rows)
                    success = sum(1 for r in rows if r.get('status', '').lower() == 'success')
                    failed = total - success
                    
                    col1.metric("Total Emails", total)
                    col2.metric("Successful", success, delta=f"{success/total*100:.0f}%" if total > 0 else "0%")
                    col3.metric("Failed", failed)
                    
                    st.markdown("### Detailed Report")
                    # Display as table
                    headers = list(rows[0].keys())
                    data = [[r.get(h, '') for h in headers] for r in rows]
                    st.table(data)
                    
                    # Download button
                    with open(f'outputs/{selected_report}', 'r', encoding='utf-8') as f:
                        csv_content = f.read()
                    st.download_button(
                        label="📥 Download Report",
                        data=csv_content,
                        file_name=selected_report,
                        mime="text/csv"
                    )
        else:
            st.info("No reports yet. Run the system to generate reports.")
    else:
        st.info("No outputs folder found. Run the system first.")

# ============================================
# PAGE 5: RUN SYSTEM
# ============================================
elif page == "⚙️ Run System":
    st.header("Execute Email Automation")
    
    st.warning("⚠️ Important: Sending real emails requires .env configuration")
    
    # Check configuration
    has_env = os.path.exists('.env')
    if has_env:
        with open('.env', 'r') as f:
            content = f.read()
            has_credentials = 'your_email@gmail.com' not in content and 'your_app_password' not in content
        if has_credentials:
            st.success("✅ .env file found with credentials!")
        else:
            st.warning("⚠️ .env exists but needs real credentials")
    else:
        st.info("📝 No .env file - will run in dry-run mode only")
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Dry Run Mode (Test Only)")
        st.caption("No real emails will be sent")
        if st.button("🚀 Run Dry Run", type="primary", use_container_width=True):
            with st.spinner("Running dry-run simulation..."):
                result = subprocess.run(["python", "main.py", "--dry-run"], capture_output=True, text=True)
                if result.returncode == 0:
                    st.success("✅ Dry run completed!")
                    with st.expander("View Output"):
                        st.code(result.stdout[-3000:])
                    
                    # Refresh reports list
                    if os.path.exists('outputs'):
                        st.info("New report generated in outputs/ folder")
                else:
                    st.error("❌ Dry run failed")
                    st.code(result.stderr)
    
    with col2:
        st.subheader("Real Email Mode")
        st.caption("Sends actual emails to contacts")
        st.warning("⚠️ Configure .env first!")
        
        if st.button("📧 Send Real Emails", use_container_width=True):
            if has_credentials:
                with st.spinner("Sending real emails..."):
                    result = subprocess.run(["python", "main.py"], capture_output=True, text=True)
                    if result.returncode == 0:
                        st.success("✅ Emails sent successfully!")
                        with st.expander("View Output"):
                            st.code(result.stdout[-3000:])
                    else:
                        st.error("❌ Sending failed")
                        st.code(result.stderr)
            else:
                st.error("❌ Cannot send real emails. Configure .env file first.")
    
    # View logs
    st.markdown("---")
    st.subheader("System Logs")
    
    if os.path.exists('logs/email_system.log'):
        with open('logs/email_system.log', 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        log_level = st.selectbox("Log Level", ["All", "INFO", "ERROR", "WARNING"])
        
        filtered_lines = lines
        if log_level != "All":
            filtered_lines = [l for l in lines if log_level in l]
        
        st.code(''.join(filtered_lines[-50:]))
    else:
        st.info("No logs yet")

# Footer
st.markdown("---")
st.markdown("### 📧 Email Automation & Reminder System")
st.caption("Built with Python, Streamlit, and SMTP")