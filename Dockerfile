FROM python:3.10
##FastAPI 애플리케이션을 실행할 Python 런타임 환경

LABEL authors="USER"
##authors라는 레이블에 값을 USER로 설정

##ENTRYPOINT ["top", "-b"]

WORKDIR /fast_api_text_analyzer
##/app으로 설정합니다.모든 명령이 /app 디렉토리에서 실행

RUN pip install --upgrade pip
# pip 최신 버전으로 업데이트

COPY requirements.txt /fast_api_text_analyzer/requirements.txt
# requirements.txt 파일을 컨테이너 내로 복사

RUN pip install -r requirements.txt
# 패키지 설치

# 소스 코드 복사
COPY . .

EXPOSE 8000
##컨테이너가 8000번 포트를 외부에 노출

# 앱 실행
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
##ENTRYPOINT는 보통 메인 애플리케이션의 실행 명령으