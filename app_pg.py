import os
from flask import Flask, render_template, request, redirect, url_for, jsonify
from database_pg import create_tables
from models_pg.item import Item
from models_pg.category import Category

# Initialize the database and create tables if they don't exist
# This is safe to run on every startup because the function uses "IF NOT EXISTS".
create_tables()

app = Flask(__name__)

# In production, the SECRET_KEY should be set as an environment variable.
# The default value is for development and should not be used in production.
app.secret_key = os.environ.get('SECRET_KEY', 'dev_secret_key_change_for_production')

# --- Main Route ---
@app.route('/')
def index():
    # For now, we'll hardcode the list_id to 1, as per your database structure.
    # In the future, this could be dynamic if you add multi-list support.
    list_id = 1
    categories = Category.get_all_for_list(list_id)
    items = Item.get_all_for_list(list_id)
    
    # Organize items by category
    items_by_category = {cat.name: [] for cat in categories}
    for item in items:
        # The key for the dictionary should be the category name
        items_by_category[item['category_name']].append(item)
        
    return render_template('index.html', categories=categories, items_by_category=items_by_category)

# --- Category Endpoints ---
@app.route('/add_category', methods=['POST'])
def add_category():
    name = request.form.get('category_name')
    list_id = request.form.get('list_id', 1) # Default to list 1
    if name:
        Category(name=name, list_id=list_id).save()
    return redirect(url_for('index'))

@app.route('/category/<int:category_id>')
def get_category(category_id):
    category = Category.get_by_id(category_id)
    if category:
        return jsonify({'id': category.id, 'name': category.name, 'list_id': category.list_id})
    return jsonify({'error': 'Category not found'}), 404

@app.route('/update_category/<int:category_id>', methods=['POST'])
def update_category(category_id):
    new_name = request.json.get('name')
    if new_name:
        Category.update(category_id, new_name)
        return jsonify(success=True)
    return jsonify(success=False, error="New name is required"), 400

@app.route('/delete_category/<int:category_id>', methods=['POST'])
def delete_category(category_id):
    Category.delete(category_id)
    return jsonify(success=True)

@app.route('/update_category_order', methods=['POST'])
def update_category_order():
    category_ids = request.json.get('category_ids', [])
    if category_ids:
        Category.update_order(category_ids)
    return jsonify(success=True)

# --- Item Endpoints ---
@app.route('/add_item', methods=['POST'])
def add_item():
    item = Item(
        name=request.form.get('name'),
        quantity=int(request.form.get('quantity', 1)),
        notes=request.form.get('notes'),
        who_needs_it=request.form.get('who_needs_it'),
        who_will_buy_it=request.form.get('who_will_buy_it'),
        category_id=request.form.get('category_id') or None
    )
    item.save()
    return redirect(url_for('index'))

@app.route('/item/<int:item_id>')
def get_item(item_id):
    item = Item.get_by_id(item_id)
    if item:
        return jsonify({
            'id': item.id, 'name': item.name, 'quantity': item.quantity,
            'notes': item.notes, 'who_needs_it': item.who_needs_it,
            'who_will_buy_it': item.who_will_buy_it, 'category_id': item.category_id,
            'is_completed': item.is_completed
        })
    return jsonify({'error': 'Item not found'}), 404

@app.route('/update_item/<int:item_id>', methods=['POST'])
def update_item(item_id):
    data = request.json
    Item.update(
        item_id, data.get('name'), data.get('quantity'), data.get('notes'),
        data.get('who_needs_it'), data.get('who_will_buy_it'), 
        data.get('category_id'), data.get('is_completed')
    )
    return jsonify(success=True)
    
@app.route('/update_item_name/<int:item_id>', methods=['POST'])
def update_item_name(item_id):
    data = request.json
    Item.update_name(item_id, data.get('name'))
    return jsonify(success=True)

@app.route('/delete_item/<int:item_id>', methods=['POST'])
def delete_item(item_id):
    Item.delete(item_id)
    return jsonify(success=True)

@app.route('/toggle_completed/<int:item_id>', methods=['POST'])
def toggle_completed(item_id):
    is_completed = request.json.get('is_completed', False)
    Item.toggle_completed(item_id, is_completed)
    return jsonify(success=True)

@app.route('/clear_completed', methods=['POST'])
def clear_completed():
    list_id = request.json.get('list_id', 1)
    Item.clear_completed(list_id)
    return jsonify(success=True)

@app.route('/update_item_order', methods=['POST'])
def update_item_order():
    data = request.json
    Item.update_order_and_category(
        data.get('item_id'),
        data.get('new_category_id'),
        data.get('sibling_ids', [])
    )
    return jsonify(success=True)

if __name__ == '__main__':
    # This block is for local development testing of the production setup.
    # It should not be used to run the app in production.
    # For production, a WSGI server like Gunicorn is used.
    print("This script is intended for deployment and is not meant to be run directly for local development.")
    print("Use 'gunicorn app_pg:app' to run, after setting DATABASE_URL.")
    # The following line is for convenience to create tables during development.
    # On Render, you can run this command from the shell to set up the DB.
    # create_tables()
