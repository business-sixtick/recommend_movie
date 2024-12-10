from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

# FastAPI 애플리케이션 인스턴스 생성
app = FastAPI()

# 기본 경로 "/"에 대한 GET 요청 처리
# @app.get("/")
# async def read_root():
#     return {"message": "Hello, World!"}

# "static" 디렉토리를 정적 파일 제공 경로로 설정
app.mount("/", StaticFiles(directory="static", html=True), name="static")

# 경로 "/items/{item_id}"에 대한 GET 요청 처리
@app.get("/items/{item_id}")
async def read_item(item_id: int, q: str = None):
    return {"item_id": item_id, "q": q}
