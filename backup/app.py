from flask import Flask, render_template, redirect, url_for, request, session, jsonify

import os
from py_files.utils import create_user, validate_user, init_user_db


app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with a secure key

# Initialize the shared user database
init_user_db()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        error = create_user(username, password)
        if error:
            return render_template('signup.html', error=error)
        else:
            return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if validate_user(username, password):
            session['username'] = username
            return redirect(url_for('dashboard'))
        else:
            error = 'Invalid username or password.'
            return render_template('login.html', error=error)
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'username' in session:
        return render_template('dashboard.html')
    return redirect(url_for('login'))


@app.route('/get_company_data')
def get_company_data():
    if 'username' in session:
        company_name = request.args.get('company_name')
        username = session['username']
        company_path = os.path.join('users', username, 'customers', company_name)

        # Fetch the projects for the selected company
        if os.path.exists(company_path):
            projects = [p for p in os.listdir(company_path) if p != '.DS_Store' and os.path.isdir(os.path.join(company_path, p))]
        else:
            projects = []

        # Render the 'project.html' template and return it as HTML
        return render_template('projects.html', company_name=company_name, projects=projects)
    return ''


@app.route('/customers', methods=['GET', 'POST'])
def customers():
    if 'username' in session:
        username = session['username']
        customers_path = os.path.join('users', username, 'customers')
        company_images = {}
        projects = {}

        # Get the companies and their projects
        companies = [c for c in os.listdir(customers_path) if c != '.DS_Store']
        for company in companies:
            company_path = os.path.join(customers_path, company)
            projects[company] = [p for p in os.listdir(company_path) if p != '.DS_Store']
            
            # Check for an image in the company folder
            image_path = os.path.join(company_path, 'image.jpg')
            if os.path.exists(image_path):
                company_images[company] = 'image.jpg'
            else:
                company_images[company] = None

        if request.method == 'POST':
            company_name = request.form['company_name']
            company_path = os.path.join(customers_path, company_name)
            if not os.path.exists(company_path):
                os.makedirs(company_path)
            return redirect(url_for('customers'))

        return render_template('customers.html', companies=companies, projects=projects, company_images=company_images)
    return redirect(url_for('login'))



@app.route('/vendors')
def vendors():
    if 'username' in session:
        # Similar logic for vendors
        return render_template('vendors.html')
    return redirect(url_for('login'))


@app.route('/projects/<company_name>', methods=['GET', 'POST'])
def projects(company_name):
    if 'username' in session:
        username = session['username']
        company_path = os.path.join('users', username, 'customers', company_name)

        # Create project if the form is submitted
        if request.method == 'POST':
            project_name = request.form['project_name']
            project_path = os.path.join(company_path, project_name)
            if not os.path.exists(project_path):
                os.makedirs(project_path)
            return redirect(url_for('projects', company_name=company_name))

        # Get the list of projects (exclude system files like .DS_Store)
        projects = [p for p in os.listdir(company_path) if p != '.DS_Store' and os.path.isdir(os.path.join(company_path, p))]

        # Render the projects template with the correct data
        return render_template('projects.html', company_name=company_name, projects=projects)
    return redirect(url_for('login'))


@app.route('/delete_company', methods=['POST'])
def delete_company():
    if 'username' in session:
        data = request.get_json()
        company_name = data.get('company_name')
        username = session['username']
        company_path = os.path.join('users', username, 'customers', company_name)
        if os.path.exists(company_path):
            import shutil
            shutil.rmtree(company_path)
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'error': 'Company not found'})
    return jsonify({'success': False, 'error': 'Unauthorized'}), 401

@app.route('/delete_project', methods=['POST'])
def delete_project():
    if 'username' in session:
        data = request.get_json()
        company_name = data.get('company_name')
        project_name = data.get('project_name')
        username = session['username']
        project_path = os.path.join('users', username, 'customers', company_name, project_name)
        if os.path.exists(project_path):
            import shutil
            shutil.rmtree(project_path)
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'error': 'Project not found'})
    return jsonify({'success': False, 'error': 'Unauthorized'}), 401

@app.route('/create_project', methods=['POST'])
def create_project():
    if 'username' in session:
        data = request.get_json()
        company_name = data.get('company_name')
        project_name = data.get('project_name')
        username = session['username']
        project_path = os.path.join('users', username, 'customers', company_name, project_name)
        if not os.path.exists(project_path):
            os.makedirs(project_path)
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'error': 'Project already exists'})
    return jsonify({'success': False, 'error': 'Unauthorized'}), 401
@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
