"""
Database Manager - SQLite operations
"""
import sqlite3
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime
import json
import logging

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Handles SQLite database operations"""
    
    def __init__(self, db_path: str = "data/beverage_counts.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn: Optional[sqlite3.Connection] = None
        self._init_database()
        logger.info(f"Database initialized: {self.db_path}")
    
    def _init_database(self):
        """Initialize database schema"""
        self.conn = sqlite3.connect(str(self.db_path), check_same_thread=False)
        cursor = self.conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                start_time TIMESTAMP,
                end_time TIMESTAMP,
                camera_url TEXT,
                total_beverages INTEGER DEFAULT 0,
                total_alcoholic INTEGER DEFAULT 0,
                total_non_alcoholic INTEGER DEFAULT 0
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS detections (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id INTEGER,
                timestamp TIMESTAMP,
                beverage_class TEXT,
                beverage_type TEXT,
                confidence REAL,
                bbox TEXT,
                FOREIGN KEY (session_id) REFERENCES sessions (id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS counts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id INTEGER,
                beverage_class TEXT,
                count INTEGER,
                FOREIGN KEY (session_id) REFERENCES sessions (id)
            )
        ''')
        
        self.conn.commit()
    
    def create_session(self, camera_url: str) -> int:
        cursor = self.conn.cursor()
        cursor.execute('INSERT INTO sessions (start_time, camera_url) VALUES (?, ?)',
                      (datetime.now(), camera_url))
        self.conn.commit()
        return cursor.lastrowid
    
    def end_session(self, session_id: int, stats: Dict):
        cursor = self.conn.cursor()
        cursor.execute('''
            UPDATE sessions SET end_time = ?, total_beverages = ?, 
            total_alcoholic = ?, total_non_alcoholic = ? WHERE id = ?
        ''', (datetime.now(), stats.get('total_beverages', 0),
              stats.get('total_alcoholic', 0), stats.get('total_non_alcoholic', 0), session_id))
        self.conn.commit()
    
    def update_counts(self, session_id: int, counts: Dict):
        cursor = self.conn.cursor()
        cursor.execute('DELETE FROM counts WHERE session_id = ?', (session_id,))
        for class_name, count in counts.items():
            cursor.execute('INSERT INTO counts (session_id, beverage_class, count) VALUES (?, ?, ?)',
                          (session_id, class_name, count))
        self.conn.commit()
    
    def save_detection(self, session_id: int, detection: Dict):
        """Save a single detection event to database"""
        cursor = self.conn.cursor()
        bbox_str = ",".join(map(str, detection.get('bbox', [])))
        cursor.execute('''
            INSERT INTO detections (session_id, timestamp, beverage_class, beverage_type, confidence, bbox)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (session_id, datetime.now(), detection.get('class_name'), 
              detection.get('type'), detection.get('confidence'), bbox_str))
        self.conn.commit()
    
    def export_to_csv(self, session_id: int, output_path: str):
        import csv
        cursor = self.conn.cursor()
        
        # 1. Get Session Summary
        cursor.execute('''SELECT start_time, end_time, total_beverages, total_alcoholic, total_non_alcoholic 
                         FROM sessions WHERE id = ?''', (session_id,))
        session_data = cursor.fetchone()
        
        # 2. Get Detailed Detections
        cursor.execute('''SELECT timestamp, beverage_class, beverage_type, confidence, bbox
                         FROM detections WHERE session_id = ? ORDER BY timestamp''', (session_id,))
        detections = cursor.fetchall()
        
        # 3. Get Class Counts
        cursor.execute('SELECT beverage_class, count FROM counts WHERE session_id = ?', (session_id,))
        counts = cursor.fetchall()
        
        with open(output_path, 'w', newline='') as f:
            writer = csv.writer(f)
            
            # Write Header Info
            writer.writerow(['--- SESSION SUMMARY ---'])
            if session_data:
                writer.writerow(['Start Time', 'End Time', 'Total', 'Alcoholic', 'Non-Alcoholic'])
                writer.writerow(session_data)
            writer.writerow([])
            
            # Write Class Counts
            writer.writerow(['--- COUNTS BY TYPE ---'])
            writer.writerow(['Beverage Class', 'Total Count'])
            writer.writerows(counts)
            writer.writerow([])
            
            # Write Detailed Log
            writer.writerow(['--- DETAILED DETECTION LOG ---'])
            writer.writerow(['Timestamp', 'Beverage Class', 'Type', 'Confidence', 'Bounding Box (x1,y1,x2,y2)'])
            writer.writerows(detections)
    
    def close(self):
        if self.conn:
            self.conn.close()
