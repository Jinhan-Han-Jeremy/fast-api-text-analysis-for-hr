## 실행 운용법 및 중요 사항항
- !! docker-compose 최초 실행시 2번 연속 docker-compose up --build 실행해야 온전히 데이터 삽입 가능
- !! 도커 운용시 alias 및 network 명칭 동일하게 설정
- !! DB 생성은 파이썬 fastAPI에서 담당하니 spring hibernate 설정시 ddl-auto: update
- !! fastAPI 필요 라이브러리는 requirements.txt에 보관---도커컴포즈가 자동 설치 운용 (pip install -r requirements.txt)
## 주요 기능
- **역할**: kotlin-hr-auto-assigner-time-forecast 어플리케이션을 연결하여 보조적 기능들을 사용
- https://github.com/Jinhan-Han-Jeremy/kotlin-hr-auto-assigner-time-forecast.git
- **데이터베이스 테이블 생성**: FastAPI 애플리케이션이 `java_hr_db` 데이터베이스에 연결하여 여러 테이블을 생성
- **CSV 데이터 삽입**: 데이터베이스 테이블에 CSV 데이터를 삽입하여 초기 데이터 구성을 완료
- **텍스트 분석 기능**: workstream 텍스트를 분석하고 핵심 정보를 추출하는 기능을 스프링부트 어플리케이션에 제공

## 데이터베이스 테이블 구조
### tasks 테이블
**컬럼**:
- `id` (INT, 자동 증가, 기본 키)
- `name` (VARCHAR, 최대 255자)
- `employee_role` (VARCHAR, 최대 255자)
- `difficulty` (INT)
- `requirements` (TEXT)

### tasks_history 테이블
컬럼:
- id (INT, 자동 증가, 기본 키)
- name (VARCHAR, 최대 255자)
- teammembers (VARCHAR, 최대 255자)
- available_jobs (VARCHAR, 최대 255자)
- spending_days (FLOAT)
- expected_days (FLOAT)
- state (VARCHAR, 최대 50자)
- requirements_satisfied (BOOLEAN)
- started_at (DATE)
- ended_at (DATE)

### team_member 테이블
컬럼:
- id (INT, 자동 증가, 기본 키)
- name (VARCHAR, 최대 255자)
- role (VARCHAR, 최대 255자)
- level (INT)
- state (BOOLEAN)
- performance_for_skills (JSON)
- achievements_score (FLOAT)

### workstream_info 테이블
컬럼:
- id (INT, 자동 증가, 기본 키)
- workstream (TEXT)
- available_jobs (VARCHAR, 최대 255자)
- FULLTEXT 인덱스 (workstream 및 available_jobs 컬럼)
