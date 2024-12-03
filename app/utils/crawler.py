import requests
from bs4 import BeautifulSoup
from app import db
from app.models import Job

def crawl_saramin():
    url = "https://www.saramin.co.kr/zf_user/search?keydownAccess=&searchType=search&searchword=python&panel_type=&search_optional_item=y&search_done=y&panel_count=y&preview=y"
    
    try:
        response = requests.get(url)
        response.raise_for_status()  # 요청이 성공했는지 확인
        soup = BeautifulSoup(response.text, 'html.parser')

        # 채용 공고를 찾기 위한 CSS 선택자 사용 (예시)
        job_list = soup.select('.item_recruit')  # 실제 CSS 클래스 이름으로 변경해야 합니다.

        for job in job_list:
            title = job.select_one('.job_tit').text.strip()  # 제목 추출
            company = job.select_one('.company').text.strip()  # 회사명 추출

            # 데이터베이스에 저장
            new_job = Job(title=title, company=company)
            db.session.add(new_job)

        db.session.commit()  # 데이터베이스에 변경사항 저장

    except Exception as e:
        print(f"Error occurred: {e}")