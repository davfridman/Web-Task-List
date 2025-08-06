from database_pg import get_db_connection
import psycopg2.extras

class Category:
    def __init__(self, name, list_id, id=None, display_order=0):
        self.id = id
        self.name = name
        self.list_id = list_id
        self.display_order = display_order

    def save(self):
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Determine the display order for the new category
        cursor.execute('SELECT MAX(display_order) FROM categories WHERE list_id = %s', (self.list_id,))
        max_order = cursor.fetchone()[0]
        self.display_order = (max_order or 0) + 1
        
        # Insert the new category and get its ID back
        cursor.execute(
            'INSERT INTO categories (name, display_order, list_id) VALUES (%s, %s, %s) RETURNING id',
            (self.name, self.display_order, self.list_id)
        )
        self.id = cursor.fetchone()[0]
        
        conn.commit()
        cursor.close()
        conn.close()

    @staticmethod
    def get_all_for_list(list_id):
        conn = get_db_connection()
        # Use DictCursor to get dictionary-like rows
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cursor.execute('SELECT * FROM categories WHERE list_id = %s ORDER BY display_order', (list_id,))
        categories = cursor.fetchall()
        cursor.close()
        conn.close()
        # Re-create Category objects from the fetched data
        return [Category(cat['name'], cat['list_id'], cat['id'], cat['display_order']) for cat in categories]
    
    @staticmethod
    def get_by_id(category_id):
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cursor.execute('SELECT * FROM categories WHERE id = %s', (category_id,))
        category_data = cursor.fetchone()
        cursor.close()
        conn.close()
        if category_data:
            return Category(category_data['name'], category_data['list_id'], category_data['id'], category_data['display_order'])
        return None

    @staticmethod
    def update(category_id, new_name):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('UPDATE categories SET name = %s WHERE id = %s', (new_name, category_id))
        conn.commit()
        cursor.close()
        conn.close()

    @staticmethod
    def update_order(category_ids):
        conn = get_db_connection()
        cursor = conn.cursor()
        for index, category_id in enumerate(category_ids):
            cursor.execute('UPDATE categories SET display_order = %s WHERE id = %s', (index, category_id))
        conn.commit()
        cursor.close()
        conn.close()

    @staticmethod
    def delete(category_id):
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        
        # First, get the list_id of the category being deleted
        cursor.execute('SELECT list_id, name FROM categories WHERE id = %s', (category_id,))
        category_to_delete = cursor.fetchone()

        if not category_to_delete or category_to_delete['name'] == 'Other':
            cursor.close()
            conn.close()
            return # Cannot delete the "Other" category

        list_id = category_to_delete['list_id']
        
        # Find the "Other" category for that same list
        cursor.execute('SELECT id FROM categories WHERE name = %s AND list_id = %s', ('Other', list_id))
        other_category = cursor.fetchone()
        
        if other_category:
            other_id = other_category['id']
            # Move all items from the deleted category to the "Other" category
            cursor.execute('UPDATE items SET category_id = %s WHERE category_id = %s', (other_id, category_id))
        
        # Finally, delete the category itself
        cursor.execute('DELETE FROM categories WHERE id = %s', (category_id,))
        
        conn.commit()
        cursor.close()
        conn.close()
