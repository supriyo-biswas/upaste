# upaste

A tiny pastebin written using the [Flask](http://flask.pocoo.org/) framework.

## Manual installation

```bash
$ virtualenv -p python3 venv
$ . venv/bin/activate
$ pip install -r requirements.txt
$ python setup.py
$ FLASK_DEBUG=1 FLASK_APP=upaste.py flask run # For development
$ gunicorn -w 2 -b 0.0.0.0:5000 upaste:app # For production
```

Use the `Dockerfile` to create a Docker image.

# License

[MIT](https://opensource.org/licenses/MIT)
