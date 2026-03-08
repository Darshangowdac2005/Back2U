# backend/utils/notification.py

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv

from config.db_connector import db
from models.notification_model import Notification

load_dotenv()

def get_user_email(user_id, cursor=None):
    """Fetches user email and name from the database."""
    should_close = False
    if cursor is None:
        cursor = db.get_cursor(dictionary=True)
        should_close = True
        
    try:
        cursor.execute("SELECT email, name FROM Users WHERE user_id = %s", (user_id,))
        user = cursor.fetchone()
        if should_close:
            cursor.close()
            
        if not user:
            print(f"Warning: User with ID {user_id} not found.")
            return None
        return user
    except Exception as e:
        print(f"Error fetching user {user_id}: {e}")
        if should_close:
             try: cursor.close()
             except: pass
        return None

def send_email(recipient_email, subject, body, server=None):
    """Handles SMTP connection and sends the email. If server is provided, uses it."""
    # Skip email sending if credentials not configured
    sender_email = os.getenv('EMAIL_SENDER')
    email_host = os.getenv('EMAIL_HOST')
    email_user = os.getenv('EMAIL_USER')
    email_pass = os.getenv('EMAIL_PASS')

    if not all([sender_email, email_host, email_user, email_pass]):
        missing = []
        if not sender_email: missing.append('EMAIL_SENDER')
        if not email_host: missing.append('EMAIL_HOST')
        if not email_user: missing.append('EMAIL_USER')
        if not email_pass: missing.append('EMAIL_PASS')
        print(f"Email credentials not configured. Missing: {', '.join(missing)}")
        print(f"Would have sent to {recipient_email}: {subject}")
        return True  # Return True to continue flow
    
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    own_server = False
    try:
        if server is None:
            own_server = True
            log_msg = f"Connecting to {email_host}:{os.getenv('EMAIL_PORT', 587)}..."
            print(log_msg)
            with open("email_debug.log", "a") as f: f.write(f"DEBUG: {log_msg}\n")
            
            server = smtplib.SMTP(email_host, int(os.getenv('EMAIL_PORT', 587)), timeout=10)
            server.starttls()  
            
            log_msg = f"Logging in as {email_user}..."
            print(log_msg)
            with open("email_debug.log", "a") as f: f.write(f"DEBUG: {log_msg}\n")
            server.login(email_user, email_pass)
        
        log_msg = f"Sending email to {recipient_email}..."
        print(log_msg)
        with open("email_debug.log", "a") as f: f.write(f"DEBUG: {log_msg}\n")
        server.sendmail(sender_email, recipient_email, msg.as_string())
        
        if own_server:
            server.quit()
        
        with open("email_debug.log", "a") as f:
            f.write(f"SUCCESS: Sent to {recipient_email}\n")
        return True
    except Exception as e:
        error_msg = f"ERROR sending email to {recipient_email}: {e}"
        print(error_msg)
        with open("email_debug.log", "a") as f:
            f.write(f"{error_msg}\n")
        # If we failed on our own connection, try to close it
        if own_server and server:
            try: server.quit()
            except: pass
        return False

def insert_notification(user_id, message, notification_type):
    """Logs the notification in the database."""
    # Note: This uses the global db, which is fine for main thread but NOT for background threads.
    # Background threads should use custom insertion logic as implemented in send_claim_resolved_emails.
    cursor = db.get_cursor()
    query = "INSERT INTO Notifications (user_id, message, type, status) VALUES (%s, %s, %s, %s)"
    cursor.execute(query, (user_id, message, notification_type, Notification.STATUSES['SENT']))
    db.conn.commit()
    cursor.close()

def log_debug(msg):
    with open("crash_debug.log", "a") as f:
        f.write(f"{msg}\n")

def send_claim_resolved_emails(item_id, claimant_id, admin_id):
    """
    Sends resolution emails to both the reporter and the claimant.
    Uses the thread-safe db singleton and a single SMTP connection.
    """
    log_debug(f"Starting send_claim_resolved_emails for Item {item_id}")
    
    try:
        log_debug("Getting cursor from thread-local db...")
        cursor = db.get_cursor(dictionary=True)
        
        # 1. Get Item Reporter (Original Lost/Found User)
        log_debug("Fetching item info...")
        cursor.execute("SELECT reported_by, title FROM Items WHERE item_id = %s", (item_id,))
        item_info = cursor.fetchone()
        
        if not item_info:
            print(f"Warning: Item with ID {item_id} not found.")
            log_debug("Item not found.")
            cursor.close()
            return
            
        reporter_id = item_info['reported_by']
        item_title = item_info['title']

        # Pass our thread-local cursor
        log_debug(f"Fetching reporter {reporter_id}...")
        reporter = get_user_email(reporter_id, cursor=cursor)
        log_debug(f"Fetching claimant {claimant_id}...")
        claimant = get_user_email(claimant_id, cursor=cursor)

        log_debug("Closing cursor...")
        cursor.close()

        if not reporter or not claimant:
            print("Warning: Missing user data for reporter or claimant. Skipping email notifications.")
            log_debug("Missing user data.")
            return

        # Prepare messages
        reporter_subject = f"SUCCESS: Your Item '{item_title}' Has Been RESOLVED!"
        reporter_body = f"Hello {reporter['name']},\n\nGood news! Your item, '{item_title}', has been verified by the Admin (ID: {admin_id}) and matched with the person who found it. Please contact the claimant, {claimant['name']}, to arrange collection. Your contact details have been shared with them."

        claimant_subject = f"SUCCESS: Your Claim on '{item_title}' Has Been APPROVED!"
        claimant_body = f"Hello {claimant['name']},\n\nYour claim on '{item_title}' has been successfully approved! Please contact the original reporter, {reporter['name']}, to arrange the return of the item. Their email is {reporter['email']}."

        # Setup one SMTP connection for both
        email_host = os.getenv('EMAIL_HOST')
        email_user = os.getenv('EMAIL_USER')
        email_pass = os.getenv('EMAIL_PASS')
        email_port = int(os.getenv('EMAIL_PORT', 587))
        
        server = None
        if all([email_host, email_user, email_pass]):
            try:
                log_debug("Opening single SMTP connection...")
                server = smtplib.SMTP(email_host, email_port, timeout=10)
                server.starttls()
                server.login(email_user, email_pass)
            except Exception as e:
                log_debug(f"Failed to open SMTP connection: {e}")
                server = None

        # Send to Reporter
        log_debug("Sending email to reporter...")
        rep_sent = False
        if server:
            rep_sent = send_email(reporter['email'], reporter_subject, reporter_body, server=server)
        
        # ALWAYS insert notification for reporter
        try:
            log_debug("Inserting notification for reporter...")
            cursor_notif = db.get_cursor()
            query = "INSERT INTO Notifications (user_id, message, type, status) VALUES (%s, %s, %s, %s)"
            status = Notification.STATUSES['SENT'] if rep_sent else Notification.STATUSES['PENDING']
            cursor_notif.execute(query, (reporter_id, f"Item '{item_title}' successfully matched and resolved. Check your email for details!", Notification.TYPES['EMAIL'], status))
            db.conn.commit()
            cursor_notif.close()
            log_debug("Notification inserted.")
        except Exception as e:
            log_debug(f"Error inserting reporter notification: {e}")

        # Send to Claimant
        log_debug("Sending email to claimant...")
        cla_sent = False
        if server:
            cla_sent = send_email(claimant['email'], claimant_subject, claimant_body, server=server)
        
        # ALWAYS insert notification for claimant
        try:
            log_debug("Inserting notification for claimant...")
            cursor_notif = db.get_cursor()
            query = "INSERT INTO Notifications (user_id, message, type, status) VALUES (%s, %s, %s, %s)"
            status = Notification.STATUSES['SENT'] if cla_sent else Notification.STATUSES['PENDING']
            cursor_notif.execute(query, (claimant_id, f"Claim on '{item_title}' approved. Check your email for reporter's contact info.", Notification.TYPES['EMAIL'], status))
            db.conn.commit()
            cursor_notif.close()
            log_debug("Notification inserted.")
        except Exception as e:
            log_debug(f"Error inserting claimant notification: {e}")

        if server:
            try: server.quit()
            except: pass

    except Exception as e:
        print(f"Error in send_claim_resolved_emails (background): {e}")
        log_debug(f"CRASH: {e}")
    finally:
        db.close()


