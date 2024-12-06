from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from analysis_service.TaskDataFetcher import TaskDataFetcher
from analysis_service.WorkstreamAnalyzer import WorkstreamAnalyzer
from db.DatabaseConnection import DatabaseConnection
from db.DataInserter import DataInserter
from contextlib import asynccontextmanager

import uvicorn
import os
from fastapi import FastAPI
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))

# Lifespan 이벤트 핸들러 yield를 활용해 iterator화를 시켜실행
@asynccontextmanager
async def lifespan(app: FastAPI):

    project_root = os.getcwd()  # 현재 작업 디렉토리
    # CSV 파일 경로 설정
    TASK_CSV_FILE = os.path.join(project_root, 'resources', 'assigned_tasks.csv')
    TASK_HISTORY_CSV_FILE = os.path.join(project_root, 'resources', 'tasks_history.csv')
    TEAM_MEMBER_CSV_FILE = os.path.join(project_root, 'resources', 'team_member.csv')

    db_connection = None

    try:
        # 애플리케이션 시작 시 실행할 코드
        print("Application startup")

        # 1. 데이터베이스 연결 설정
        db_connection = DatabaseConnection()

        if db_connection.connection is None:
            raise RuntimeError("데이터베이스 연결에 실패했습니다.")

        isExistingTasks = db_connection.check_table_exists('tasks')
        isExistingTasks_history = db_connection.check_table_exists('tasks_history')
        isExistingTeam_member = db_connection.check_table_exists('team_member')

        ##db가 구성 되있지 않다면 자동 실행
        addable = True
        if ((isExistingTasks_history and isExistingTeam_member and isExistingTasks) or addable):
            # 테이블 초기화 (기존 데이터 삭제)
            db_connection.clear_table('tasks')  # 수정: connection 객체를 제거
            db_connection.clear_table('tasks_history')  # 수정: connection 객체를 제거
            db_connection.clear_table('team_member')  # 수정: connection 객체를 제거
            db_connection.clear_table('workstream_info')  # 수정: connection 객체를 제거

            # 데이터 삽입 클래스 생성
            data_inserter = DataInserter(db_connection)

            # 테이블 생성 및 데이터 삽입
            task_table_query = """
            CREATE TABLE IF NOT EXISTS tasks (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255),
                employees VARCHAR(255),
                difficulty INT,
                requirements TEXT
            );
            """

            task_history_table_query = """
            CREATE TABLE IF NOT EXISTS tasks_history (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255),
                teammembers VARCHAR(255),
                available_jobs VARCHAR(255),
                spending_days INT,
                state VARCHAR(50),
                requirements_satisfied BOOLEAN,
                started_at TIMESTAMP NULL DEFAULT NULL,
                ended_at TIMESTAMP NULL DEFAULT NULL
            );
            """

            team_member_table_query = """
            CREATE TABLE IF NOT EXISTS team_member (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255),
                role VARCHAR(255),
                level INT,
                state BOOLEAN,
                performance_for_skills JSON,
                achievements_score float
            );
            """

            work_stream_table_query = """
            CREATE TABLE IF NOT EXISTS workstream_info (
                id INT AUTO_INCREMENT PRIMARY KEY,
                workstream TEXT,
                available_jobs VARCHAR(255),
                FULLTEXT (workstream, available_jobs)  -- Full-Text 인덱스 생성
            );
            """

            # 테이블 생성
            db_connection.create_tables(task_table_query)
            db_connection.create_tables(task_history_table_query)
            db_connection.create_tables(team_member_table_query)
            db_connection.create_tables(work_stream_table_query)

            # CSV 데이터를 데이터베이스에 삽입
            data_inserter.insert_task_csv_to_mysql(TASK_CSV_FILE)
            data_inserter.insert_tasks_history_csv_to_mysql(TASK_HISTORY_CSV_FILE)
            data_inserter.insert_member_csv_to_mysql(TEAM_MEMBER_CSV_FILE)

        yield  # 애플리케이션의 정상적인 lifespan 이벤트 처리를 위해 필요

    except Exception as e:
        print(f"Error during startup: {str(e)}")

    finally:
        if db_connection:
            db_connection.close()  # 데이터베이스 연결 종료
        print("Application shutdown")



def create_app() -> FastAPI:

    # FastAPI 인스턴스 생성
    app = FastAPI(lifespan=lifespan)
    return app


app = create_app()

# 기본 엔드포인트
@app.get("/")
async def root():
    test_env = os.environ["TEST_ENV"]
    return {"message": "FastAPI 서버가 실행 중입니다." + " testing name :" + test_env}


# 요청 데이터 구조 정의 (Pydantic 모델)
class WorkstreamInput(BaseModel):
    input_text: str


# TaskDataFetcher, WorkstreamAnalyzer 클래스를 사용하여 데이터 처리
@app.post("/analyze_workstream")
async def analyze_workstream(workstream_input: WorkstreamInput):
    """작업과 관련된 텍스트 분석 엔드포인트"""
    try:
        # 1. TaskDataFetcher 인스턴스 생성 및 데이터 가져오기
        task_fetcher = TaskDataFetcher()
        tasks_info = task_fetcher.fetch_tasks_data()

        if tasks_info.empty:
            raise HTTPException(status_code=404, detail="Tasks not found")

        # 2. WorkstreamAnalyzer 인스턴스를 통해 분석
        analyzer = WorkstreamAnalyzer(tasks_info)
        analyzed_tasks = analyzer.analyzed_texts(workstream_input.input_text)

        return {"analyzed_tasks": analyzed_tasks.to_dict(orient='records')}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0")
