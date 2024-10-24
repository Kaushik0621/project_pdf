from flask import Flask, render_template, redirect, url_for, request, session, jsonify
import os
import json
from py_files.utils import create_user, validate_user, init_user_db
from py_files.systems_db import init_systems_db
from py_files.area_utils import calculate_area
from py_files.vendors_routes import vendors_bp
from py_files.vendors_db import init_db 
import json
import uuid
import shutil
import os
import py_files.config as cf
from flask import send_from_directory, abort
import requests
from py_files.systems_routes import systems_bp

PROJECTS_JSON = os.path.join('projects.json')

def load_projects():
    if not os.path.exists(PROJECTS_JSON):
        with open(PROJECTS_JSON, 'w') as f:
            json.dump({}, f, indent=4)
        return {}

    with open(PROJECTS_JSON, 'r') as f:
        return json.load(f)


def save_projects(projects):
    with open(PROJECTS_JSON, 'w') as f:
        json.dump(projects, f, indent=4)

    response = {
        'backup_save': False,
        'error': None
    }

    try:
        parent_dir = os.path.abspath(os.path.join(os.getcwd(), '..'))
        backup_dir = os.path.join(parent_dir, 'cad_pdf_extractror')

        if not os.path.exists(backup_dir):
            response['error'] = "Backup directory does not exist"
            return jsonify(response)

        backup_json_path = os.path.join(backup_dir, 'projects.json')
        with open(backup_json_path, 'w') as f:
            json.dump(projects, f, indent=4)
        response['backup_save'] = True

    except Exception as e:
        response['error'] = f"Backup save failed: {str(e)}"

    return jsonify(response)



def add_project_to_json(project_name, project_id, project_path):
    projects = load_projects()
    projects[project_name] = {
        "project_id": project_id,
        "project_path": project_path
    }
    save_projects(projects)



def remove_project_from_json(project_name):
    projects = load_projects()
    
    if project_name in projects:
        del projects[project_name]
        save_projects(projects)
        return True
    return False


app = Flask(__name__)
app.secret_key = 'your_secret_key'

init_user_db()
init_systems_db()
init_db()

project_data = load_projects()

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
        company_path = os.path.join(cf.USER_PATH, username, 'customers', company_name)

        if os.path.exists(company_path):
            projects = [p for p in os.listdir(company_path) if p != '.DS_Store' and os.path.isdir(os.path.join(company_path, p))]
        else:
            projects = []

        return render_template('projects_list.html', company_name=company_name, projects=projects)
    return ''

@app.route('/project_details')
def project_details():
    if 'username' in session:
        company_name = request.args.get('company_name')
        project_name = request.args.get('project_name')
        username = session['username']
        project_path = os.path.join(cf.USER_PATH, username, 'customers', company_name, project_name)

        # Load the JSON file (update the filename if necessary)
        json_file_path = os.path.join(project_path, 'extracted_data.json')  # Update to the correct filename
        project_json = {}
        if os.path.exists(json_file_path):
            with open(json_file_path, 'r') as json_file:
                project_json = json.load(json_file)

        # Get the PDF file
        pdf_name = None
        for file_name in os.listdir(project_path):
            if file_name.endswith('.pdf'):
                pdf_name = file_name
                break

        # Set the current page (default to page 1)
        current_page = int(request.args.get('page', 1))

        # Print JSON to debug
        print(f"Loaded JSON: {project_json}")

        return render_template('project_details.html', company_name=company_name, 
                               project_name=project_name, project_json=project_json, 
                               pdf_name=pdf_name, current_page=current_page)
    return redirect(url_for('login'))





@app.route('/static/uploads/<path:filename>')
def serve_pdf(filename):
    company_name = request.args.get('company_name')
    project_name = request.args.get('project_name')
    username = session.get('username')  # Get username from session

    if not company_name or not project_name or not username:
        abort(400, description="Missing company name, project name, or username")

    project_path = os.path.join(cf.USER_PATH, username, 'customers', company_name, project_name)

    if not os.path.exists(project_path):
        abort(404, description="Project path not found")

    return send_from_directory(project_path, filename)





@app.route('/edit_company', methods=['POST'])
def edit_company():
    if 'username' in session:
        data = request.get_json()
        old_company_name = data.get('company_name')
        new_company_name = data.get('new_company_name')
        username = session['username']
        customers_path = os.path.join(cf.USER_PATH, username, 'customers')

        old_company_path = os.path.join(customers_path, old_company_name)
        new_company_path = os.path.join(customers_path, new_company_name)

        if os.path.exists(old_company_path):
            os.rename(old_company_path, new_company_path)
            return jsonify({'success': True})
        return jsonify({'success': False, 'error': 'Company not found'})
    return jsonify({'success': False, 'error': 'Unauthorized'}), 401

@app.route('/customers', methods=['GET', 'POST'])
def customers():
    if 'username' in session:
        username = session['username']
        customers_path = os.path.join(cf.USER_PATH, username, 'customers')

        companies = [c for c in os.listdir(customers_path) if c != '.DS_Store']
        if request.method == 'POST':
            company_name = request.form['company_name']
            company_path = os.path.join(customers_path, company_name)
            if not os.path.exists(company_path):
                os.makedirs(company_path)
            return redirect(url_for('customers'))

        return render_template('customers.html', companies=companies)
    return redirect(url_for('login'))

@app.route('/create_project', methods=['POST'])
def create_project():
    if 'username' in session:
        data = request.get_json()
        company_name = data.get('company_name')
        project_name = data.get('project_name')
        username = session['username']
        
        load_projects()
        
        if not company_name or not project_name:
            return jsonify({'success': False, 'error': 'Missing company or project name'}), 400

        company_path = os.path.join(cf.USER_PATH, username, 'customers', company_name)
        project_path = os.path.join(company_path, project_name)

        if not os.path.exists(company_path):
            return jsonify({'success': False, 'error': 'Company does not exist'}), 400

        if not os.path.exists(project_path):
            try:
                os.makedirs(project_path)
                project_id = str(uuid.uuid4())
                add_project_to_json(project_name, project_id, project_path)
                return jsonify({'success': True, 'project_id': project_id})
            except Exception as e:
                return jsonify({'success': False, 'error': str(e)}), 500
        else:
            return jsonify({'success': False, 'error': 'Project already exists'}), 400
    return jsonify({'success': False, 'error': 'Unauthorized'}), 401

@app.route('/edit_project', methods=['POST'])
def edit_project():
    if 'username' in session:
        data = request.get_json()
        company_name = data.get('company_name')
        project_name = data.get('project_name')
        new_project_name = data.get('new_project_name')
        username = session['username']
        project_path = os.path.join(cf.USER_PATH, username, 'customers', company_name, project_name)
        new_project_path = os.path.join(cf.USER_PATH, username, 'customers', company_name, new_project_name)
        if os.path.exists(project_path):
            os.rename(project_path, new_project_path)
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'error': 'Project not found'}), 400
    return jsonify({'success': False, 'error': 'Unauthorized'}), 401

@app.route('/cad_pdf_editor', methods=['POST'])
def cad_pdf_editor():
    if 'username' in session:
        data = request.get_json()
        company_name = data.get('company_name')
        project_name = data.get('project_name')
        username = session['username']
        project_path = os.path.join(cf.USER_PATH, username, 'customers', company_name, project_name)
        
        print(f"Current project path: {project_path}")
        
        # Send project_path to FastAPI
        fastapi_url = 'http://localhost:8888/set_project_path'
        try:
            response = requests.post(fastapi_url, json={'project_path': project_path})
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"Error connecting to FastAPI: {e}")
            return jsonify({'success': False, 'message': 'Unable to connect to the PDF editor service.'}), 503
        
        if response.status_code == 200:
            # Get the UUID (pdf_id) from FastAPI's response
            project_id = response.json().get('pdf_id')
            if project_id:
                fastapi_viewer_url = f"http://localhost:8888/viewer/{project_id}"
                # Return the redirect URL as JSON so JavaScript can open the new tab
                return jsonify({'success': True, 'redirect_url': fastapi_viewer_url})
            else:
                # No PDF found; redirect to FastAPI app's root URL
                fastapi_upload_url = 'http://localhost:8888/'
                # Return success: True and the redirect_url to the upload page
                return jsonify({'success': True, 'redirect_url': fastapi_upload_url})
        else:
            return jsonify({'success': False, 'message': 'Failed to send project path to FastAPI'}), 500

    return jsonify({'success': False, 'error': 'Unauthorized'}), 401



@app.route('/delete_company', methods=['POST'])
def delete_company():
    if 'username' in session:
        data = request.get_json()
        company_name = data.get('company_name')
        username = session['username']
        company_path = os.path.join(cf.USER_PATH, username, 'customers', company_name)
        if os.path.exists(company_path):
            shutil.rmtree(company_path)
            return jsonify({'success': True})
        return jsonify({'success': False, 'error': 'Company not found'})
    return jsonify({'success': False, 'error': 'Unauthorized'}), 401

@app.route('/delete_project', methods=['POST'])
def delete_project():
    if 'username' in session:
        data = request.get_json()
        company_name = data.get('company_name')
        project_name = data.get('project_name')
        username = session['username']
        project_path = os.path.join(cf.USER_PATH, username, 'customers', company_name, project_name)
        if os.path.exists(project_path):
            import shutil
            shutil.rmtree(project_path)
            if remove_project_from_json(project_name):
                return jsonify({'success': True})
            else:
                return jsonify({'success': False, 'error': 'Project not found in JSON'}), 404
        return jsonify({'success': False, 'error': 'Project not found'}), 404
    return jsonify({'success': False, 'error': 'Unauthorized'}), 401


app.register_blueprint(vendors_bp)
app.register_blueprint(systems_bp)

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
