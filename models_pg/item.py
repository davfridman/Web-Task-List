from database_pg import get_db_connection
import psycopg2.extras

class Item:
    def __init__(self, name, quantity, id=None, notes=None, who_needs_it=None, who_will_buy_it=None, category_id=None, display_order=0, is_completed=False):
        self.id = id
        self.name = name
        self.quantity = quantity
        self.notes = notes
        self.who_needs_it = who_needs_it
        self.who_will_buy_it = who_will_buy_it
        self.category_id = category_id
        self.display_order = display_order
        self.is_completed = is_completed

    def save(self):
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Ensure category_id is set, defaulting to 1 ('Other') if not specified
        self.category_id = self.category_id or 1

        if self.id:
            # Update existing item
            cursor.execute(
                'UPDATE items SET name = %s, quantity = %s, notes = %s, who_needs_it = %s, who_will_buy_it = %s, category_id = %s, is_completed = %s WHERE id = %s',
                (self.name, self.quantity, self.notes, self.who_needs_it, self.who_will_buy_it, self.category_id, self.is_completed, self.id)
            )
        else:
            # Insert new item
            cursor.execute('SELECT MAX(display_order) FROM items WHERE category_id = %s', (self.category_id,))
            max_order = cursor.fetchone()[0]
            self.display_order = (max_order or 0) + 1
            
            cursor.execute(
                'INSERT INTO items (name, quantity, notes, who_needs_it, who_will_buy_it, category_id, display_order, is_completed) VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING id',
                (self.name, self.quantity, self.notes, self.who_needs_it, self.who_will_buy_it, self.category_id, self.display_order, self.is_completed)
            )
            self.id = cursor.fetchone()[0]
            
        conn.commit()
        cursor.close()
        conn.close()

    @staticmethod
    def get_all_for_list(list_id):
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cursor.execute('''
            SELECT
                i.id, i.name, i.quantity, i.notes, i.who_needs_it, i.who_will_buy_it,
                i.is_completed, i.display_order,
                c.id as category_id, c.name as category_name
            FROM items i
            JOIN categories c ON i.category_id = c.id
            WHERE i.is_deleted = FALSE AND c.list_id = %s
            ORDER BY c.display_order, i.display_order
        ''', (list_id,))
        items = cursor.fetchall()
        cursor.close()
        conn.close()
        return items
    
    @staticmethod
    def get_by_id(item_id):
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cursor.execute('SELECT * FROM items WHERE id = %s', (item_id,))
        item_data = cursor.fetchone()
        cursor.close()
        conn.close()
        if item_data:
            return Item(**item_data)
        return None
        
    @staticmethod
    def update(item_id, name, quantity, notes, who_needs_it, who_will_buy_it, category_id, is_completed):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            'UPDATE items SET name = %s, quantity = %s, notes = %s, who_needs_it = %s, who_will_buy_it = %s, category_id = %s, is_completed = %s WHERE id = %s',
            (name, quantity, notes, who_needs_it, who_will_buy_it, category_id, is_completed, item_id)
        )
        conn.commit()
        cursor.close()
        conn.close()
    
    @staticmethod
    def update_name(item_id, name):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('UPDATE items SET name = %s WHERE id = %s', (name, item_id))
        conn.commit()
        cursor.close()
        conn.close()

    @staticmethod
    def toggle_completed(item_id, is_completed):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('UPDATE items SET is_completed = %s WHERE id = %s', (is_completed, item_id))
        conn.commit()
        cursor.close()
        conn.close()

    @staticmethod
    def clear_completed(list_id):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE items SET is_deleted = TRUE 
            WHERE is_completed = TRUE AND category_id IN 
            (SELECT id FROM categories WHERE list_id = %s)
        ''', (list_id,))
        conn.commit()
        cursor.close()
        conn.close()
        
    @staticmethod
    def update_order_and_category(item_id, new_category_id, sibling_ids):
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('UPDATE items SET category_id = %s WHERE id = %s', (new_category_id, item_id))
        
        for index, sibling_id in enumerate(sibling_ids):
            cursor.execute('UPDATE items SET display_order = %s WHERE id = %s', (index, sibling_id))
            
        conn.commit()
        cursor.close()
        conn.close()

    @staticmethod
    def delete(item_id):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('UPDATE items SET is_deleted = TRUE WHERE id = %s', (item_id,))
        conn.commit()
        cursor.close()
        conn.close()
