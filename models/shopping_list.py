from database import get_db_connection

class ShoppingList:
    def __init__(self, name, id=None):
        self.id = id
        self.name = name

    def save(self):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO shopping_lists (name) VALUES (?)', (self.name,))
        self.id = cursor.lastrowid
        conn.commit()
        conn.close()

    @staticmethod
    def get_all():
        conn = get_db_connection()
        lists = conn.execute('SELECT * FROM shopping_lists').fetchall()
        conn.close()
        return [ShoppingList(l['name'], l['id']) for l in lists]

    @staticmethod
    def get_by_id(list_id):
        conn = get_db_connection()
        list_data = conn.execute('SELECT * FROM shopping_lists WHERE id = ?', (list_id,)).fetchone()
        conn.close()
        if list_data:
            return ShoppingList(list_data['name'], list_data['id'])
        return None

    @staticmethod
    def update_name(list_id, new_name):
        conn = get_db_connection()
        conn.execute('UPDATE shopping_lists SET name = ? WHERE id = ?', (new_name, list_id))
        conn.commit()
        conn.close()

    @staticmethod
    def delete(list_id):
        conn = get_db_connection()
        conn.execute('DELETE FROM shopping_lists WHERE id = ?', (list_id,))
        conn.commit()
        conn.close()
