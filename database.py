import sqlite3
import json
from datetime import datetime
from dotenv import load_dotenv

load_dotenv(override=True)

DB = "accounts.db"


with sqlite3.connect(DB) as conn:
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS accounts (name TEXT PRIMARY KEY, account TEXT)')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            datetime DATETIME,
            type TEXT,
            message TEXT
        )
    ''')
    cursor.execute('CREATE TABLE IF NOT EXISTS market (date TEXT PRIMARY KEY, data TEXT)')
    conn.commit()

def write_account(name, account_dict):
    json_data = json.dumps(account_dict)
    with sqlite3.connect(DB) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO accounts (name, account)
            VALUES (?, ?)
            ON CONFLICT(name) DO UPDATE SET account=excluded.account
        ''', (name.lower(), json_data))
        conn.commit()

def read_account(name):
    with sqlite3.connect(DB) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT account FROM accounts WHERE name = ?', (name.lower(),))
        row = cursor.fetchone()
        return json.loads(row[0]) if row else None
    
def write_log(name: str, type: str, message: str):
    """
    Write a log entry to the logs table.
    
    Args:
        name (str): The name associated with the log
        type (str): The type of log entry
        message (str): The log message
    """
    now = datetime.now().isoformat()
    
    with sqlite3.connect(DB) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO logs (name, datetime, type, message)
            VALUES (?, datetime('now'), ?, ?)
        ''', (name.lower(), type, message))
        conn.commit()

def read_log(name: str, last_n=10):
    """
    Read the most recent log entries for a given name.
    
    Args:
        name (str): The name to retrieve logs for
        last_n (int): Number of most recent entries to retrieve
        
    Returns:
        list: A list of tuples containing (datetime, type, message)
    """
    with sqlite3.connect(DB) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT datetime, type, message FROM logs 
            WHERE name = ? 
            ORDER BY datetime DESC
            LIMIT ?
        ''', (name.lower(), last_n))
        
        return reversed(cursor.fetchall())

def read_log_prioritized(name: str, last_n=10):
    """
    Read log entries prioritizing account logs (trading transactions) over trace logs.
    
    Args:
        name (str): The name to retrieve logs for
        last_n (int): Number of most recent entries to retrieve
        
    Returns:
        list: A list of tuples containing (datetime, type, message)
    """
    with sqlite3.connect(DB) as conn:
        cursor = conn.cursor()
        
        # First get recent account logs (trading transactions)
        cursor.execute('''
            SELECT datetime, type, message FROM logs 
            WHERE name = ? AND type = 'account'
            ORDER BY datetime DESC
            LIMIT ?
        ''', (name.lower(), last_n))
        
        account_logs = cursor.fetchall()
        remaining_slots = last_n - len(account_logs)
        
        if remaining_slots > 0:
            # Fill remaining slots with other log types
            cursor.execute('''
                SELECT datetime, type, message FROM logs 
                WHERE name = ? AND type != 'account'
                ORDER BY datetime DESC
                LIMIT ?
            ''', (name.lower(), remaining_slots))
            
            other_logs = cursor.fetchall()
            all_logs = account_logs + other_logs
        else:
            all_logs = account_logs
        
        # Sort by datetime descending and return reversed for chronological order
        all_logs.sort(key=lambda x: x[0], reverse=True)
        return reversed(all_logs)

def read_mcp_tool_logs(name: str, last_n=10):
    """
    Read the most recent MCP tool call logs for a given name.
    
    Args:
        name (str): The name to retrieve logs for
        last_n (int): Number of most recent entries to retrieve
        
    Returns:
        list: A list of tuples containing (datetime, type, message)
    """
    with sqlite3.connect(DB) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT datetime, type, message FROM logs 
            WHERE name = ? AND type = 'mcp_tool'
            ORDER BY datetime DESC
            LIMIT ?
        ''', (name.lower(), last_n))
        
        return reversed(cursor.fetchall())

def write_market(date: str, data: dict) -> None:
    data_json = json.dumps(data)
    with sqlite3.connect(DB) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO market (date, data)
            VALUES (?, ?)
            ON CONFLICT(date) DO UPDATE SET data=excluded.data
        ''', (date, data_json))
        conn.commit()

def read_market(date: str) -> dict | None:
    with sqlite3.connect(DB) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT data FROM market WHERE date = ?', (date,))
        row = cursor.fetchone()
        return json.loads(row[0]) if row else None