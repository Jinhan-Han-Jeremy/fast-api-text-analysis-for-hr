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
            INSERT INTO tasks (name, employee_role, difficulty, requirements)
            VALUES (%s, %s, %s, %s)
            """
            cursor = self.connection.cursor()
            for _, row in data.iterrows():
                cursor.execute(insert_query, (
                    row['name'],
                    row['employee_role'],
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

        #날짜값처리 위한 함수
        def process_date(value):
            """
            날짜 값을 처리하여 유효한 날짜만 반환.
            NULL 또는 변환 실패 시 None 반환.
            """
            if pd.isnull(value) or value in [None, "", "NULL"]:
                return None
            try:
                # 날짜만 추출하여 반환
                return pd.to_datetime(value, errors='coerce').date()
            except Exception:
                return None

        # started_at과 ended_at 컬럼에서 날짜만 추출
        if 'started_at' in data.columns:
            data['started_at'] = data['started_at'].apply(process_date)
        if 'ended_at' in data.columns:
            data['ended_at'] = data['ended_at'].apply(process_date)

        # SQL INSERT 쿼리
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
                row['started_at'],  # 날짜만 포함된 값
                row['ended_at']     # 날짜만 포함된 값
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