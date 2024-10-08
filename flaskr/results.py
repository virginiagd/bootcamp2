from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from .auth import login_required
from .db import get_db

bp = Blueprint('results', __name__, url_prefix='/results')

@bp.route('/<int:id>', methods=('GET',))
@login_required
def results(id):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute(
        'SELECT title, body FROM survey WHERE id = %s',
        (id,)
    )
    survey = cursor.fetchone()

    if survey is None:
        abort(404, f"Survey id {id} does not exist.")

    # Fetch the results
    cursor.execute(
        'SELECT vote_option, COUNT(*) as count FROM votes WHERE survey_id = %s GROUP BY vote_option',
        (id,)
    )
    results = cursor.fetchall()
    cursor.close()

    # Check if results is empty
    if not results:
        flash('No votes found for this survey.')
        return redirect(url_for('survey.survey'))

    labels = [result['vote_option'] for result in results]
    data = [result['count'] for result in results]

    print("Labels:", labels)  # Debugging line
    print("Data:", data)      # Debugging line

    return render_template('results/results.html', survey=survey, labels=labels, data=data)
