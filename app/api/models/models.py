import mysql.connector
from mysql.connector import Error, pooling
import os
from dotenv import load_dotenv

load_dotenv()

# 환경 변수 검증 함수
def validate_env_vars():
    required_vars = ["DB_HOST", "DB_USER", "DB_PASSWORD", "DB_NAME"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]

    if missing_vars:
        raise EnvironmentError(f"Missing required environment variables: {', '.join(missing_vars)}")

# 데이터베이스 연결 함수
def get_db_connection():
    try:
        # 환경 변수 검증
        validate_env_vars()

        # 데이터베이스 연결
        connection = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME"),
        )
        if connection.is_connected():
            return connection

    except Error as e:
        print(f"Error connecting to MySQL database: {e}")
        raise

# Connection Pool (옵션)
connection_pool = pooling.MySQLConnectionPool(
    pool_name="mypool",
    pool_size=5,  # 최대 연결 수
    host=os.getenv("DB_HOST"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    database=os.getenv("DB_NAME"),
)

# Connection Pool을 이용한 연결 함수
def get_pooled_connection():
    try:
        return connection_pool.get_connection()
    except Error as e:
        print(f"Error getting connection from pool: {e}")
        raise
