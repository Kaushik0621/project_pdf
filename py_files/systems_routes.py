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

    # Fetch companies from the customer folder
    customers_path = os.path.join(cf.USER_PATH, username, 'customers')
    companies = [c for c in os.listdir(customers_path) if os.path.isdir(os.path.join(customers_path, c))]

    # Fetch all systems
    systems = get_systems()
    return render_template('systems.html', systems=systems, coatings=coatings, companies=companies)


# Route to add a new system with layers
@systems_bp.route('/add_system', methods=['POST'])
def add_system_route():
    data = request.get_json()
    company_name = data['company_name']
    system_name = data['system_name']
    layers = data['layers']

    # Add the system with company name, system name, and layers
    system_id = add_system(company_name, system_name, layers)
    
    return jsonify({'success': True, 'system_id': system_id})


# Route to calculate and return total cost based on provided layers
@systems_bp.route('/get_total_cost', methods=['POST'])
def get_total_cost():
    layers = request.json.get('layers', [])
    total_cost = sum(float(layer['price']) for layer in layers)
    return jsonify({'success': True, 'total_cost': total_cost})

# Route to edit an existing system by updating layers
@systems_bp.route('/edit_system', methods=['POST'])
def edit_system():
    data = request.get_json()
    system_id = data['system_id']
    
    # Remove existing layers and add new ones based on the updated data
    layers = data.get('layers', [])
    for layer in layers:
        add_layer(system_id, layer['coating_name'], layer['material_name'], layer['vendor_name'], layer['price'])
    
    return jsonify({'success': True})


# Route to delete a system and its associated layers
@systems_bp.route('/delete_system', methods=['POST'])
def delete_system_route():
    system_id = request.json['id']  # Using JSON for consistency
    delete_system(system_id)
    return jsonify({'success': True})


# Route to fetch vendors based on material and coating for selection
@systems_bp.route('/get_vendors_for_material_and_coating', methods=['GET'])
def get_vendors_for_material_and_coating_route():
    material_name = request.args.get('material_name')
    coating_name = request.args.get('coating_name')
    
    vendors = get_vendors_for_material_and_coating(material_name, coating_name)
    print(f"Vendors fetched: {vendors}")  # Debugging output to verify vendor data structure
    
    if vendors:
        # Expecting vendors to be a list of dictionaries, so access keys directly
        return jsonify({'success': True, 'vendors': [{'vendor_name': vendor['vendor_name'], 'price': vendor['price']} for vendor in vendors]})
    
    return jsonify({'success': False, 'error': 'No vendors found for this material and coating.'})



# Route to fetch systems by a specific company name
@systems_bp.route('/get_systems_for_company', methods=['GET'])
def get_systems_for_company():
    company_name = request.args.get('company_name')
    
    # Fetch systems for the given company name, including their layers and total price
    systems = get_systems_by_company_name(company_name)
    
    return jsonify({'systems': systems})
