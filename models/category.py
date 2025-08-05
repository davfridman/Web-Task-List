from database import get_db_connection

class Category:
    def __init__(self, name, list_id, id=None, display_order=0):
        self.id = id
        self.name = name
        self.list_id = list_id
        self.display_order = display_order

    def save(self):
        conn = get_db_connection()
        max_order = conn.execute('SELECT MAX(display_order) FROM categories WHERE list_id = ?', (self.list_id,)).fetchone()[0] or 0
        self.display_order = max_order + 1
        cursor = conn.cursor()
        cursor.execute('INSERT INTO categories (name, display_order, list_id) VALUES (?, ?, ?)', (self.name, self.display_order, self.list_id))
        self.id = cursor.lastrowid
        conn.commit()
        conn.close()

    @staticmethod
    def get_all_for_list(list_id):
        conn = get_db_connection()
        categories = conn.execute('SELECT * FROM categories WHERE list_id = ? ORDER BY display_order', (list_id,)).fetchall()
        conn.close()
        return [Category(cat['name'], cat['list_id'], cat['id'], cat['display_order']) for cat in categories]
    
    @staticmethod
    def get_by_id(category_id):
        conn = get_db_connection()
        category = conn.execute('SELECT * FROM categories WHERE id = ?', (category_id,)).fetchone()
        conn.close()
        if category:
            return Category(category['name'], category['list_id'], category['id'], category['display_order'])
        return None

    @staticmethod
    def update(category_id, new_name):
        conn = get_db_connection()
        conn.execute('UPDATE categories SET name = ? WHERE id = ?', (new_name, category_id))
        conn.commit()
        conn.close()

    @staticmethod
    def update_order(category_ids):
        conn = get_db_connection()
        cursor = conn.cursor()
        for index, category_id in enumerate(category_ids):
            cursor.execute('UPDATE categories SET display_order = ? WHERE id = ?', (index, category_id))
        conn.commit()
        conn.close()

    @staticmethod
    def delete(category_id):
        conn = get_db_connection()
        # Find the "Other" category for the same list
        category_to_delete = Category.get_by_id(category_id)
        if not category_to_delete or category_to_delete.name == 'Other':
            return # Or handle error appropriately

        other = conn.execute('SELECT id FROM categories WHERE name = "Other" AND list_id = ?', (category_to_delete.list_id,)).fetchone()
        if other:
            other_id = other['id']
            # Move items to the "Other" category before deleting
            conn.execute('UPDATE items SET category_id = ? WHERE category_id = ?', (other_id, category_id))
        
        conn.execute('DELETE FROM categories WHERE id = ?', (category_id,))
        conn.commit()
        conn.close()
