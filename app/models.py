from app import db

class Job(db.Model):
    __tablename__ = 'jobs'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    company_name = db.Column(db.String(255), nullable=False)
    location = db.Column(db.String(255), nullable=False)
    deadline = db.Column(db.Date, nullable=False)
    description = db.Column(db.Text, nullable=True)
