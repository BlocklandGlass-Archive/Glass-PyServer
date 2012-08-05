from flask import render_template

from .keygen import blueprint as keygen
from ..helpers import NestableBlueprint

blueprint = NestableBlueprint('keygen', __name__)
blueprint.register_blueprint(keygen, url_prefix='/generate')


@blueprint.route('/')
def index():
    return render_template("keys/index.haml")
