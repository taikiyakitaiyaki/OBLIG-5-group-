from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Application(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), nullable=False)
    parent1_name = db.Column(db.String(120), nullable=False)
    parent2_name = db.Column(db.String(120), nullable=True)
    parent1_address = db.Column(db.String(120), nullable=False)
    parent2_address = db.Column(db.String(120), nullable=True)
    parent1_phone = db.Column(db.String(20), nullable=False)
    parent2_phone = db.Column(db.String(20), nullable=True)
    parent1_id = db.Column(db.String(20), nullable=False)
    parent2_id = db.Column(db.String(20), nullable=True)
    child1_id = db.Column(db.String(20), nullable=False)
    child1_age = db.Column(db.Integer, nullable=False)
    child2_id = db.Column(db.String(20), nullable=True)
    child2_age = db.Column(db.Integer, nullable=True)
    priority = db.Column(db.Boolean, nullable=False)
    kindergarten_list = db.Column(db.String(200), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    siblings = db.Column(db.String(10), nullable=False)
    income = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(10), nullable=False)
    
    
