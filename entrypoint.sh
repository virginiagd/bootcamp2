#!/bin/sh

# Iniciar la aplicación
flask --app flaskr init-db
exec flask --app flaskr run --host=0.0.0.0
