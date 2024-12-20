import requests
from bs4 import BeautifulSoup
from datetime import datetime
import logging
import mysql.connector
import os
from dotenv import load_dotenv
import time
import json
import requests

# 환경 변수 로드
load_dotenv()

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class DatabaseManager:
    def __init__(self):
        self.db_config = {
            "host": os.getenv("DB_HOST"),
            "user": os.getenv("DB_USER"),
            "password": os.getenv("DB_PASSWORD"),
            "database": os.getenv("DB_NAME"),
        }
        self.connection = None

    def connect(self):
        if self.connection is None or not self.connection.is_connected():
            self.connection = mysql.connector.connect(**self.db_config)

    def close(self):
        if self.connection and self.connection.is_connected():
            self.connection.close()

    def execute(self, query, params=None):
        try:
            self.connect()
            cursor = self.connection.cursor()
            cursor.execute(query, params)
            self.connection.commit()
            cursor.close()
        except mysql.connector.Error as err:
            logging.error(f"Database error: {err}")

    def fetch_one(self, query, params=None):
        try:
            self.connect()
            cursor = self.connection.cursor()
            cursor.execute(query, params)
            result = cursor.fetchone()
            cursor.close()
            return result
        except mysql.connector.Error as err:
            logging.error(f"Database error: {err}")
            return None


class SaraminCrawler:
    def __init__(self, db_manager, max_retries=3):
        self.base_url = "https://www.saramin.co.kr/zf_user/jobs/list/job-category"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.max_retries = max_retries
        self.db_manager = db_manager
        self.existing_urls = set()
        self.load_existing_urls()

    def load_existing_urls(self):
        query = "SELECT url FROM jobs"
        try:
            self.db_manager.connect()
            cursor = self.db_manager.connection.cursor()
            cursor.execute(query)
            self.existing_urls = {row[0] for row in cursor.fetchall()}
            cursor.close()
            logging.info(f"Loaded {len(self.existing_urls)} existing job URLs.")
        except mysql.connector.Error as err:
            logging.error(f"Error loading existing URLs: {err}")

    def create_table(self):
        query = """
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
        """
        self.db_manager.execute(query)

    def fetch_job_page(self, page):
        for attempt in range(self.max_retries):
            try:
                logging.info(f"Fetching page {page}...")
                response = requests.get(f"{self.base_url}?page={page}", headers=self.headers)
                response.raise_for_status()
                return BeautifulSoup(response.text, 'html.parser')
            except requests.RequestException as e:
                logging.error(f"Error fetching page {page}: {e}")
                time.sleep(2)
        return None

    def extract_job_data(self, job_item):
        try:
            return {
                'job_group': '91,92',
                'badge': job_item.select_one('.badge')['src'] if job_item.select_one('.badge') else None,
                'company_name': job_item.select_one('.corp_name a')['title'] if job_item.select_one('.corp_name a') else None,
                'title': job_item.select_one('.job_tit a')['title'] if job_item.select_one('.job_tit a') else None,
                'deadline': job_item.select_one('.date')['title'] if job_item.select_one('.date') else None,
                'address_main': job_item.select_one('.work_place').text.strip() if job_item.select_one('.work_place') else None,
                'address_total': job_item.select_one('.work_place').text.strip() if job_item.select_one('.work_place') else None,
                'experience': job_item.select_one('.career').text.strip() if job_item.select_one('.career') else None,
                'education': job_item.select_one('.education').text.strip() if job_item.select_one('.education') else None,
                'employment_type': job_item.select_one('.employment_type').text.strip() if job_item.select_one('.employment_type') else None,
                'salary': job_item.select_one('.salary').text.strip() if job_item.select_one('.salary') else None,
                'tech_stack': ', '.join([tag.text.strip() for tag in job_item.select('.job_sector span')]) if job_item.select('.job_sector span') else None,
                'createdAt': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'crawledAt': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'url': 'https://www.saramin.co.kr' + job_item.select_one('.job_tit a')['href'] if job_item.select_one('.job_tit a') else None,
                'description': self.fetch_job_description('https://www.saramin.co.kr' + job_item.select_one('.job_tit a')['href']) if job_item.select_one('.job_tit a') else None
            }
        except Exception as e:
            logging.error(f"Error extracting job data: {e}")
            return None

    def fetch_job_description(self, url):
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            description = soup.select_one('.job_summary')
            return description.text.strip() if description else ''
        except Exception as e:
            logging.error(f"Error fetching job description: {e}")
            return ''

    def save_to_database(self, job_data):
        query = """
        INSERT INTO jobs (job_group, badge, company_name, title, deadline, address_main, address_total,
                          experience, education, employment_type, salary, tech_stack, createdAt, crawledAt, url, description)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        self.db_manager.execute(query, tuple(job_data.values()))

    def crawl(self, max_jobs=50):
        self.create_table()
        jobs = []
        page = 1

        while len(jobs) < max_jobs:
            soup = self.fetch_job_page(page)
            if not soup:
                break

            job_items = soup.select('.item_recruit')
            for job_item in job_items:
                if len(jobs) >= max_jobs:
                    break

                job_data = self.extract_job_data(job_item)
                if job_data and job_data['url'] not in self.existing_urls:
                    self.save_to_database(job_data)
                    self.existing_urls.add(job_data['url'])
                    jobs.append(job_data)
                    logging.info(f"Saved job: {job_data['title']}")

            page += 1
            time.sleep(1)

        # 크롤링 결과를 JSON 파일로 저장
        with open('jobs.json', 'w', encoding='utf-8') as f:
            json.dump(jobs, f, ensure_ascii=False, indent=4)    

        logging.info(f"Crawling completed. Total jobs crawled: {len(jobs)}")
        return jobs
