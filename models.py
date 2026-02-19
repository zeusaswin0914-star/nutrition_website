"""Optional SQLAlchemy models for storing predictions.

This module is intentionally tolerant when `flask_sqlalchemy` is not
installed. The application currently supports MongoDB; keep these
models as an optional SQLite fallback for environments that prefer
SQLAlchemy.
"""

from datetime import datetime
import sys

try:
    from flask_sqlalchemy import SQLAlchemy
    HAS_SQLA = True
except Exception:
    SQLAlchemy = None
    HAS_SQLA = False


if HAS_SQLA:
    db = SQLAlchemy()


    class Prediction(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        created_at = db.Column(db.DateTime, default=datetime.utcnow)
        inputs = db.Column(db.Text, nullable=False)
        prediction = db.Column(db.Float, nullable=False)
        report = db.Column(db.Text)
        recommendations = db.Column(db.Text)


    def init_db(app):
        """Initialize the database (create tables)."""
        db.init_app(app)
        with app.app_context():
            db.create_all()

else:
    # Provide placeholders so importing modules don't crash. Callers
    # can check `HAS_SQLA` to decide whether to use SQLAlchemy.

    db = None


    class Prediction:  # pragma: no cover - simple placeholder
        def __init__(self, *args, **kwargs):
            raise RuntimeError('flask_sqlalchemy not available; install it to use SQLAlchemy models')


    def init_db(app):
        print('Notice: flask_sqlalchemy not installed; skipping SQLAlchemy init', file=sys.stderr)
