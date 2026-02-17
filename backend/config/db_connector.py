import mysql.connector
import os
from dotenv import load_dotenv
from utils.security import hash_password

load_dotenv()

# Configuration from .env file
db_config = {
    'host': os.getenv('MYSQL_HOST'),
    'user': os.getenv('MYSQL_USER'),
    'password': os.getenv('MYSQL_PASSWORD'),
    'database': os.getenv('MYSQL_DB'),
    'use_pure': True,
    'ssl_disabled': True
}

# If database doesn't exist, connect without it first
try:
    db_config_temp = db_config.copy()
    del db_config_temp['database']
    temp_conn = mysql.connector.connect(**db_config_temp)
    temp_cursor = temp_conn.cursor()
    temp_cursor.execute("CREATE DATABASE IF NOT EXISTS back2u")
    temp_conn.commit()
    temp_cursor.close()
    temp_conn.close()
    print("✅ Database 'back2u' created successfully!")
except mysql.connector.Error as err:
    print(f"❌ Error creating database: {err}")
    exit(1)

import threading

class Database:
    def __init__(self):
        self._local = threading.local()

    def connect(self):
        """Creates a new connection for the current thread."""
        try:
            conn = mysql.connector.connect(**db_config)
            print(f"✅ MySQL Database connected successfully in thread {threading.get_ident()}!")
            return conn
        except mysql.connector.Error as err:
            print(f"❌ Error connecting to MySQL: {err}")
            return None

    @property
    def conn(self):
        if not hasattr(self._local, 'conn') or self._local.conn is None:
            self._local.conn = self.connect()
        return self._local.conn

    def get_cursor(self, dictionary=False):
        try:
            if self.conn:
                self.conn.ping(reconnect=True)
            else:
                self._local.conn = self.connect()
        except mysql.connector.Error:
            print("Connection lost, reconnecting...")
            self._local.conn = self.connect()
            
        if self.conn:
            return self.conn.cursor(dictionary=dictionary)
        else:
            raise Exception("Failed to establish database connection")

    def close(self):
        if hasattr(self._local, 'conn') and self._local.conn:
            try:
                self._local.conn.close()
                self._local.conn = None
            except:
                pass

db = Database()
# Note: No global db.connect() here, it will connect on demand per thread.


def create_tables_and_seed():
    cursor = db.get_cursor()
    item_ids = []
    
    # --- 1. Users Table ---
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Users (
            user_id INT PRIMARY KEY AUTO_INCREMENT,
            name VARCHAR(100) NOT NULL,
            email VARCHAR(100) UNIQUE NOT NULL,
            role ENUM('student', 'faculty', 'admin') NOT NULL DEFAULT 'student',
            password_hash VARCHAR(255) NOT NULL
        )
    """)
    
    # --- 2. Categories Table ---
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Categories (
            category_id INT PRIMARY KEY AUTO_INCREMENT,
            name VARCHAR(50) UNIQUE NOT NULL
        )
    """)
    
    # --- 3. Items Table ---
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Items (
            item_id INT PRIMARY KEY AUTO_INCREMENT,
            reported_by INT NOT NULL,
            category_id INT NOT NULL,
            title VARCHAR(100) NOT NULL,
            description TEXT,
            status ENUM('lost', 'found', 'claim_pending', 'resolved') NOT NULL,
            date_reported DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (reported_by) REFERENCES Users(user_id),
            FOREIGN KEY (category_id) REFERENCES Categories(category_id)
        )
    """)
    
    # --- 4. Claims Table ---
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Claims (
            claim_id INT PRIMARY KEY AUTO_INCREMENT,
            item_id INT NOT NULL,
            claimant_id INT NOT NULL,
            claim_status ENUM('pending', 'approved', 'rejected') NOT NULL DEFAULT 'pending',
            verification_details TEXT,
            claimed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (item_id) REFERENCES Items(item_id),
            FOREIGN KEY (claimant_id) REFERENCES Users(user_id)
        )
    """)
    
    # --- 5. Notifications Table ---
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Notifications (
            notification_id INT PRIMARY KEY AUTO_INCREMENT,
            user_id INT NOT NULL, 
            message TEXT NOT NULL,
            type ENUM('email', 'system') NOT NULL,
            status ENUM('sent', 'pending', 'read') NOT NULL DEFAULT 'pending',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES Users(user_id)
        )
    """)
    
    # --- Add the MySQL trigger to update Items.status when a claim is approved ---
    try:
        cursor.execute("DROP TRIGGER IF EXISTS update_item_status_on_claim_approval")
        cursor.execute("""
            CREATE TRIGGER update_item_status_on_claim_approval
            AFTER UPDATE ON Claims
            FOR EACH ROW
            BEGIN
                IF NEW.claim_status = 'approved' THEN
                    UPDATE Items SET status = 'resolved' WHERE item_id = NEW.item_id;
                END IF;
            END;
        """)
        print("✅ Trigger 'update_item_status_on_claim_approval' created successfully.")
    except mysql.connector.Error as err:
        print(f"❌ Failed to create trigger: {err}")
    
    # Seed categories if empty
    cursor.execute("SELECT COUNT(*) FROM Categories")
    count = cursor.fetchone()[0]
    print(f"Categories table has {count} entries.")
    if count == 0:
        categories = ['Electronics', 'Clothing', 'Books', 'Accessories', 'Other']
        print(f"🌱 Seeding {len(categories)} default categories...")
        for cat in categories:
            try:
                cursor.execute("INSERT INTO Categories (name) VALUES (%s)", (cat,))
                print(f"✅ Inserted category: {cat}")
            except mysql.connector.Error as err:
                print(f"❌ Failed to insert category '{cat}': {err}")
                # Continue with other categories even if one fails
        print("Category seeding completed.")
    else:
        print("✅ Categories already seeded.")

    # Only ensure tables exist; do not insert any sample data
    db.conn.commit()
    cursor.close()
    print("✅ Database tables checked/created successfully.")
