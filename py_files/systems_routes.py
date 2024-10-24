from flask import Blueprint, request, jsonify, render_template, session, redirect, url_for
from .systems_db import init_systems_db, add_system, add_layer, get_coatings, get_materials_for_coating, get_vendors_for_material_and_coating, delete_layer, get_systems, get_systems_by_company_name, delete_system
import os
import py_files.config as cf

systems_bp = Blueprint('systems_bp', __name__)

# Initialize systems.db when the app starts
init_systems_db()

# Route to load systems page with companies from customer folder
@systems_bp.route('/systems', methods=['GET', 'POST'])
def systems():
    username = session.get('username')
    if not username:
        return redirect(url_for('login'))  # Redirect to login if the session does not have a username

    # Fetch coatings from admin.db and pass them to the template
    coatings = get_coatings()

    # Fetch companies from customer folder
    customers_path = os.path.join(cf.USER_PATH, username, 'customers')
    companies = [c for c in os.listdir(customers_path) if os.path.isdir(os.path.join(customers_path, c))]

    systems = get_systems()
    return render_template('systems.html', systems=systems, coatings=coatings, companies=companies)


# Add a new system
@systems_bp.route('/add_system', methods=['POST'])
def add_system_route():
    data = request.get_json()
    company_name = data['company_name']
    system_name = data['system_name']
    layers = data['layers']

    # Pass company_name, system_name, and layers to add_system function
    system_id = add_system(company_name, system_name, layers)
    
    return jsonify({'success': True, 'system_id': system_id})


# Get total cost of the system based on added layers
@systems_bp.route('/get_total_cost', methods=['POST'])
def get_total_cost():
    layers = request.json.get('layers', [])
    total_cost = sum(float(layer['price']) for layer in layers)
    return jsonify({'success': True, 'total_cost': total_cost})

# Route to edit a system (adding/removing layers)
@systems_bp.route('/edit_system', methods=['POST'])
def edit_system():
    data = request.get_json()
    system_id = data['system_id']
    
    # Handle adding/removing layers
    layers = data.get('layers', [])
    # Delete existing layers and add new ones
    for layer in layers:
        add_layer(system_id, layer['coating_name'], layer['material_name'], layer['vendor_name'], layer['price'])
    
    return jsonify({'success': True})

# Route to delete a system
@systems_bp.route('/delete_system', methods=['POST'])
def delete_system_route():
    system_id = request.json['id']  # Using JSON for consistency
    delete_system(system_id)
    return jsonify({'success': True})

@systems_bp.route('/get_vendors_for_material_and_coating', methods=['GET'])
def get_vendors_for_material_and_coating_route():
    material_name = request.args.get('material_name')
    coating_name = request.args.get('coating_name')
    
    vendors = get_vendors_for_material_and_coating(material_name, coating_name)
    print(f"Vendors fetched: {vendors}")  # Add this line for debugging
    
    if vendors:
        return jsonify({'success': True, 'vendors': [{'vendor_name': v[0], 'price': v[1]} for v in vendors]})
    return jsonify({'success': False, 'error': 'No vendors found for this material and coating.'})


@systems_bp.route('/get_systems_for_company', methods=['GET'])
def get_systems_for_company():
    company_name = request.args.get('company_name')
    
    # Fetch systems for the given company name
    systems = get_systems_by_company_name(company_name)
    
    return jsonify({'systems': systems})
