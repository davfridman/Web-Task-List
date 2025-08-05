from flask import Flask, render_template, request, redirect, url_for, jsonify, make_response
from database import create_tables
from models.item import Item
from models.category import Category
from models.shopping_list import ShoppingList

app = Flask(__name__)

# --- Helper ---
def get_active_list_id():
    return request.cookies.get('active_list_id', '1') # Default to list 1

# --- Main Routes ---
@app.route('/')
def index():
    active_list_id = get_active_list_id()
    all_lists = ShoppingList.get_all()
    
    if not all_lists:
        # Create a default list if the database is completely empty
        default_list = ShoppingList("Main List")
        default_list.save()
        all_lists = [default_list]

    active_list_id = request.cookies.get('active_list_id')
    if not active_list_id or not any(l.id == int(active_list_id) for l in all_lists):
        active_list_id = all_lists[0].id

    categories = Category.get_all_for_list(active_list_id)
    items = Item.get_all_for_list(active_list_id)
    
    grouped_items = {cat.id: {'id': cat.id, 'name': cat.name, 'items': []} for cat in categories}

    for item in items:
        category_id = item['category_id']
        if category_id in grouped_items:
            grouped_items[category_id]['items'].append(item)

    response = make_response(render_template(
        'index.html', 
        grouped_items=list(grouped_items.values()), 
        categories=categories,
        all_lists=all_lists,
        active_list_id=int(active_list_id)
    ))
    response.set_cookie('active_list_id', str(active_list_id))
    return response

@app.route('/set_active_list/<int:list_id>')
def set_active_list(list_id):
    response = make_response(redirect(url_for('index')))
    response.set_cookie('active_list_id', str(list_id))
    return response

# --- Shopping List Endpoints ---
@app.route('/list/<int:list_id>')
def get_list(list_id):
    shopping_list = ShoppingList.get_by_id(list_id)
    if shopping_list:
        return jsonify({'id': shopping_list.id, 'name': shopping_list.name})
    return jsonify({'error': 'List not found'}), 404

@app.route('/update_list/<int:list_id>', methods=['POST'])
def update_list(list_id):
    new_name = request.json.get('name')
    if new_name:
        ShoppingList.update_name(list_id, new_name)
        return jsonify(success=True)
    return jsonify(success=False, error="New name is required"), 400

@app.route('/add_list', methods=['POST'])
def add_list():
    list_name = request.form.get('list_name')
    if list_name:
        new_list = ShoppingList(name=list_name)
        new_list.save()
        # Create a default "Other" category for the new list
        other = Category(name="Other", list_id=new_list.id)
        other.save()
    return redirect(url_for('index'))

@app.route('/delete_list/<int:list_id>', methods=['POST'])
def delete_list(list_id):
    ShoppingList.delete(list_id)
    return redirect(url_for('index'))

# --- Category Endpoints ---
@app.route('/add_category', methods=['POST'])
def add_category():
    name = request.form.get('category_name')
    active_list_id = get_active_list_id()
    if name and active_list_id:
        Category(name=name, list_id=active_list_id).save()
    return redirect(url_for('index'))

@app.route('/update_category_order', methods=['POST'])
def update_category_order():
    category_ids = request.json.get('category_ids', [])
    if category_ids:
        Category.update_order(category_ids)
    return jsonify(success=True)

@app.route('/category/<int:category_id>')
def get_category(category_id):
    category = Category.get_by_id(category_id)
    if category:
        return jsonify({'id': category.id, 'name': category.name})
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

# --- Item Endpoints ---
@app.route('/add', methods=['POST'])
def add_item():
    active_list_id = get_active_list_id()
    category_id = request.form.get('category_id')
    if not category_id:
        # Find the Other category for the active list
        conn = get_db_connection()
        other = conn.execute('SELECT id FROM categories WHERE name = "Other" AND list_id = ?', (active_list_id,)).fetchone()
        conn.close()
        category_id = other['id'] if other else None

    item = Item(
        name=request.form.get('name'),
        quantity=int(request.form.get('quantity', 1)),
        notes=request.form.get('notes'),
        who_needs_it=request.form.get('who_needs_it'),
        who_will_buy_it=request.form.get('who_will_buy_it'),
        category_id=category_id
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
        data.get('who_needs_it'), data.get('who_will_buy_it'), data.get('category_id'),
        data.get('is_completed')
    )
    return jsonify(success=True)
    
@app.route('/delete/<int:item_id>')
def delete_item(item_id):
    Item.delete(item_id)
    return redirect(url_for('index'))

@app.route('/update_item_name/<int:item_id>', methods=['POST'])
def update_item_name(item_id):
    data = request.json
    Item.update_name(item_id, data.get('name'))
    return jsonify(success=True)

@app.route('/toggle_completed/<int:item_id>', methods=['POST'])
def toggle_completed(item_id):
    is_completed = request.json.get('is_completed', 0)
    Item.toggle_completed(item_id, is_completed)
    return jsonify(success=True)

@app.route('/clear_completed', methods=['POST'])
def clear_completed():
    active_list_id = get_active_list_id()
    Item.clear_completed(active_list_id)
    return redirect(url_for('index'))

@app.route('/update_item_and_order', methods=['POST'])
def update_item_and_order():
    data = request.json
    Item.update_order_and_category(
        data.get('item_id'),
        data.get('new_category_id'),
        data.get('sibling_ids', [])
    )
    return jsonify(success=True)

if __name__ == '__main__':
    create_tables()
    app.run(debug=True)
