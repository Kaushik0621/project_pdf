from flask import Blueprint, render_template, request, jsonify, redirect, url_for
import sqlite3  # Import sqlite3 here
import os
from .vendors_db import get_vendors, add_vendor, get_materials, add_material, get_coatings, add_coating, get_products, add_product, get_coating_for_material, get_materials_for_coating
import py_files.config as cf
admin_db_path = os.path.join(cf.USER_DATA_PATH, 'admin.db')
vendors_bp = Blueprint('vendors_bp', __name__)

@vendors_bp.route('/vendors', methods=['GET', 'POST'])
def vendors():
    if request.method == 'POST':
        vendor_name = request.form['vendor_name']
        add_vendor(vendor_name)
    vendors = get_vendors()
    return render_template('vendors.html', vendors=vendors)

@vendors_bp.route('/materials', methods=['GET', 'POST'])
def materials():
    if request.method == 'POST':
        material_name = request.form['material_name']
        coating_name = request.form['coating_name']
        add_material(material_name, coating_name)
    materials = get_materials()
    coatings = get_coatings()
    return render_template('materials.html', materials=materials, coatings=coatings)
@vendors_bp.route('/get_products_for_company')
def get_products_for_company():
    company_name = request.args.get('company_name')
    
    # Fetch products related to the company
    conn = sqlite3.connect(admin_db_path)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT material_name, coating_name, price 
        FROM products 
        WHERE vendor_name = ?
    ''', (company_name,))
    
    products = cursor.fetchall()
    conn.close()

    if products:
        return jsonify({'success': True, 'products': [{'material_name': p[0], 'coating_name': p[1], 'price': p[2]} for p in products]})
    else:
        return jsonify({'success': False, 'error': 'No products found for this company.'})

@vendors_bp.route('/coatings', methods=['GET', 'POST'])
def coatings():
    if request.method == 'POST':
        coating_name = request.form['coating_name']
        add_coating(coating_name)
    coatings = get_coatings()
    return render_template('coatings.html', coatings=coatings)

@vendors_bp.route('/products', methods=['GET', 'POST'])
def products():
    if request.method == 'POST':
        material_name = request.form['material_name']
        coating_name = request.form['coating_name']
        vendor_name = request.form['vendor_name']
        price = request.form['price']
        add_product(material_name, coating_name, vendor_name, price)
    products = get_products()
    materials = get_materials()
    coatings = get_coatings()
    vendors = get_vendors()
    return render_template('products.html', products=products, materials=materials, coatings=coatings, vendors=vendors)

@vendors_bp.route('/systems', methods=['GET', 'POST'])
def systems():
    return render_template('systems.html')

@vendors_bp.route('/get_coating_for_material')
def get_coating_for_material_route():
    material_name = request.args.get('material_name')
    coating_name = get_coating_for_material(material_name)
    if coating_name:
        return jsonify({'success': True, 'coating_name': coating_name})
    return jsonify({'success': False})

# @vendors_bp.route('/get_materials_for_coating')
# def get_materials_for_coating():
#     coating_name = request.args.get('coating_name')
    
#     # Connect to the database and fetch materials for the given coating
#     conn = sqlite3.connect(admin_db_path)
#     cursor = conn.cursor()
#     cursor.execute('SELECT material_name FROM materials WHERE coating_name = ?', (coating_name,))
#     materials = cursor.fetchall()
#     conn.close()
    
#     return jsonify({'materials': [material[0] for material in materials]})
@vendors_bp.route('/get_materials_for_coating')
def get_materials_for_coating():
    coating_name = request.args.get('coating_name')
    
    # Connect to the database and fetch materials for the given coating
    conn = sqlite3.connect(admin_db_path)
    cursor = conn.cursor()
    cursor.execute('SELECT material_name FROM materials WHERE coating_name = ?', (coating_name,))
    materials = cursor.fetchall()
    conn.close()
    
    return jsonify({'materials': [material[0] for material in materials]})

@vendors_bp.route('/edit_product', methods=['POST'])
def edit_product():
    data = request.get_json()
    product_id = data['id']
    new_price = data['price']
    
    conn = sqlite3.connect(admin_db_path)
    cursor = conn.cursor()
    cursor.execute('UPDATE products SET price = ? WHERE id = ?', (new_price, product_id))
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})


@vendors_bp.route('/delete_product', methods=['POST'])
def delete_product():
    data = request.get_json()
    product_id = data['id']
    
    conn = sqlite3.connect(admin_db_path)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM products WHERE id = ?', (product_id,))
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})
