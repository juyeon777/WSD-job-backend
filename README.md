# YeonHire - 채용 공고 플랫폼

**YeonHire**는 채용 공고를 쉽게 검색하고 지원할 수 있는 웹 애플리케이션입니다.  
Flask 백엔드를 기반으로 하고 Swagger를 통해 API 문서를 제공합니다.

---

## 📚 **기술 스택**

- **Backend**: Flask  
- **Database**: MySQL  
- **ORM**: Flask-SQLAlchemy  
- **인증**: JWT (Flask-JWT-Extended)  
- **API 문서화**: Swagger UI  
- **배포**: J-Cloud  

---

## 📂 **프로젝트 구조**

WSD-job-backend/
│
├── app/
│   ├── api/                 # API 라우트
│   │   ├── __init__.py
│   │   ├── auth.py          # 사용자 인증 관련 API
│   │   ├── jobs.py          # 채용 공고 관련 API
│   │   ├── applications.py  # 지원 내역 관리 API
│   │   └── bookmarks.py     # 즐겨찾기 관리 API
│   │
│   ├── crawler/             # 크롤링 관련 코드
│   │   ├── crawler.py       # 크롤링 스크립트
│   │
│   ├── models/              # 데이터베이스 모델
│   │   ├── __init__.py
│   │   └── models.py
│   │
│   ├── static/              # 정적 파일
│   │   └── swagger.json     # Swagger 문서 정의 파일
│   │
│   ├── templates/           # HTML 템플릿 파일
│   │   ├── index.html       # 메인 페이지
│   │   └── jobs.html        # 채용 공고 페이지
│   │
│   ├── config.py            # 애플리케이션 설정
│   ├── main.py              # Flask 메인 진입점
│   ├── __init__.py          # 애플리케이션 초기화
│
├── migrations/              # 마이그레이션 파일
│   ├── versions/            # 버전 관리
│   └── alembic.ini          # Alembic 설정 파일
│
├── scripts/                 # 추가 스크립트
│   ├── jobs_sample.py       # 샘플 데이터 스크립트
│   └── script.py.mako       # 스크립트 템플릿
│
├── .env                     # 환경 변수 파일
├── .gitignore               # Git 무시할 파일 목록
├── README.md                # 프로젝트 문서
├── requirements.txt         # 의존성 목록
└── run.py                   # 서버 실행 파일
