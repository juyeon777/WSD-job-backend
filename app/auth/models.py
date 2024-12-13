from app import db, bcrypt

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)

    def set_password(self, password):
        """비밀번호를 해싱하여 저장"""
        self.password = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        """입력된 비밀번호와 저장된 해시를 비교"""
        return bcrypt.check_password_hash(self.password, password)

    def to_dict(self):
        """사용자 정보를 JSON으로 변환"""
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email
        }
