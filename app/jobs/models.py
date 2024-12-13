from app import db

class Job(db.Model):
    """
    Job 테이블 모델
    """
    __tablename__ = 'jobs'

    id = db.Column(db.Integer, primary_key=True)  # 기본 키
    job_group = db.Column(db.String(255))  # 직업 그룹
    badge = db.Column(db.String(255))  # 뱃지
    company_name = db.Column(db.String(255))  # 회사 이름
    title = db.Column(db.String(255))  # 채용 공고 제목
    deadline = db.Column(db.Date)  # 마감일
    address_main = db.Column(db.String(255))  # 주요 근무지
    address_total = db.Column(db.String(255))  # 전체 근무지
    experience = db.Column(db.String(255))  # 경력
    education = db.Column(db.String(255))  # 학력
    employment_type = db.Column(db.String(255))  # 고용 유형
    salary = db.Column(db.String(255))  # 급여
    tech_stack = db.Column(db.Text)  # 기술 스택
    created_at = db.Column(db.DateTime, server_default=db.func.now())  # 생성 시간
    crawled_at = db.Column(db.DateTime)  # 크롤링 시간
    url = db.Column(db.Text)  # 채용 공고 URL
    description = db.Column(db.Text)  # 채용 공고 설명

    def to_dict(self):
        """
        Job 객체를 JSON 형식으로 변환
        """
        return {
            "id": self.id,
            "job_group": self.job_group,
            "badge": self.badge,
            "company_name": self.company_name,
            "title": self.title,
            "deadline": self.deadline.strftime('%Y-%m-%d') if self.deadline else None,
            "address_main": self.address_main,
            "address_total": self.address_total,
            "experience": self.experience,
            "education": self.education,
            "employment_type": self.employment_type,
            "salary": self.salary,
            "tech_stack": self.tech_stack,
            "created_at": self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            "crawled_at": self.crawled_at.strftime('%Y-%m-%d %H:%M:%S') if self.crawled_at else None,
            "url": self.url,
            "description": self.description
        }
