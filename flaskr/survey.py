from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from .auth import login_required
from .db import get_db

bp = Blueprint('survey', __name__, url_prefix='/surveys')

#show all of the surveys
@bp.route('/')
@login_required
def survey():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute(
        'SELECT id, title, body, created, first, second'
        ' FROM survey'
        ' ORDER BY created DESC'
    )
    surveys = cursor.fetchall()
    cursor.close()
    return render_template('form/surveys.html', surveys=surveys)

# Create a new survey (only accessible to admin user with id = 1)
@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    # Check if the user is the administrator
    if g.user['id'] != 1:
        abort(403, "You do not have permission to access this page.")

    if request.method == 'POST':
        title = request.form.get('title')
        body = request.form.get('body')
        first_option = request.form.get('first_option')
        second_option = request.form.get('second_option')
        error = None

        # Validate that a title and both options are provided
        if not title:
            error = 'Title is required.'
        elif not first_option or not second_option:
            error = 'Both options are required.'

        if error is not None:
            flash(error)  # Show the error message to the user
        else:
            db = get_db()
            cursor = db.cursor()
            # Insert the new survey into the database, initializing votes for both options to 0
            cursor.execute(
                'INSERT INTO survey (title, body, first, second)'
                ' VALUES (%s, %s, %s, %s)',
                (title, body, 0, 0)  
            )
            db.commit()
            cursor.close()
            return redirect(url_for('survey.survey'))

    return render_template('form/create_survey.html')

# Show details of a single survey
@bp.route('/<int:id>', methods=('GET',))
@login_required
def show_survey(id):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute(
        'SELECT id, title, body, first, second'
        ' FROM survey WHERE id = %s',  # Get the survey by ID
        (id,)
    )
    survey=cursor.fetchone()
    # If the survey does not exist, return a 404 error
    if survey is None:
        abort(404, f"Survey id {id} does not exist.")

    # Check if the user has already voted on this survey
    cursor.execute(
        'SELECT id FROM votes WHERE user_id = %s AND survey_id = %s',
        (g.user['id'], id)
    )
    vote=cursor.fetchone()
    cursor.close()

    # Pass information about whether the user has already voted to the template
    already_voted = vote is not None

    return render_template('form/show_survey.html', survey=survey, already_voted=already_voted)

# Handle voting on a survey
@bp.route('/<int:id>/vote', methods=('POST',))
@login_required
def vote(id):
    option = request.form.get('option')  # Get the selected option from the form
    db = get_db()
    cursor = db.cursor()
    # Check if the user has already voted on this survey
    cursor.execute(
        'SELECT id FROM votes WHERE user_id = %s AND survey_id = %s',
        (g.user['id'], id)
    )
    vote = cursor.fetchone()

    if vote:
        flash('You have already voted in this survey.')  # Prevent voting again
        return redirect(url_for('survey.show_survey', id=id))

    # Increment the vote count for the selected option
    if option == 'first':
        cursor.execute('UPDATE survey SET first = first + 1 WHERE id = %s', (id,))
    elif option == 'second':
        cursor.execute('UPDATE survey SET second = second + 1 WHERE id = %s', (id,))
    else:
        flash('Invalid option selected.')

    # Record that the user has voted on this survey
    cursor.execute(
        'INSERT INTO votes (user_id, survey_id, vote_option) VALUES (%s, %s, %s)',
        (g.user['id'], id, option)
    )
    cursor.close()
    db.commit()
    return redirect(url_for('survey.show_survey', id=id))

# Delete a survey (only accessible to admin user with id = 1)
@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete_survey(id):
    db = get_db()
    cursor = db.cursor()
    # Check if the user is the administrator
    if g.user['id'] != 1:
        abort(403, "You do not have permission to delete surveys.")

    # Check if the survey exists
    cursor.execute(
        'SELECT id FROM survey WHERE id = %s',
        (id,)
    )
    survey = cursor.fetchone()

    if survey is None:
        abort(404, f"Survey id {id} does not exist.")

    # Delete the survey from the database
    cursor.execute('DELETE FROM votes WHERE survey_id = %s', (id,))
    cursor.execute('DELETE FROM survey WHERE id = %s', (id,))
    cursor.close()
    db.commit()

    flash(f"Survey {id} has been deleted.")
    return redirect(url_for('survey.survey'))
