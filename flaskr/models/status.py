from flaskr import db
from datetime import datetime, date


# Status
class Status(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)

    veokit_system_id = db.Column(db.Integer, nullable=False, index=True)
