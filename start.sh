#!/usr/bin/env bash
# Exit script immediately if any command fails
set -o errexit

# Define the path to your SQLite database
# If you are using a Render Persistent Disk, this should be the path to the mounted disk
# e.g., DB_FILE="/data/db.sqlite3"
DB_FILE="db.sqlite3"

if [ ! -f "$DB_FILE" ]; then
    echo "SQLite database ($DB_FILE) not found. Running initial setup..."


    # 1. Run migrations (this automatically creates the db.sqlite3 file)
    python manage.py migrate --no-input

    # 2. Run the pre-seeder command (from the previous step)
    python manage.py seed_db

    # 3. Create sample articles in SQL
    python manage.py populate_db

    # 4. Vectorize existing articles and store in LanceDB
    python manage.py index_articles


    echo "Initial setup complete!"
else
    echo "SQLite database ($DB_FILE) already exists. Skipping migrations and seeding."
fi

echo "Starting Django server..."

# Render uses the $PORT environment variable (defaults to 10000).
# You MUST bind to 0.0.0.0, otherwise Render cannot route traffic to your app.
#PORT=${PORT:-8000}
#python manage.py runserver 0.0.0.0:$PORT
#python manage.py runserver

gunicorn --bind 0.0.0.0:$PORT core.wsgi:application