import sqlite3

def get_db_connection():
    conn = sqlite3.connect('shopping_list.db')
    conn.row_factory = sqlite3.Row
    return conn

def create_tables():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Enable foreign key support
    cursor.execute("PRAGMA foreign_keys = ON")

    # Create shopping_lists table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS shopping_lists (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL
    )''')

    # Create categories table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS categories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        display_order INTEGER,
        list_id INTEGER NOT NULL,
        FOREIGN KEY (list_id) REFERENCES shopping_lists (id) ON DELETE CASCADE
    )''')

    # Create items table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        quantity INTEGER NOT NULL,
        notes TEXT,
        who_needs_it TEXT,
        who_will_buy_it TEXT,
        is_deleted INTEGER DEFAULT 0,
        is_completed INTEGER DEFAULT 0,
        category_id INTEGER,
        display_order INTEGER,
        FOREIGN KEY (category_id) REFERENCES categories (id) ON DELETE CASCADE
    )''')

    # Create a default list if none exist
    cursor.execute("INSERT OR IGNORE INTO shopping_lists (id, name) VALUES (1, 'Main List')")
    
    # Create a default "Other" category for the default list if none exists
    cursor.execute("INSERT OR IGNORE INTO categories (id, name, display_order, list_id) VALUES (1, 'Other', 99999, 1)")

    conn.commit()
    conn.close()
