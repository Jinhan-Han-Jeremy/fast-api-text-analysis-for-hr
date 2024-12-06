import pandas as pd
import json

class DataInserter:
    def __init__(self, db_connection):
        self.connection = db_connection.connection

    # task 테이블에 데이터를 삽입하는 함수
    def insert_task_csv_to_mysql(self, csv_file):
        if self.connection:
            data = pd.read_csv(csv_file)
            data = data.where(pd.notnull(data), None)
            insert_query = """
            INSERT INTO tasks (name, employees, difficulty, requirements)
            VALUES (%s, %s, %s, %s)
            """
            cursor = self.connection.cursor()
            for _, row in data.iterrows():
                cursor.execute(insert_query, (
                    row['name'],
                    row['employees'],
                    row['difficulty'],
                    row['requirements']
                ))
            self.connection.commit()
            cursor.close()
            print("task 테이블에 CSV 데이터가 성공적으로 삽입되었습니다.")

    # tasks_history 테이블에 데이터를 삽입하는 함수
    def insert_tasks_history_csv_to_mysql(self, csv_file):
        if self.connection:
            data = pd.read_csv(csv_file)
            data = data.where(pd.notnull(data), None)

            # # 시간 변환 (잘못된 값은 NaT로 처리)
            # data['started_at'] = pd.to_datetime(data['started_at'], errors='coerce')
            # data['ended_at'] = pd.to_datetime(data['ended_at'], errors='coerce')

            insert_query = """
            INSERT INTO tasks_history (name, teammembers, available_jobs, spending_days, state, requirements_satisfied, started_at, ended_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor = self.connection.cursor()
            for _, row in data.iterrows():
                cursor.execute(insert_query, (
                    row['name'],
                    row['teammembers'],
                    row['available_jobs'],
                    row['spending_days'] if pd.notnull(row['spending_days']) else None,
                    row['state'],
                    row['requirements_satisfied'],
                    row['started_at'],
                    row['ended_at']
                ))
            self.connection.commit()
            cursor.close()
            print("tasks_history 테이블에 CSV 데이터가 성공적으로 삽입되었습니다.")

    # team_member 테이블에 데이터를 삽입하는 함수
    def insert_member_csv_to_mysql(self, csv_file):
        if self.connection:
            data = pd.read_csv(csv_file, encoding='utf-8')
            data = data.where(pd.notnull(data), None)
            insert_query = """
            INSERT INTO team_member (name, role, level, state, performance_for_skills, achievements_score)
            VALUES (%s, %s, %s, %s, %s, %s)
            """
            cursor = self.connection.cursor()

            for _, row in data.iterrows():
                skills_performance = None
                ##json 형태로 데이터 분할 및 관리
                if row['performance_for_skills']:
                    try:
                        skills_performance = json.loads(row['performance_for_skills'])
                        skills_performance = json.dumps(skills_performance, ensure_ascii=False)
                    except json.JSONDecodeError as e:
                        print(f"JSONDecodeError: {e} - Invalid JSON data: {row['performance_for_skills']}")
                        continue

                cursor.execute(insert_query, (
                    row['name'],
                    row['role'],
                    row['level'],
                    row['state'],
                    skills_performance,
                    row['achievements_score']
                ))

            self.connection.commit()
            cursor.close()
            print("team_member 테이블에 CSV 데이터가 성공적으로 삽입되었습니다.")