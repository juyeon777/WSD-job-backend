from sqlalchemy import (
    Column, Integer, String, ForeignKey, DateTime, Text, create_engine
)
from sqlalchemy.orm import relationship, declarative_base, sessionmaker
from datetime import datetime
import os
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

# Base 클래스 초기화
Base = declarative_base()

# 사용자 테이블 (users)
class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password = Column(String(255), nullable=False)  # 비밀번호는 해싱 후 저장
    created_at = Column(DateTime, default=datetime.utcnow)

    # 관계 설정
    applications = relationship("Application", back_populates="user", cascade="all, delete-orphan")
    bookmarks = relationship("Bookmark", back_populates="user", cascade="all, delete-orphan")
    resumes = relationship("Resume", back_populates="user", cascade="all, delete-orphan")

# 채용 공고 테이블 (jobs)
class Job(Base):
    __tablename__ = 'jobs'

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(200), nullable=False)
    company_id = Column(Integer, ForeignKey('companies.id'))
    description = Column(Text)
    location = Column(String(100))
    salary = Column(String(50))  # 급여 정보
    created_at = Column(DateTime, default=datetime.utcnow)

    # 관계 설정
    applications = relationship("Application", back_populates="job", cascade="all, delete-orphan")
    bookmarks = relationship("Bookmark", back_populates="job", cascade="all, delete-orphan")
    company = relationship("Company", back_populates="jobs")

# 회사 정보 테이블 (companies)
class Company(Base):
    __tablename__ = 'companies'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    industry = Column(String(100))
    location = Column(String(100))
    description = Column(Text)

    # 관계 설정
    jobs = relationship("Job", back_populates="company", cascade="all, delete-orphan")

# 지원 내역 테이블 (applications)
class Application(Base):
    __tablename__ = 'applications'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    job_id = Column(Integer, ForeignKey('jobs.id'), nullable=False)
    applied_at = Column(DateTime, default=datetime.utcnow)
    status = Column(String(50), default="지원")  # 상태: 지원, 취소 등

    # 관계 설정
    user = relationship("User", back_populates="applications")
    job = relationship("Job", back_populates="applications")

# 북마크 테이블 (bookmarks)
class Bookmark(Base):
    __tablename__ = 'bookmarks'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    job_id = Column(Integer, ForeignKey('jobs.id'), nullable=False)
    bookmarked_at = Column(DateTime, default=datetime.utcnow)

    # 관계 설정
    user = relationship("User", back_populates="bookmarks")
    job = relationship("Job", back_populates="bookmarks")

# 이력서 테이블 (resumes)
class Resume(Base):
    __tablename__ = 'resumes'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # 관계 설정
    user = relationship("User", back_populates="resumes")

# 토큰 블랙리스트 테이블 (token_blacklist)
class TokenBlacklist(Base):
    __tablename__ = 'token_blacklist'

    id = Column(Integer, primary_key=True, autoincrement=True)
    token = Column(String(500), nullable=False, unique=True)
    blacklisted_at = Column(DateTime, default=datetime.utcnow)

# 로그인 히스토리 테이블 (login_history)
class LoginHistory(Base):
    __tablename__ = 'login_history'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    ip_address = Column(String(50))
    logged_in_at = Column(DateTime, default=datetime.utcnow)

    # 관계 설정
    user = relationship("User")

# 데이터베이스 연결 설정
def get_engine():
    return create_engine(
        f"mysql+mysqlconnector://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
        f"@{os.getenv('DB_HOST')}/{os.getenv('DB_NAME')}",
        echo=True
    )

# 테이블 생성 함수
def create_tables():
    engine = get_engine()
    Base.metadata.create_all(engine)
    print("테이블 생성 완료")

# 세션 팩토리 설정
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=get_engine())
