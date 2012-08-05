
from hamlish_jinja import HamlishExtension

from flask import Flask, render_template

from werkzeug.debug import DebuggedApplication

from .keys import blueprint as keys


app = Flask(__name__)
app.config['SECRET_KEY'] = "abcd"
app.debug = True
if app.debug:
    app.wsgi_app = DebuggedApplication(app.wsgi_app, evalex=True)

app.jinja_options['extensions'].append(HamlishExtension)

app.jinja_env.hamlish_mode = 'debug' if app.debug else 'compact'
app.jinja_env.hamlish_enable_div_shortcut = True

app.register_blueprint(keys, url_prefix='/keys')


@app.route('/')
def index():
    return render_template("index.haml")


application = app
