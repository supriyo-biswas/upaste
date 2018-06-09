import os
import time
import secrets
import string
import sqlite3
import hashlib
from pygments import lexers, highlight
from pygments.formatters import HtmlFormatter
from flask import Flask, request, redirect, Response, render_template, g, abort

app = Flask(__name__)
db_file = os.path.dirname(os.path.realpath(__file__)) + '/data/db.sqlite'
langs = [i[:-5] for i in lexers.LEXERS]

def get_db():
	db = getattr(g, '_database', None)
	if db is None:
		db = g._database = sqlite3.connect(db_file)

	return db

def random_str(n):
	return ''.join([secrets.choice(string.ascii_lowercase + string.digits) for i in range(n)])

def save_paste(title, content, lang):
	short_content = content.strip()[:2048]
	if not short_content:
		raise ValueError("You can't create an empty paste.")

	title = title[:100].strip()
	if not title:
		title = None

	if lang not in langs:
		lang = type(lexers.guess_lexer(short_content)).__name__[:-5]

	db = get_db()

	for i in range(1, 10):
		id = random_str(8)
		if db.execute('SELECT id FROM pastes WHERE id = ?', [id]).fetchone() == None:
			hash = hashlib.sha256(content.encode()).hexdigest()

			db.execute('INSERT INTO pastes VALUES(?, ?, ?, ?, ?)', [
				id, title, lang, hash, int(time.time())
			])
			db.execute('INSERT OR IGNORE INTO contents VALUES(?, ?)', [
				hash, content
			])

			db.commit()
			return id

	raise ValueError('Failed to create paste. Please try again later.')

def get_paste(id):
	db = get_db()
	rv = db.execute('''
		SELECT title, lang, contents, create_time FROM pastes, contents
		WHERE id = ? AND pastes.hash = contents.hash
	''',[id]).fetchone()

	if rv is not None:
		rv = {
			'title': rv[0],
			'lang': rv[1],
			'content': rv[2],
			'time': time.ctime(rv[3])
		}

	return rv

def get_recent_pastes(page, limit):
	db = get_db()
	rv = []
	nextpage = False

	res = db.execute('''
		SELECT id, title, lang, create_time FROM pastes ORDER BY create_time DESC
		LIMIT ? OFFSET ?
	''', [limit + 1, (page - 1) * limit])

	for i in res.fetchall():
		rv.append({
			'id': i[0],
			'title': i[1],
			'lang': i[2],
			'time': time.ctime(i[3])
		})

	if len(rv) == limit + 1:
		del rv[-1]
		nextpage = True

	return rv, nextpage

@app.route('/', methods=['POST'])
def submit():
	title = request.form['title']
	content = request.form['content']
	lang = request.form['lang']

	try:
		paste_id = save_paste(title, content, lang)
		return redirect('/paste/' + paste_id)
	except ValueError as e:
		return render_template('home.html', langs=langs, error=str(e), title=title, content=content)

@app.route('/', methods=['GET'])
def home():
	return render_template('home.html', langs=langs)

@app.route('/recent/<num>')
def recent(num):
	try:
		num = int(num)
		pastes, nextpage = get_recent_pastes(num, 30)
		return render_template('recent.html', num=num, pastes=pastes, nextpage=nextpage)
	except ValueError:
		return (render_template('404.html'), 404)

@app.route('/paste/<id>')
def view(id):
	paste = get_paste(id)

	if paste is None:
		abort(404)
	else:
		formatter = HtmlFormatter()
		lexer = getattr(lexers, paste['lang'] + 'Lexer')
		paste['content'] = highlight(paste['content'], lexer(), formatter)
		paste['id'] = id

		return render_template('view.html', paste=paste)

@app.route('/raw/<id>')
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
	db = getattr(g, '_database', None)
	if db is not None:
		db.close()

if __name__ == '__main__':
	app.run()
