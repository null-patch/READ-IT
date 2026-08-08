# Alembic scaffold README

This directory contains Alembic configuration wired to the project's SQLAlchemy metadata.

Usage:

1. Ensure DATABASE_URL is set in your environment or .env file.

2. Create a new revision (autogenerate):

   alembic revision --autogenerate -m "create initial tables"

3. Inspect and adjust the generated revision under alembic/versions/ before applying.

4. Apply migrations:

   alembic upgrade head

Notes:
- The env.py tries to import the project's Base metadata from app.database.database.Base.
  If you add models in other modules, ensure they are imported so that metadata includes them when autogenerating.
