## 주요 기능
- **역할**: java hr auto assign 어플리케이션을 연결하여 보조적 기능들을 사용
- **데이터베이스 테이블 생성**: FastAPI 애플리케이션이 `java_hr_db` 데이터베이스에 연결하여 여러 테이블을 생성
- **CSV 데이터 삽입**: 데이터베이스 테이블에 CSV 데이터를 삽입하여 초기 데이터 구성을 완료
- **텍스트 분석 기능**: workstream 텍스트를 분석하고 핵심 정보를 추출하는 기능을 스프링부트 어플리케이션에 제공

## 데이터베이스 테이블 구조
### tasks 테이블
**컬럼**:
- `id` (INT, 자동 증가, 기본 키)
- `name` (VARCHAR, 최대 255자)
- `employees` (VARCHAR, 최대 255자)
- `difficulty` (INT)
- `requirements` (TEXT)

### tasks_history 테이블
컬럼:
- id (INT, 자동 증가, 기본 키)
- name (VARCHAR, 최대 255자)
- teammembers (VARCHAR, 최대 255자)
- available_jobs (VARCHAR, 최대 255자)
- spending_days (INT)
- state (VARCHAR, 최대 50자)
- requirements_satisfied (BOOLEAN)

### team_member 테이블
컬럼:
- id (INT, 자동 증가, 기본 키)
- name (VARCHAR, 최대 255자)
- role (VARCHAR, 최대 255자)
- level (INT)
- state (BOOLEAN)
- performance_for_skills (JSON)

### workstream_info 테이블
컬럼:
- id (INT, 자동 증가, 기본 키)
- workstream (TEXT)
- available_jobs (VARCHAR, 최대 255자)
- FULLTEXT 인덱스 (workstream 및 available_jobs 컬럼)
