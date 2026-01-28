import os
from flask import jsonify, request, render_template, url_for
from werkzeug.utils import secure_filename
from . import menu_bp

# Upload configuration
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# In-memory storage for dishes and categories
DISHES = {
    1: [
        {"id": 1, "name": "Caesar Salad", "price": 299.99, "quantity": "100ml", "description": "Fresh romaine lettuce with parmesan", "images": ["caesar_salad.jpg"], "image_urls": ["/static/uploads/caesar_salad.jpg"]},
        {"id": 2, "name": "Garlic Bread", "price": 199.99, "quantity": "2 pcs", "description": "Toasted bread with garlic butter", "images": ["garlic_bread.jpg"], "image_urls": ["/static/uploads/garlic_bread.jpg"]}
    ],
    2: [
        {"id": 3, "name": "Grilled Salmon", "price": 599.99, "quantity": "250gm", "description": "Fresh Atlantic salmon with herbs", "images": ["salmon.jpg", "salmon_side.jpg"], "image_urls": ["/static/uploads/salmon.jpg", "/static/uploads/salmon_side.jpg"]},
        {"id": 4, "name": "Beef Steak", "price": 699.99, "quantity": "1 plate", "description": "Premium ribeye steak", "images": ["steak.jpg"], "image_urls": ["/static/uploads/steak.jpg"]}
    ],
    3: [
        {"id": 5, "name": "Chocolate Cake", "price": 249.99, "quantity": "1 slice", "description": "Rich chocolate layer cake", "images": ["chocolate_cake.jpg"], "image_urls": ["/static/uploads/chocolate_cake.jpg"]},
        {"id": 6, "name": "Ice Cream", "price": 149.99, "quantity": "2 scoops", "description": "Vanilla ice cream with toppings", "images": [], "image_urls": []}
    ],
    4: [
        {"id": 7, "name": "Ginger Tea", "price": 99.99, "quantity": "1 cup", "description": "Hot ginger tea with spices", "images": ["dish_5_ginger-tea-recipe-3.jpg"], "image_urls": ["/static/uploads/dish_5_ginger-tea-recipe-3.jpg"]},
        {"id": 8, "name": "Cardamom Tea", "price": 89.99, "quantity": "1 cup", "description": "Aromatic cardamom tea", "images": ["dish_6_cardamom-tea3.jpg"], "image_urls": ["/static/uploads/dish_6_cardamom-tea3.jpg"]}
    ]
}

CATEGORIES = {
    1: "Starters",
    2: "Main Course", 
    3: "Desserts",
    4: "aa bereges"
}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_uploaded_file(file, dish_id):
    """Save uploaded file and return filename"""
    if file and allowed_file(file.filename):
        filename = secure_filename(f"dish_{dish_id}_{file.filename}")
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        
        # Create upload directory if it doesn't exist
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        
        try:
            file.save(filepath)
            return filename
        except Exception as e:
            print(f"Error saving file: {e}")
            return None
    return None

@menu_bp.route("/menu")
def menu_page():
    return render_template('menu/menu_page.html')

@menu_bp.route("/menu-dashboard")
def menu_dashboard():
    return render_template('menu/menu_dashboard.html')

@menu_bp.route("/api/categories")
def get_categories():
    return jsonify({"success": True, "categories": CATEGORIES})

@menu_bp.route("/api/dishes/<int:category_id>")
def get_dishes(category_id):
    dishes = DISHES.get(category_id, [])
    return jsonify({"success": True, "dishes": dishes})

@menu_bp.route("/api/add-dish", methods=["POST"])
def add_dish():
    try:
        category_id = int(request.form.get("category_id", 0))
        name = request.form.get("name", "").strip()
        price_str = request.form.get("price", "0").strip()
        quantity_str = request.form.get("quantity", "0").strip()
        description = request.form.get("description", "").strip()
        
        # Validation
        if not name:
            return jsonify({"success": False, "message": "Dish name is required"})
        
        try:
            price = float(price_str) if price_str else 0
        except ValueError:
            return jsonify({"success": False, "message": "Invalid price format"})
            
        quantity = quantity_str.strip() if quantity_str else "0"
        
        if price <= 0:
            return jsonify({"success": False, "message": "Price must be greater than 0"})
        if not quantity:
            return jsonify({"success": False, "message": "Quantity is required"})
        if category_id not in DISHES:
            return jsonify({"success": False, "message": "Category not found"})
        
        # Generate new ID
        all_ids = [dish["id"] for dishes in DISHES.values() for dish in dishes]
        new_id = max(all_ids, default=0) + 1
        
        # Handle image uploads
        images = []
        uploaded_files = request.files.getlist('images')
        valid_files = [f for f in uploaded_files if f and f.filename and f.filename.strip()]
        
        if len(valid_files) > 3:
            return jsonify({"success": False, "message": "Maximum 3 images allowed"})
        
        for file in valid_files:
            saved_filename = save_uploaded_file(file, new_id)
            if saved_filename:
                images.append(saved_filename)
        
        # Create new dish with proper image URLs
        image_urls = []
        for img in images:
            image_urls.append(url_for('static', filename=f'uploads/{img}'))
        
        new_dish = {
            "id": new_id,
            "name": name,
            "price": price,
            "quantity": quantity,
            "description": description,
            "images": images,
            "image_urls": image_urls
        }
        
        DISHES[category_id].append(new_dish)
        return jsonify({"success": True, "message": "Dish added successfully", "dish": new_dish})
        
    except Exception as e:
        return jsonify({"success": False, "message": f"Server error: {str(e)}"})

@menu_bp.route("/api/edit-dish", methods=["POST"])
def edit_dish():
    try:
        dish_id = int(request.form.get("dish_id", 0))
        name = request.form.get("name", "").strip()
        price_str = request.form.get("price", "0").strip()
        quantity_str = request.form.get("quantity", "0").strip()
        description = request.form.get("description", "").strip()
        
        # Validation
        if not name:
            return jsonify({"success": False, "message": "Dish name is required"})
            
        try:
            price = float(price_str) if price_str else 0
        except ValueError:
            return jsonify({"success": False, "message": "Invalid price format"})
            
        quantity = quantity_str.strip() if quantity_str else "0"
        
        if price <= 0:
            return jsonify({"success": False, "message": "Price must be greater than 0"})
        if not quantity:
            return jsonify({"success": False, "message": "Quantity is required"})
        
        # Find and update dish
        for category_dishes in DISHES.values():
            for dish in category_dishes:
                if dish["id"] == dish_id:
                    dish["name"] = name
                    dish["price"] = price
                    dish["quantity"] = quantity
                    dish["description"] = description
                    
                    # Handle new image uploads
                    uploaded_files = request.files.getlist('images')
                    valid_files = [f for f in uploaded_files if f and f.filename and f.filename.strip()]
                    
                    if valid_files:
                        if len(valid_files) > 3:
                            return jsonify({"success": False, "message": "Maximum 3 images allowed"})
                        
                        new_images = []
                        image_urls = []
                        for file in valid_files:
                            saved_filename = save_uploaded_file(file, dish_id)
                            if saved_filename:
                                new_images.append(saved_filename)
                                image_urls.append(url_for('static', filename=f'uploads/{saved_filename}'))
                        dish["images"] = new_images
                        dish["image_urls"] = image_urls
                    
                    return jsonify({"success": True, "message": "Dish updated successfully", "dish": dish})
        
        return jsonify({"success": False, "message": "Dish not found"})
        
    except Exception as e:
        return jsonify({"success": False, "message": f"Server error: {str(e)}"})

@menu_bp.route("/api/delete-dish", methods=["POST"])
def delete_dish():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "message": "No data provided"})
        
        dish_id = int(data.get("dish_id", 0))
        
        for category_dishes in DISHES.values():
            for i, dish in enumerate(category_dishes):
                if dish["id"] == dish_id:
                    category_dishes.pop(i)
                    return jsonify({"success": True, "message": "Dish deleted successfully"})
        
        return jsonify({"success": False, "message": "Dish not found"})
        
    except Exception as e:
        return jsonify({"success": False, "message": f"Server error: {str(e)}"})

@menu_bp.route("/api/add-category", methods=["POST"])
def add_category():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "message": "No data provided"})
        
        name = data.get("name", "").strip()
        
        if not name:
            return jsonify({"success": False, "message": "Category name is required"})
        
        for existing_name in CATEGORIES.values():
            if existing_name.lower() == name.lower():
                return jsonify({"success": False, "message": "Category already exists"})
        
        new_id = max(list(CATEGORIES.keys()) + list(DISHES.keys()), default=0) + 1
        
        CATEGORIES[new_id] = name
        DISHES[new_id] = []
        
        return jsonify({
            "success": True, 
            "message": f"Category '{name}' added successfully", 
            "category": {"id": new_id, "name": name}
        })
        
    except Exception as e:
        return jsonify({"success": False, "message": f"Server error: {str(e)}"})

@menu_bp.route("/api/edit-category", methods=["POST"])
def edit_category():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "message": "No data provided"})
        
        category_id = int(data.get("category_id", 0))
        name = data.get("name", "").strip()
        
        if not name:
            return jsonify({"success": False, "message": "Category name is required"})
        
        if category_id not in CATEGORIES:
            return jsonify({"success": False, "message": "Category not found"})
        
        # Check if name already exists (excluding current category)
        for existing_id, existing_name in CATEGORIES.items():
            if existing_id != category_id and existing_name.lower() == name.lower():
                return jsonify({"success": False, "message": "Category name already exists"})
        
        CATEGORIES[category_id] = name
        
        return jsonify({
            "success": True, 
            "message": f"Category updated to '{name}' successfully", 
            "category": {"id": category_id, "name": name}
        })
        
    except Exception as e:
        return jsonify({"success": False, "message": f"Server error: {str(e)}"})

@menu_bp.route("/api/delete-category", methods=["POST"])
def delete_category():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "message": "No data provided"})
        
        category_id = int(data.get("category_id", 0))
        
        if category_id not in CATEGORIES:
            return jsonify({"success": False, "message": "Category not found"})
        
        category_name = CATEGORIES[category_id]
        dishes_count = len(DISHES.get(category_id, []))
        
        # Remove category and its dishes
        del CATEGORIES[category_id]
        if category_id in DISHES:
            del DISHES[category_id]
        
        return jsonify({
            "success": True, 
            "message": f"Category '{category_name}' and {dishes_count} dish(es) deleted successfully"
        })
        
    except Exception as e:
        return jsonify({"success": False, "message": f"Server error: {str(e)}"})

@menu_bp.route("/api/full-menu")
def get_full_menu():
    full_menu = []
    for category_id, category_name in CATEGORIES.items():
        dishes = DISHES.get(category_id, [])
        full_menu.append({
            "category_id": category_id,
            "category_name": category_name,
            "dishes": dishes
        })
    return jsonify({"success": True, "menu": full_menu})

@menu_bp.route("/api/dish/<int:dish_id>")
def get_dish(dish_id):
    try:
        for category_dishes in DISHES.values():
            for dish in category_dishes:
                if dish["id"] == dish_id:
                    return jsonify({"success": True, "dish": dish})
        return jsonify({"success": False, "message": "Dish not found"})
    except Exception as e:
        return jsonify({"success": False, "message": f"Server error: {str(e)}"})

# Initialize database tables for menu if using database
def init_menu_db():
    """Initialize menu database tables if needed"""
    pass