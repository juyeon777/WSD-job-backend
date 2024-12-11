class Config:
    SECRET_KEY = 'supersecretkey'  # JWT 토큰 생성을 위한 Secret Key
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:juyeon777@localhost/job_portal'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
