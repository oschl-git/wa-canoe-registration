import re
import json

from flask import Flask, render_template, request, abort, redirect
from registration import Registration

app = Flask(__name__, static_url_path='/static', static_folder='static', template_folder='templates')

data_file = 'registrations.json'


def load_registrations():
	try:
		output = []
		with open(data_file, 'r') as file:
			loaded_registrations = json.load(file)

		for r in loaded_registrations:
			output.append(Registration(
				r['nick'],
				r['can_swim'],
				r['friend']
			))

		return output
	except FileNotFoundError:
		return []


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


@app.route('/', methods=['GET'])
def index():
	return render_template('index.html', registrations=display_registrations()), 200


@app.route('/registration', methods=['GET'])
def registration():
	return render_template('registration.html'), 200


@app.route('/register', methods=['POST'])
def register():
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

	save_registration(Registration(
		request.form['nick'],
		request.form['can_swim'],
		friend,
	))

	return redirect('/')


@app.route('/api/check-nickname/<name>', methods=['GET'])
def check_nickname(name):
	return {'exists': True} if nickname_exists(name) else {'exists': False}


def nickname_exists(name):
	registrations = load_registrations()
	for r in registrations:
		if r.nick == name: return True
	return False


def friend_exists(name):
	registrations = load_registrations()
	for r in registrations:
		if r.friend == name: return True
	return False


def get_registration_index(name):
	registrations = load_registrations()
	registration_index = 0
	for r in registrations:
		if r.nick == name: return registration_index
		registration_index += 1
	raise IndexError('Attempted to find index of nonexistent nickname.')


def get_registration_index_by_friend(name):
	registrations = load_registrations()
	registration_index = 0
	for r in registrations:
		if r.friend == name: return registration_index
		registration_index += 1
	raise IndexError('Attempted to find index of nonexistent nickname.')


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


def get_registrations_size():
	return len(load_registrations())


if __name__ == '__main__':
	app.run(host='0.0.0.0', port=8080)
