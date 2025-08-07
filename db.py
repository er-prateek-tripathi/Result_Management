# db.py - Handles database operations for Student Result System
import sqlite3

DB_NAME = "database.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        dob TEXT,
        class TEXT,
        section TEXT,
        roll TEXT UNIQUE,
        address TEXT
    )''')
    cur.execute('''CREATE TABLE IF NOT EXISTS scores (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        roll TEXT,
        sub1 INTEGER,
        sub2 INTEGER,
        sub3 INTEGER,
        total INTEGER,
        percent REAL,
        grade TEXT,
        FOREIGN KEY(roll) REFERENCES students(roll) ON DELETE CASCADE
    )''')
    cur.execute('''CREATE TABLE IF NOT EXISTS users (
        username TEXT PRIMARY KEY,
        password TEXT
    )''')
    cur.execute("INSERT OR IGNORE INTO users (username, password) VALUES (?, ?)", ("admin", "admin123"))
    conn.commit()
    conn.close()

def get_connection():
    return sqlite3.connect(DB_NAME)

def execute_query(query, params=()):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(query, params)
    conn.commit()
    conn.close()

def fetch_one(query, params=()):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(query, params)
    result = cur.fetchone()
    conn.close()
    return result

def fetch_all(query, params=()):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(query, params)
    results = cur.fetchall()
    conn.close()
    return results
# This code initializes the database for the Student Result Management System.
# It creates tables for students, scores, and users if they do not already exist.