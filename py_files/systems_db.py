import sqlite3
import os
import py_files.config as cf

# Paths for systems.db and admin.db
systems_db_path = os.path.join(cf.USER_DATA_PATH, 'systems.db')
admin_db_path = os.path.join(cf.USER_DATA_PATH, 'admin.db')

def init_systems_db():
    conn = sqlite3.connect(systems_db_path)
    cursor = conn.cursor()

    # Create systems table with total_price column
    cursor.execute('''CREATE TABLE IF NOT EXISTS systems (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        company_name TEXT NOT NULL,
        system_name TEXT NOT NULL,
        total_price REAL DEFAULT 0
    )''')

    # Create layers table linked to systems
    cursor.execute('''CREATE TABLE IF NOT EXISTS layers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        system_id INTEGER NOT NULL,
        coating_name TEXT NOT NULL,
        material_name TEXT NOT NULL,
        vendor_name TEXT NOT NULL,
        price REAL NOT NULL,
        FOREIGN KEY (system_id) REFERENCES systems(id) ON DELETE CASCADE
    )''')

    conn.commit()
    conn.close()

def add_system(company_name, system_name, layers):
    conn = sqlite3.connect(systems_db_path)
    cursor = conn.cursor()

    # Calculate total price from layers
    total_price = sum(float(layer['price']) for layer in layers)

    # Insert system with the company name, system name, and total price
    cursor.execute('INSERT INTO systems (company_name, system_name, total_price) VALUES (?, ?, ?)', 
                   (company_name, system_name, total_price))
    conn.commit()
    system_id = cursor.lastrowid

    # Insert each layer for the system
    for layer in layers:
        add_layer(system_id, layer['coating_name'], layer['material_name'], layer['vendor_name'], layer['price'])

    conn.close()
    return system_id

def add_layer(system_id, coating_name, material_name, vendor_name, price):
    conn = sqlite3.connect(systems_db_path)
    cursor = conn.cursor()
    cursor.execute('''INSERT INTO layers (system_id, coating_name, material_name, vendor_name, price) 
                      VALUES (?, ?, ?, ?, ?)''', 
                   (system_id, coating_name, material_name, vendor_name, price))
    conn.commit()
    conn.close()

def get_systems():
    conn = sqlite3.connect(systems_db_path)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM systems')
    systems = cursor.fetchall()
    conn.close()
    return systems

def get_systems_by_company_name(company_name):
    conn = sqlite3.connect(systems_db_path)
    cursor = conn.cursor()
    cursor.execute('SELECT id, system_name, total_price FROM systems WHERE company_name = ?', (company_name,))
    systems = cursor.fetchall()
    conn.close()
    
    # Fetch layers for each system and return as a list of dictionaries
    systems_with_layers = []
    for system in systems:
        system_id = system[0]
        layers = get_layers_by_system_id(system_id)
        systems_with_layers.append({
            'id': system_id,
            'system_name': system[1],
            'total_price': system[2],
            'layers': layers
        })
    return systems_with_layers

def get_layers_by_system_id(system_id):
    conn = sqlite3.connect(systems_db_path)
    cursor = conn.cursor()
    cursor.execute('SELECT coating_name, material_name, vendor_name, price FROM layers WHERE system_id = ?', 
                   (system_id,))
    layers = cursor.fetchall()
    conn.close()
    return [{'coating_name': layer[0], 'material_name': layer[1], 'vendor_name': layer[2], 'price': layer[3]} 
            for layer in layers]

def get_coatings():
    conn = sqlite3.connect(admin_db_path)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM coatings')  # Assuming coatings table exists in admin.db
    coatings = cursor.fetchall()
    conn.close()
    return coatings

def get_materials_for_coating(coating_name):
    conn = sqlite3.connect(admin_db_path)
    cursor = conn.cursor()
    cursor.execute('SELECT material_name FROM materials WHERE coating_name = ?', (coating_name,))
    materials = cursor.fetchall()
    conn.close()
    return [material[0] for material in materials]

def get_vendors_for_material_and_coating(material_name, coating_name):
    conn = sqlite3.connect(admin_db_path)
    cursor = conn.cursor()
    cursor.execute('SELECT vendor_name, price FROM products WHERE material_name = ? AND coating_name = ?', 
                   (material_name, coating_name))
    vendors = cursor.fetchall()
    conn.close()
    return [{'vendor_name': vendor[0], 'price': vendor[1]} for vendor in vendors]

def delete_layer(layer_id):
    conn = sqlite3.connect(systems_db_path)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM layers WHERE id = ?', (layer_id,))
    conn.commit()
    conn.close()

def delete_system(system_id):
    conn = sqlite3.connect(systems_db_path)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM systems WHERE id = ?', (system_id,))
    cursor.execute('DELETE FROM layers WHERE system_id = ?', (system_id,))
    conn.commit()
    conn.close()
