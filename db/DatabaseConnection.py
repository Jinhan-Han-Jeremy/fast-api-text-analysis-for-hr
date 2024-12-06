import mysql.connector
from mysql.connector import Error
import os

class DatabaseConnection:
    def __init__(self):
        # 환경 변수 불러오기
        self.db_config = {
            "database": os.getenv("DB_NAME"),
            "user": os.getenv("DB_USER"),
            "password": os.getenv("DB_PASSWORD"),
            "host": os.getenv("DB_HOST")
        }
        # MySQL 연결 생성
        self.connection = self.create_connection()


    # MySQL 연결 설정
    def create_connection(self):
        try:
            print('dddasd')
            connection = mysql.connector.connect(
                host=self.db_config["host"],
                database=self.db_config["database"],
                user=self.db_config["user"],
                password=self.db_config["password"]
            )

            print('dddasd')
            if connection.is_connected():
                print("MySQL 데이터베이스에 성공적으로 연결되었습니다.")
            return connection
        except Error as e:
            print(f"Error: '{e}' 발생")
            return None

    # 테이블 생성 함수
    def create_tables(self, create_table_query):
        if self.connection:
            cursor = self.connection.cursor()
            cursor.execute(create_table_query)
            self.connection.commit()
            cursor.close()
            create_table = create_table_query.split()
            print(create_table[5])
            print(" 테이블이 성공적으로 생성되었습니다.")

    # 테이블 초기화 함수 (기존 데이터 삭제)
    def clear_table(self, table_name):
        if self.connection and self.check_table_exists(table_name):
            cursor = self.connection.cursor()
            cursor.execute(f"TRUNCATE TABLE {table_name};")  # TRUNCATE로 데이터 삭제 및 id 초기화
            self.connection.commit()
            cursor.close()
            print(f"{table_name} 테이블의 기존 데이터가 삭제되었습니다.")


    # 테이블 존재 여부 확인 함수
    def check_table_exists(self, table_name):
        if self.connection:
            cursor = self.connection.cursor()
            query = f"SHOW TABLES LIKE '{table_name}'"
            cursor.execute(query)
            result = cursor.fetchone()
            cursor.close()
            if result:
                print(f"테이블 '{table_name}'이(가) 존재합니다.")
                return True
            else:
                print(f"테이블 '{table_name}'이(가) 존재하지 않습니다.")
                return False