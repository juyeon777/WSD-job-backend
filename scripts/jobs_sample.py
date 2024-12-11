import pymysql
import csv
from datetime import datetime

def clean_data(value):
    return value.strip() if value else None

def parse_date(date_string, format):
    try:
        return datetime.strptime(date_string, format) if date_string else None
    except ValueError:
        return None

# MySQL 연결 정보
connection = pymysql.connect(
    host='localhost',
    user='root',
    password='juyeon777',
    database='job_portal',
    charset='utf8mb4'
)

try:
    with connection.cursor() as cursor:
        csv_file_path = 'C:/Users/juyeon/Downloads/random_50_jobs.csv'

        with open(csv_file_path, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            print(f"CSV 헤더: {reader.fieldnames}")

            insert_query = """
                INSERT INTO jobs (
                    job_group, badge, company_name, title, deadline, 
                    address_main, address_total, experience, education, 
                    employment_type, salary, tech_stack, createdAt, 
                    crawledAt, url, description
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """

            batch_size = 100
            values = []

            for row_number, row in enumerate(reader, start=1):
                job_group = clean_data(row.get('job_group'))
                badge = clean_data(row.get('badge'))
                company_name = clean_data(row.get('company_name'))
                title = clean_data(row.get('title'))
                deadline = parse_date(clean_data(row.get('deadline')), '%Y-%m-%d')
                address_main = clean_data(row.get('address_main'))
                address_total = clean_data(row.get('address_total'))
                experience = clean_data(row.get('experience'))
                education = clean_data(row.get('education'))
                employment_type = clean_data(row.get('employment_type'))
                salary = clean_data(row.get('salary'))
                tech_stack = clean_data(row.get('tech_stack'))
                createdAt = parse_date(clean_data(row.get('createdAt')), '%Y-%m-%d %H:%M:%S')
                crawledAt = parse_date(clean_data(row.get('crawledAt')), '%Y-%m-%d %H:%M:%S')
                url = clean_data(row.get('url'))
                description = clean_data(row.get('description'))

                values.append((
                    job_group, badge, company_name, title, deadline, address_main, 
                    address_total, experience, education, employment_type, salary, 
                    tech_stack, createdAt, crawledAt, url, description
                ))

                if len(values) >= batch_size:
                    try:
                        cursor.executemany(insert_query, values)
                        connection.commit()
                        print(f"{len(values)} 행 삽입 완료")
                        values = []
                    except Exception as e:
                        print(f"배치 삽입 실패: {e}")
                        connection.rollback()

            # 남은 데이터 처리
            if values:
                try:
                    cursor.executemany(insert_query, values)
                    connection.commit()
                    print(f"마지막 {len(values)} 행 삽입 완료")
                except Exception as e:
                    print(f"마지막 배치 삽입 실패: {e}")
                    connection.rollback()

        print("데이터 삽입 완료!")

except Exception as e:
    print(f"스크립트 실행 중 오류 발생: {e}")

finally:
    connection.close()
