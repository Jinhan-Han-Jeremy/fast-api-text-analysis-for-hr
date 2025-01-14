import pandas as pd
from fastapi import FastAPI
from db.DatabaseConnection import DatabaseConnection

# FastAPI 인스턴스 생성
app = FastAPI()

# Database 작업 클래스
# Database 작업 클래스
class TaskDataFetcher:
    def __init__(self, connection):

        self.connection = connection  # 기존 연결을 사용
        self.tasks_info = pd.DataFrame(columns=['name', 'difficulty', 'requirements'])
        print("TaskDataFetcher initialized with existing connection")

    def fetch_tasks_data(self):
        if self.connection is None or not self.connection.is_connected():
            print("DB 연결에 실패했습니다.")
            return self.tasks_info

        try:
            cursor = self.connection.cursor()
            
            # 제거할 태스크 이름 가져오기
            query_to_remove = "SELECT name FROM tasks_history"
            cursor.execute(query_to_remove)
            task_names_to_remove = [row[0] for row in cursor.fetchall()]  # 튜플을 리스트로 변환

            # 기본 태스크 쿼리
            query = "SELECT name, difficulty, requirements FROM tasks"
            if task_names_to_remove:
                placeholders = ', '.join(['%s'] * len(task_names_to_remove))
                query += f" WHERE name NOT IN ({placeholders})"
            
            cursor.execute(query, task_names_to_remove)
            rows = cursor.fetchall()

            # 데이터를 리스트로 저장한 뒤 DataFrame 변환
            task_data = [{'name': row[0], 'difficulty': row[1], 'requirements': row[2]} for row in rows]
            self.tasks_info = pd.DataFrame(task_data)

        except Exception as e:
            print(f"데이터 가져오는 중 오류 발생: {e}")

        finally:
            cursor.close()  # 연결 닫지 않음, 커서만 닫음
            print("DB 커서가 닫혔습니다.")

        return self.tasks_info