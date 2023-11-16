import re
import json
from flask import Flask, render_template, request, abort, redirect
from registration import Registration

# Create a Flask web application
app = Flask(__name__, static_url_path='/static', static_folder='static', template_folder='templates')

# Specify the file where registration data is stored
data_file = 'registrations.json'

# Load registrations from the data file
def load_registrations():
    try:
        output = []
        with open(data_file, 'r') as file:
            loaded_registrations = json.load(file)

        # Convert loaded data into Registration objects
        for r in loaded_registrations:
            output.append(Registration(
                r['nick'],
                r['can_swim'],
                r['friend']
            ))

        return output
    except FileNotFoundError:
        return []

# Save a new registration to the data file
def save_registration(new_registration):
    registrations = load_registrations()

    registrations.append(new_registration)

    output = []
    for r in registrations:
        output.append({
            'nick': r.nick,
            'can_swim': r.can_swim,
            'friend': r.friend
        })

    with open(data_file, 'w') as file:
        json.dump(output, file, indent=4)

# Display registrations with friend names instead of indices
def display_registrations():
    registrations = load_registrations()
    registration_index = 0
    output = []
    for registration in registrations:
        if isinstance(registration.friend, int):
            registration.friend = registrations[registration.friend].nick
        output.append(registration)
        registration_index += 1
    return output

# Route for the home page
@app.route('/', methods=['GET'])
def index():
    return render_template('index.html', registrations=display_registrations()), 200

# Route for the registration page
@app.route('/registration', methods=['GET'])
def registration():
    return render_template('registration.html'), 200

# Handle registration form submission
@app.route('/register', methods=['POST'])
def register():
    # Validation checks for the submitted form data
    if request.form['can_swim'] == '0':
        abort(400, "Musíte být plavec.")

    if not re.match(r"[A-Za-z0-9]{2,20}", request.form['nick']):
        abort(400, "Přezdívka nesplňuje podmínky.")

    if request.form['friend'] is not None and not re.match(r"[A-Za-z0-9]{2,20}", request.form['friend']):
        abort(400, "Kamarád nesplňuje podmínky.")

    if nickname_exists(request.form['nick']):
        abort(400, "Přezdívka již existuje.")

    # If friend name already exists, add friend index
    friend = request.form['friend']
    if nickname_exists(request.form['friend']):
        friend = get_registration_index(request.form['friend'])

    # Check if somebody has user as friend, link together
    if friend_exists(request.form['nick']):
        modify_registration_friend(get_registration_index_by_friend(request.form['nick']), get_registrations_size())

    # Save the new registration
    save_registration(Registration(
        request.form['nick'],
        request.form['can_swim'],
        friend,
    ))

    # Redirect to the home page
    return redirect('/')

# API endpoint to check if a nickname already exists
@app.route('/api/check-nickname/<name>', methods=['GET'])
def check_nickname(name):
    return {'exists': True} if nickname_exists(name) else {'exists': False}

# Check if a nickname already exists
def nickname_exists(name):
    registrations = load_registrations()
    for r in registrations:
        if r.nick == name: return True
    return False

# Check if a friend's nickname already exists
def friend_exists(name):
    registrations = load_registrations()
    for r in registrations:
        if r.friend == name: return True
    return False

# Get the index of a registration by nickname
def get_registration_index(name):
    registrations = load_registrations()
    registration_index = 0
    for r in registrations:
        if r.nick == name: return registration_index
        registration_index += 1
    raise IndexError('Attempted to find the index of a nonexistent nickname.')

# Get the index of a registration by friend's nickname
def get_registration_index_by_friend(name):
    registrations = load_registrations()
    registration_index = 0
    for r in registrations:
        if r.friend == name: return registration_index
        registration_index += 1
    raise IndexError('Attempted to find the index of a nonexistent friend nickname.')

# Modify the friend of a registration
def modify_registration_friend(registration_index, new_friend):
    registrations = load_registrations()
    registrations[registration_index].friend = new_friend

    output = []
    for r in registrations:
        output.append({
            'nick': r.nick,
            'can_swim': r.can_swim,
            'friend': r.friend
        })

    with open(data_file, 'w') as file:
        json.dump(output, file, indent=4)

# Get the number of registrations
def get_registrations_size():
    return len(load_registrations())

# Run the application if this script is executed
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=7070)
