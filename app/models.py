from app import db
from werkzeug.security import generate_password_hash, check_password_hash

# Job 모델
class Job(db.Model):
    __tablename__ = 'jobs'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    company_name = db.Column(db.String(255), nullable=False)
    location = db.Column(db.String(255), nullable=False)
    deadline = db.Column(db.Date, nullable=False)
    description = db.Column(db.Text, nullable=True)

# User 모델 (회원 관리)
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
