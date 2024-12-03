class Config:
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:euns1026!@localhost:3000/jobDB'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = 'your-secret-key'