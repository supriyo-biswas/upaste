import os
import time
import random
import string
import sqlite3
from flask import Flask, request, redirect, Response, render_template
from flask import g, abort

app = Flask(__name__)
db_file = os.path.dirname(os.path.realpath(__file__)) + "/data/db.sqlite"

def get_db():
	db = getattr(g, "_database", None)
	if db is None:
		db = g._database = sqlite3.connect(db_file)

	return db

def random_str(n):
	s = ""

	for i in range(0, n):
		s += random.choice(string.ascii_lowercase + string.digits)

	return s

def save_paste(title, content):
	if not content.strip():
		raise ValueError("You can't create an empty paste.")

	title = title.strip()
	if not title:
		title = None

	db = get_db()

	for i in range(1, 10):
		id = random_str(8)

		if db.execute("SELECT id FROM pastes WHERE id = ?", [id]).fetchone() == None:
			db.execute("INSERT INTO pastes VALUES(?, ?, ?, ?)", [
				id, title, content, int(time.time())
			])
			db.commit()
			return id

	raise ValueError("Failed to create paste. Please try again later.")

def get_paste(id):
	db = get_db()
	res = db.execute('SELECT * FROM pastes WHERE id = ?', [id]).fetchone()

	if res is not None:
		res = {
			'id': res[0],
			'title': res[1],
			'content': res[2],
			'time': time.ctime(res[3])
		}

	return res

def get_recent_pastes():
	db = get_db()
	rv = []

	res = db.execute("SELECT id, title, create_time FROM pastes ORDER BY create_time DESC LIMIT 30")

	for i in res.fetchall():
		rv.append({
			'id': i[0],
			'title': i[1],
			'time': time.ctime(i[2])
		})

	return rv

@app.route("/", methods=["GET", "POST"])
def home():
	if request.method == "GET":
		return render_template("home.html")
	else:
		title = request.form["title"]
		content = request.form["content"]

		try:
			paste_id = save_paste(title, content)
			return redirect("/paste/" + paste_id)
		except ValueError as e:
			return render_template("home.html", error=str(e), title=title, content=content)

@app.route("/recent")
def recent():
	return render_template("recent.html", pastes=get_recent_pastes())

@app.route("/paste/<id>")
def view(id):
	paste = get_paste(id)

	if paste is None:
		abort(404)
	else:
		return render_template('view.html', paste=paste)

@app.route("/raw/<id>")
def view_raw(id):
	paste = get_paste(id)

	if paste is None:
		abort(404)
	else:
		return Response(paste['content'], mimetype='text/plain')

@app.errorhandler(404)
def page_not_found(exception):
	return (render_template('404.html'), 404)

@app.teardown_appcontext
def close_db(exception):
	db = getattr(g, "_database", None)
	if db is not None:
		db.close()

if __name__ == "__main__":
	app.run()
