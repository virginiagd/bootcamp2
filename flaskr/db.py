
import time
import click
from flask import current_app, g
import mysql.connector
from mysql.connector import Error

def get_db():
    if 'db' not in g:
        g.db = mysql.connector.connect(
            host=current_app.config['DB_HOST'],
            user=current_app.config['DB_USER'],
            password=current_app.config['DB_PASSWORD'],
            database=current_app.config['DB_NAME']
        )

    return g.db


def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()


def init_db():
    while True:
        try:
            db = get_db()
            if db.is_connected():
                click.echo("MySQL database is ready!")
                cursor = db.cursor()
            
                with current_app.open_resource('schema.sql') as f:
                    cursor.execute(f.read().decode('utf8'))

                cursor.close()
                break
        except Error as e:
            click.echo("Waiting for MySQL database to be ready...")
            time.sleep(5)



@click.command('init-db')
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')

def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)