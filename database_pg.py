import os
import psycopg2
import psycopg2.extras
import urllib.parse as up

def get_db_connection():
    up.uses_netloc.append("postgres")
    # In a production environment (like on Render), DATABASE_URL will be set.
    # For local development, you might have a different way to connect,
    # but for deployment, this is the standard.
    if "DATABASE_URL" not in os.environ:
        raise RuntimeError("DATABASE_URL is not set. This configuration is for production.")

    url = up.urlparse(os.environ["DATABASE_URL"])
    conn = psycopg2.connect(
        database=url.path[1:],
        user=url.username,
        password=url.password,
        host=url.hostname,
        port=url.port
    )
    return conn

def create_tables():
    """Creates the necessary tables in the PostgreSQL database."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Create shopping_lists table with SERIAL for auto-incrementing primary key
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS shopping_lists (
        id SERIAL PRIMARY KEY,
        name TEXT NOT NULL
    )''')

    # Create categories table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS categories (
        id SERIAL PRIMARY KEY,
        name TEXT NOT NULL,
        display_order INTEGER,
        list_id INTEGER NOT NULL,
        FOREIGN KEY (list_id) REFERENCES shopping_lists (id) ON DELETE CASCADE
    )''')

    # Create items table with BOOLEAN for is_deleted and is_completed
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS items (
        id SERIAL PRIMARY KEY,
        name TEXT NOT NULL,
        quantity INTEGER NOT NULL,
        notes TEXT,
        who_needs_it TEXT,
        who_will_buy_it TEXT,
        is_deleted BOOLEAN DEFAULT FALSE,
        is_completed BOOLEAN DEFAULT FALSE,
        category_id INTEGER,
        display_order INTEGER,
        FOREIGN KEY (category_id) REFERENCES categories (id) ON DELETE CASCADE
    )''')

    # Use ON CONFLICT to safely insert default data
    cursor.execute("INSERT INTO shopping_lists (id, name) VALUES (1, 'Main List') ON CONFLICT (id) DO NOTHING")
    
    cursor.execute("INSERT INTO categories (id, name, display_order, list_id) VALUES (1, 'Other', 99999, 1) ON CONFLICT (id) DO NOTHING")

    conn.commit()
    cursor.close()
    conn.close()
