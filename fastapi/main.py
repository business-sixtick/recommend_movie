from fastapi import FastAPI, Depends, HTTPException, Request, Form, Cookie, Query
from fastapi.responses import RedirectResponse, JSONResponse
from passlib.context import CryptContext
from jose import JWTError, jwt
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from starlette.requests import Request
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from typing import Optional, Dict
import json
import base64
import httpx
import requests
from bs4 import BeautifulSoup

# .env 파일에서 환경 변수 로드하기
from dotenv import load_dotenv
import os

# .env 파일을 로드합니다.
load_dotenv()

# 환경 변수 사용하기
ID = os.getenv('ID')
PASS = os.getenv('PASS')
HOST = os.getenv('HOST')
PORT = os.getenv('PORT')

# Database configuration
# DATABASE_URL = "mysql+pymysql://username:password@localhost/db_name"
DATABASE_URL = "mysql+pymysql://ahncho:dkswh18@192.168.0.26:3306/movie_fastapi"
if ID:
    DATABASE_URL = f"mysql+pymysql://{ID}:{PASS}@{HOST}:{PORT}/movie_fastapi"
print(f'DATABASE_URL : {DATABASE_URL}' )
# 여기서 붙는 pymysql은 데이터베이스 드라이버: 이건 주로 간단한 개발 환경에 사용한다
# 공식 드라이버는 mysql-connector

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# JWT configuration
SECRET_KEY = "secretKey"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# Database model
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    # 자동 증가 방식식
    username = Column(String(50), unique=True, index=True, nullable=False)
    hashed_password = Column(String(100), nullable=False)

# Pydantic schemas
class UserCreate(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None

# 테이블 생성
Base.metadata.create_all(bind=engine)

# FastAPI application
app = FastAPI()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_user(db, username: str):
    return db.query(User).filter(User.username == username).first()

def authenticate_user(db, username: str, password: str):
    user = get_user(db, username)
    if not user or not verify_password(password, user.hashed_password):
        return False
    return user

def get_current_user(token: str, db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
        token_data = TokenData(username=username)
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    user = get_user(db, username=token_data.username)
    if user is None:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    return user





# 템플릿 디렉토리 설정
templates = Jinja2Templates(directory="templates")




# # 회원 가입 페이지 제공
# @app.get("/register", response_class=HTMLResponse)
# def register_page(request: Request):
#     return templates.TemplateResponse("register.html", {"request": request})

# 회원 가입을 처리하는 api
@app.post("/register", response_model=dict)
def register(username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    
    # 이미 등록된 사용자인지 확인 
    db_user = get_user(db, username=username)
    if db_user: 
        raise HTTPException(status_code=400, detail="Username already registered")
    
    # 비밀번호를 암호화, 즉 해싱한다 
    hashed_password = get_password_hash(password)
    
    # 새로운 사용자 추가 
    new_user = User(username=username, hashed_password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # 모달창으로 회원가입을 처리하므로 리다이렉트 경로는 없앤다 
    # return RedirectResponse(url="/login", status_code=303)

    # 회원 가입 후 리다이렉트 코드 제거, 그 대신 단순히 응답을 반환
    return {"message": "User successfully registered"}





def decode_jwt(token: str):
    # JWT 토큰을 '.' 기준으로 분리
    header_b64, payload_b64, signature_b64 = token.split(".")
    
    # Base64 URL 디코딩 (JWT는 URL-safe Base64로 인코딩됨)
    header_json = base64.urlsafe_b64decode(header_b64 + "==").decode('utf-8')
    payload_json = base64.urlsafe_b64decode(payload_b64 + "==").decode('utf-8')
    
    # 디코딩된 헤더와 페이로드를 JSON 객체로 변환
    header = json.loads(header_json)
    payload = json.loads(payload_json)
    
    return header, payload, signature_b64

# # 로그인 페이지 제공 
# @app.get("/login")
# async def get_login(request: Request):
#     return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login")
async def login(username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    db_user = authenticate_user(db, username, password)
    if not db_user:
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    
    print()
    # db_user를 JSON 형식으로 출력
    print("db_user:", json.dumps(db_user.__dict__, default=str))  # __dict__로 속성 가져오기
    print()

    # 토큰 생성
    access_token = create_access_token(
        data={"sub": db_user.username}, expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    header, payload, signature = decode_jwt(access_token)
    # 출력
    print()
    print("Header:", json.dumps(header, indent=4))
    print("Payload:", json.dumps(payload, indent=4))
    print("Signature:", signature)
    print()
    
    # 로그인 성공 시 /list로 리다이렉트 (username을 동적으로 포함)
    response = RedirectResponse(url="/list", status_code=303)
    # 로그인 성공 후 사용자가 이동할 경로, 303 see other는 클라이언트가 서버에서 제공한 url로 이동하도록 지시하는 역할 
    response.set_cookie(key="access_token", value=access_token, httponly=True) # 보안 강화용 
    return response



# # 현재 로그인한 사용자의 정보를 가져오는 api
# @app.get("/users/me", response_model=dict)
# def read_users_me(current_user: User = Depends(get_current_user)):
#     return {"username": current_user.username}





@app.get("/logout")
async def logout(request: Request):
    response = templates.TemplateResponse("list.html", {"request":request})
    response.delete_cookie(key="access_token")
    return response

# JWT 디코딩 함수
def decode_access_token(access_token: str) -> Optional[str]:
    try:
        payload = jwt.decode(access_token, key=SECRET_KEY, algorithms=ALGORITHM)
        username = payload.get("sub")  # "sub" 필드에 username이 들어있다고 가정
        return username
    except JWTError:
        return None  # 토큰이 잘못되었거나 만료된 경우
    
# SECRET_KEY = "secretKey"
# ALGORITHM = "HS256"



@app.get("/list")
async def list_page(request: Request):
    # 쿠키에서 access_token을 확인
    access_token = request.cookies.get("access_token")
    if access_token:
        # 토큰이 존재하면 디코딩하여 username을 얻을 수 있음
        username = decode_access_token(access_token)
    else:
        username = None  # 토큰이 없으면 username은 None

    return templates.TemplateResponse("list.html", {"request": request, "username": username})




# # 외부 API 요청을 처리하는 엔드포인트
# @app.get("/search")
# async def search(query: str):
#     # 외부 API 요청 URL (예시)
#     external_url = f"http://sixtick.duckdns.org:19821/llm?role=사용자가 질문한 내용과 관련된 영화 제목을 콤마로 구분해서 제목만 보여줘&query={query}"

#     # httpx를 사용하여 외부 API로 요청
#     async with httpx.AsyncClient() as client:
#         try:
#             response = await client.get(external_url)
#             return JSONResponse(content={"result": response.text})  # 결과를 클라이언트에 반환
#         except httpx.HTTPStatusError as http_error:
#             return JSONResponse(content={"error": f"HTTP Error: {http_error}"}, status_code=400)
#         except httpx.RequestError as request_error:
#             return JSONResponse(content={"error": f"Request Error: {request_error}"}, status_code=400)
        