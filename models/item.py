from database import get_db_connection

class Item:
    def __init__(self, name, quantity, id=None, notes=None, who_needs_it=None, who_will_buy_it=None, category_id=None, display_order=0, is_completed=0):
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
        if self.id:
            conn.execute(
                'UPDATE items SET name = ?, quantity = ?, notes = ?, who_needs_it = ?, who_will_buy_it = ?, category_id = ?, is_completed = ? WHERE id = ?',
                (self.name, self.quantity, self.notes, self.who_needs_it, self.who_will_buy_it, self.category_id, self.is_completed, self.id)
            )
        else:
            max_order = conn.execute('SELECT MAX(display_order) FROM items WHERE category_id = ?', (self.category_id,)).fetchone()[0] or 0
            self.display_order = max_order + 1
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO items (name, quantity, notes, who_needs_it, who_will_buy_it, category_id, display_order) VALUES (?, ?, ?, ?, ?, ?, ?)',
                (self.name, self.quantity, self.notes, self.who_needs_it, self.who_will_buy_it, self.category_id, self.display_order)
            )
            self.id = cursor.lastrowid
        conn.commit()
        conn.close()

    @staticmethod
    def get_all_for_list(list_id):
        conn = get_db_connection()
        items_with_categories = conn.execute('''
            SELECT
                i.id, i.name, i.quantity, i.notes, i.who_needs_it, i.who_will_buy_it,
                i.is_completed, i.display_order,
                c.id as category_id, c.name as category_name
            FROM items i
            JOIN categories c ON i.category_id = c.id
            WHERE i.is_deleted = 0 AND c.list_id = ?
            ORDER BY c.display_order, i.display_order
        ''', (list_id,)).fetchall()
        conn.close()
        return items_with_categories
    
    @staticmethod
    def get_by_id(item_id):
        conn = get_db_connection()
        item = conn.execute('SELECT * FROM items WHERE id = ?', (item_id,)).fetchone()
        conn.close()
        if item:
            return Item(item['name'], item['quantity'], item['id'], item['notes'], item['who_needs_it'], item['who_will_buy_it'], item['category_id'], item['display_order'], item['is_completed'])
        return None
        
    @staticmethod
    def update(item_id, name, quantity, notes, who_needs_it, who_will_buy_it, category_id, is_completed):
        conn = get_db_connection()
        conn.execute(
            'UPDATE items SET name = ?, quantity = ?, notes = ?, who_needs_it = ?, who_will_buy_it = ?, category_id = ?, is_completed = ? WHERE id = ?',
            (name, quantity, notes, who_needs_it, who_will_buy_it, category_id, is_completed, item_id)
        )
        conn.commit()
        conn.close()
    
    @staticmethod
    def update_name(item_id, name):
        conn = get_db_connection()
        conn.execute('UPDATE items SET name = ? WHERE id = ?', (name, item_id))
        conn.commit()
        conn.close()

    @staticmethod
    def toggle_completed(item_id, is_completed):
        conn = get_db_connection()
        conn.execute('UPDATE items SET is_completed = ? WHERE id = ?', (is_completed, item_id))
        conn.commit()
        conn.close()

    @staticmethod
    def clear_completed(list_id):
        conn = get_db_connection()
        conn.execute('''
            UPDATE items SET is_deleted = 1 
            WHERE is_completed = 1 AND category_id IN 
            (SELECT id FROM categories WHERE list_id = ?)
        ''', (list_id,))
        conn.commit()
        conn.close()
        
    @staticmethod
    def update_order_and_category(item_id, new_category_id, sibling_ids):
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('UPDATE items SET category_id = ? WHERE id = ?', (new_category_id, item_id))
        
        for index, sibling_id in enumerate(sibling_ids):
            cursor.execute('UPDATE items SET display_order = ? WHERE id = ?', (index, sibling_id))
            
        conn.commit()
        conn.close()

    @staticmethod
    def delete(item_id):
        conn = get_db_connection()
        conn.execute('UPDATE items SET is_deleted = 1 WHERE id = ?', (item_id,))
        conn.commit()
        conn.close()
