from flask import Flask, jsonify
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
import mysql.connector
from datetime import datetime
import time
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO)

# Flask 애플리케이션 생성
app = Flask(__name__)

# MySQL 연결 설정
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="juyeon777",
    database="job_portal"
)
cursor = db.cursor()

# 테이블 생성 함수
def create_table():
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
    db.commit()
    print("Table 'jobs' created or already exists.")

# 크롤링 함수
def crawl_saramin():
    base_url = "https://www.saramin.co.kr/zf_user/jobs/list/job-category"
    
    # Selenium WebDriver 설정
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # 브라우저 창을 띄우지 않음 (옵션)
    
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)

    jobs = []
    
    print("Starting crawling process...")
    
    for page in range(1, 11):  # 최대 10페이지까지 크롤링
        try:
            print(f"Crawling page {page}...")
            driver.get(f"{base_url}?page={page}")
            time.sleep(2)  # 페이지 로딩 대기
            
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            job_items = soup.select('.item_recruit')

            print(f"Found {len(job_items)} job listings on this page.")
            
            for item in job_items:
                job_data = extract_job_data(item)
                if job_data and not is_duplicate(job_data['url']):
                    jobs.append(job_data)
                    save_to_database(job_data)
                    print(f"Saved job: {job_data['title']}")
                else:
                    logging.info(f"Skipped duplicate or invalid job: {job_data}")
                
                if len(jobs) >= 100:  # 최대 100개 저장
                    break
            
            time.sleep(1)  # 대기 시간 조정
            
        except Exception as e:
            logging.error(f"Error occurred on page {page}: {e}")
            time.sleep(5)

    driver.quit()  # WebDriver 종료
    
    print(f"Crawling finished. Total jobs crawled: {len(jobs)}")
    return jobs

# 데이터 추출 함수
def extract_job_data(job):
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
    except Exception as e:
        logging.error(f"Error extracting job data: {e}")
        return None

# 채용 공고 설명 가져오기
def get_job_description(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        description = soup.select_one('.job_summary')
        return description.text.strip() if description else ''
    except Exception as e:
        logging.error(f"Error fetching job description: {e}")
        return ''

# 중복 확인 함수
def is_duplicate(url):
    cursor.execute("SELECT COUNT(*) FROM jobs WHERE url = %s", (url,))
    return cursor.fetchone()[0] > 0

# 데이터베이스에 저장하는 함수
def save_to_database(job_data):
    sql = """
    INSERT INTO jobs (job_group, badge, company_name, title, deadline, address_main, address_total, 
                      experience, education, employment_type, salary, tech_stack, createdAt, crawledAt, url, description)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    
    values = tuple(job_data.values())
    
    try:
        cursor.execute(sql, values)
        db.commit()
    except mysql.connector.Error as err:
        logging.error(f"Error saving to database: {err}")

@app.route('/crawl', methods=['GET'])
def start_crawling():
    create_table()
    jobs = crawl_saramin()
    return jsonify({"message": f"Crawled {len(jobs)} jobs successfully"})

if __name__ == '__main__':
    create_table()
    crawled_jobs = crawl_saramin()
    print(f"Successfully crawled and saved {len(crawled_jobs)} jobs.")
