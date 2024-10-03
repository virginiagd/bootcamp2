from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from .auth import login_required
from .db import get_db

bp = Blueprint('survey', __name__, url_prefix='/survey')

#show all of the surveys
@bp.route('/')
@login_required
def survey():
    db = get_db()
    surveys = db.execute(
        'SELECT id, title, body, created, first, second'
        ' FROM survey'
        ' ORDER BY created DESC'
    ).fetchall()
    return render_template('form/survey.html', surveys=surveys)