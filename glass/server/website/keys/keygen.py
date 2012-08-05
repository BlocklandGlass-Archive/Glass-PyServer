import M2Crypto

from flask.ext.wtf import Form

from flask import render_template, Blueprint


blueprint = Blueprint('keys.keygen', __name__)

keyLength = 2048
publicExponent = 65537


def noop(*args, **kwargs):
    pass


def generateKey():
    pair = M2Crypto.RSA.gen_key(keyLength, publicExponent, callback=noop)
    return pair


class KeyGenForm(Form):
    pass


@blueprint.route('/', methods=('GET', 'POST'))
def keyGen():
    form = KeyGenForm()
    if form.validate_on_submit():
        key = generateKey()
        return key.as_pem(None)
    return render_template("keys/keygen.haml", form=form)
