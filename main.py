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


@app.route('/', methods=['GET'])
def index():
	return render_template('index.html', registrations=load_registrations()), 200


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

	save_registration(Registration(
		request.form['nick'],
		request.form['can_swim'],
		request.form['friend'],
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


if __name__ == '__main__':
	app.run(host='0.0.0.0', port=8080)
