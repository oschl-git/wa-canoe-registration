import re

from flask import Flask, render_template, request, abort, redirect
from registration import Registration

app = Flask(__name__, static_url_path='/static', static_folder='static', template_folder='templates')
registrations = []


@app.route('/', methods=['GET'])
def index():
	return render_template('index.html', registrations=registrations), 200


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

	registrations.append(Registration(
		request.form['nick'],
		request.form['can_swim'],
		request.form['friend'],
	))

	return redirect('/')


@app.route('/api/check-nickname/<name>', methods=['GET'])
def check_nickname(name):
	return {'exists': True} if nickname_exists(name) else {'exists': False}


def nickname_exists(name):
	for r in registrations:
		if r.nick == name: return True
	return False


if __name__ == '__main__':
	app.run(host='0.0.0.0', port=8080)
