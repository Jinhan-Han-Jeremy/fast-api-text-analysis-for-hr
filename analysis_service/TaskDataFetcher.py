import pandas as pd
from fastapi import FastAPI
from db.DatabaseConnection import DatabaseConnection

# FastAPI 인스턴스 생성
app = FastAPI()

# Database 작업 클래스
class TaskDataFetcher:
    def __init__(self):
        self.connection = DatabaseConnection.create_connection()
        self.tasks_info = pd.DataFrame(columns=['name', 'difficulty', 'requirements'])


    def fetch_tasks_data(self):
        if self.connection is None:
            print("DB 연결에 실패했습니다.")
            return self.tasks_info

        try:
            cursor = self.connection.cursor()
            ## 핵심 쿼리에서 제거할 쿼리정보들 추출
            query_to_remove = "SELECT name FROM tasks_history"
            cursor.execute(query_to_remove)
            task_names_to_remove = cursor.fetchall()

            # 리스트 변환 (fetchall() 결과는 튜플 리스트이므로 변환 필요)
            task_names_to_remove_list = [name[0] for name in task_names_to_remove]

            # 기본 쿼리
            query = "SELECT name, difficulty, requirements FROM tasks"

            # task_names_to_remove_list가 비어있지 않으면 (제외할 이름이 있으면) 조건을 추가
            if task_names_to_remove_list:
                placeholders = ', '.join(['%s'] * len(task_names_to_remove_list))
                query += f" WHERE name NOT IN ({placeholders})"

            cursor.execute(query)
            rows = cursor.fetchall()

            # 데이터를 DataFrame에 추가
            for row in rows:
                self.tasks_info = self.tasks_info.append({
                    'name': row[0],
                    'difficulty': row[1],
                    'requirements': row[2]
                }, ignore_index=True)

        finally:
            if self.connection.is_connected():
                cursor.close()
                self.connection.close()
                print("MySQL 연결이 닫혔습니다.")

        return self.tasks_info