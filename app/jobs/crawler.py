import requests
from flask import Flask, jsonify
from bs4 import BeautifulSoup
import mysql.connector
from datetime import datetime
import time
import logging
import os
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Flask 애플리케이션 생성
app = Flask(__name__)

# MySQL 연결 설정
db_config = {
    "host": os.getenv("DB_HOST"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "database": os.getenv("DB_NAME")
}

# 데이터베이스 연결 함수
def get_db_connection():
    return mysql.connector.connect(**db_config)

# 테이블 생성 함수
def create_table():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS jobs (
        id INT AUTO_INCREMENT PRIMARY KEY,
        job_group VARCHAR(255),
        badge VARCHAR(255),
        company_name VARCHAR(255),
        title VARCHAR(255),
        deadline DATE,
        address_main VARCHAR(255),
        address_total VARCHAR(255),
        experience VARCHAR(255),
        education VARCHAR(255),
        employment_type VARCHAR(255),
        salary VARCHAR(255),
        tech_stack TEXT,
        createdAt DATETIME,
        crawledAt DATETIME,
        url TEXT,
        description TEXT
    )
    """)
    conn.commit()
    cursor.close()
    conn.close()
    logging.info("Table 'jobs' created or already exists.")

# 크롤링 함수
def crawl_saramin(max_jobs=50, max_retries=3):
    """
    사람인 웹사이트에서 채용 공고 크롤링
    - max_jobs: 최대 가져올 채용 공고 수
    - max_retries: 요청 실패 시 재시도 횟수
    """
    base_url = "https://www.saramin.co.kr/zf_user/jobs/list/job-category"
    jobs = []
    page = 1

    while len(jobs) < max_jobs:
        try:
            logging.info(f"Crawling page {page}...")

            # 페이지 요청
            response = requests.get(f"{base_url}?page={page}")
            response.raise_for_status()

            # HTML 파싱
            soup = BeautifulSoup(response.text, 'html.parser')
            job_items = soup.select('.item_recruit')

            for item in job_items:
                if len(jobs) >= max_jobs:
                    break

                # 채용 공고 데이터 추출
                job_data = extract_job_data(item)

                # 중복 확인 및 저장
                if job_data and job_data['url'] not in existing_urls:
                    jobs.append(job_data)
                    save_to_database(job_data)
                    existing_urls.add(job_data['url'])
                    logging.info(f"Saved job: {job_data['title']}")
                else:
                    logging.info(f"Skipped duplicate or invalid job")

            page += 1
            time.sleep(1)  # 대기 시간 조정

        except requests.RequestException as e:
            logging.error(f"Error occurred on page {page}: {e}")
            if max_retries > 0:
                max_retries -= 1
                time.sleep(5)
                continue
            else:
                break

    logging.info(f"Crawling finished. Total jobs crawled: {len(jobs)}")
    return jobs


# 데이터 추출 함수
def extract_job_data(job):
    """
    단일 채용 공고 데이터 추출
    """
    try:
        return {
            'job_group': '91,92',
            'badge': job.select_one('.badge')['src'] if job.select_one('.badge') and job.select_one('.badge').has_attr('src') else None,
            'company_name': job.select_one('.corp_name a')['title'] if job.select_one('.corp_name a') else None,
            'title': job.select_one('.job_tit a')['title'] if job.select_one('.job_tit a') else None,
            'deadline': job.select_one('.date')['title'] if job.select_one('.date') else None,
            'address_main': job.select_one('.work_place').text.strip() if job.select_one('.work_place') else None,
            'address_total': job.select_one('.work_place').text.strip() if job.select_one('.work_place') else None,
            'experience': job.select_one('.career').text.strip() if job.select_one('.career') else None,
            'education': job.select_one('.education').text.strip() if job.select_one('.education') else None,
            'employment_type': job.select_one('.employment_type').text.strip() if job.select_one('.employment_type') else None,
            'salary': job.select_one('.salary').text.strip() if job.select_one('.salary') else None,
            'tech_stack': ', '.join([tag.text.strip() for tag in job.select('.job_sector span')]) if job.select('.job_sector span') else None,
            'createdAt': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'crawledAt': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'url': 'https://www.saramin.co.kr' + job.select_one('.job_tit a')['href'] if job.select_one('.job_tit a') else None,
            'description': get_job_description('https://www.saramin.co.kr' + job.select_one('.job_tit a')['href']) if job.select_one('.job_tit a') else None
        }
    except KeyError as e:
        logging.error(f"Missing key during job data extraction: {e}")
        return None
    except Exception as e:
        logging.error(f"Unexpected error during job data extraction: {e}")
        return None

# 채용 공고 설명 가져오기
def get_job_description(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        description = soup.select_one('.job_summary')
        return description.text.strip() if description else ''
    except Exception as e:
        logging.error(f"Error fetching job description: {e}")
        return ''

# 중복 확인 함수
def is_duplicate(url):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM jobs WHERE url = %s", (url,))
    result = cursor.fetchone()[0] > 0
    cursor.close()
    conn.close()
    return result

# 데이터베이스에 저장하는 함수
def save_to_database(job_data):
    sql = """
    INSERT INTO jobs (job_group, badge, company_name, title, deadline, address_main, address_total, 
                      experience, education, employment_type, salary, tech_stack, createdAt, crawledAt, url, description)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    
    values = tuple(job_data.values())
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(sql, values)
        conn.commit()
        cursor.close()
        conn.close()
    except mysql.connector.Error as err:
        logging.error(f"Error saving to database: {err}")

@app.route('/crawl', methods=['GET'])
def start_crawling():
    create_table()
    jobs = crawl_saramin(max_jobs=50)
    return jsonify({"message": f"Crawled {len(jobs)} jobs successfully"})

if __name__ == '__main__':
    create_table()
    crawled_jobs = crawl_saramin(max_jobs=50)
    print(f"Successfully crawled and saved {len(crawled_jobs)} jobs.")
