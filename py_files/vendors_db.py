import sqlite3

def init_db():
    conn = sqlite3.connect('your_database.db')
    cursor = conn.cursor()

    cursor.execute('''CREATE TABLE IF NOT EXISTS vendors (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL)''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS materials (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        material_name TEXT NOT NULL,
        coating_name TEXT NOT NULL)''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS coatings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        coating_name TEXT NOT NULL)''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        material_name TEXT NOT NULL,
        coating_name TEXT NOT NULL,
        vendor_name TEXT NOT NULL,
        price REAL NOT NULL)''')

    conn.commit()
    conn.close()

def add_vendor(vendor_name):
    conn = sqlite3.connect('your_database.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO vendors (name) VALUES (?)', (vendor_name,))
    conn.commit()
    conn.close()

def get_vendors():
    conn = sqlite3.connect('your_database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM vendors')
    vendors = cursor.fetchall()
    conn.close()
    return vendors

def add_material(material_name, coating_name):
    conn = sqlite3.connect('your_database.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO materials (material_name, coating_name) VALUES (?, ?)', (material_name, coating_name))
    conn.commit()
    conn.close()

def get_materials():
    conn = sqlite3.connect('your_database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM materials')
    materials = cursor.fetchall()
    conn.close()
    return materials

def add_coating(coating_name):
    conn = sqlite3.connect('your_database.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO coatings (coating_name) VALUES (?)', (coating_name,))
    conn.commit()
    conn.close()

def get_coatings():
    conn = sqlite3.connect('your_database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM coatings')
    coatings = cursor.fetchall()
    conn.close()
    return coatings

def add_product(material_name, coating_name, vendor_name, price):
    conn = sqlite3.connect('your_database.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO products (material_name, coating_name, vendor_name, price) VALUES (?, ?, ?, ?)', (material_name, coating_name, vendor_name, price))
    conn.commit()
    conn.close()

def get_products():
    conn = sqlite3.connect('your_database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM products')
    products = cursor.fetchall()
    conn.close()
    return products

def get_coating_for_material(material_name):
    conn = sqlite3.connect('your_database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT coating_name FROM materials WHERE material_name = ?', (material_name,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None

def get_materials_for_coating(coating_name):
    conn = sqlite3.connect('your_database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT material_name FROM materials WHERE coating_name = ?', (coating_name,))
    materials = cursor.fetchall()
    conn.close()
    return materials
