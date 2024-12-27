from fastapi import FastAPI, Depends, HTTPException, Request, Form, Response, Query, Cookie
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse, FileResponse, JSONResponse         
from passlib.context import CryptContext
from jose import JWTError, jwt
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
from fastapi.templating import Jinja2Templates
from starlette.requests import Request
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from typing import Optional
import json
import base64
import requests

# .env 파일에서 환경 변수 로드하기
from dotenv import load_dotenv
import os




# .env 파일을 로드합니다.
load_dotenv()

# 환경 변수 사용하기
ID = os.getenv('DB_USER')
PASS = os.getenv('DB_PASS')
HOST = os.getenv('DB_HOST')
PORT = os.getenv('DB_PORT')
DB_NAME = os.getenv('DB_NAME')

print(f"ID: {ID}, PASS: {PASS}, HOST: {HOST}, PORT: {PORT}, DB_NAME: {DB_NAME}")

# Database configuration
# DATABASE_URL = "mysql+pymysql://username:password@localhost/db_name"
# DATABASE_URL = "mysql+pymysql://ahncho:dkswh18@192.168.0.26:3306/movie_fastapi"
# DATABASE_URL = "mysql+pymysql://root:root@127.0.0.1:3306/movie"
# if ID:
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



# 정적 파일 디렉토리 설정 (HTML, CSS, JS, 이미지 등)
app.mount("/static", StaticFiles(directory="static"), name="static")

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
        data={"sub": db_user.username}, # sub는 jwt의 표준 필드로 subject
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES) # 토큰의 만료 시간 설정 
    )

    header, payload, signature = decode_jwt(access_token) # jwt 디코딩 
    # 출력
    print()
    print("Header:", json.dumps(header, indent=4))
    print("Payload:", json.dumps(payload, indent=4))
    print("Signature:", signature)
    print()
    
    return JSONResponse( # json 형식의 응답을 생성하는 객체 
        content={
            "status": "success",
            "redirect_url": "/list", # 로그인 성공 후 리디렉션할 url 
            "access_token": access_token
        },
        headers={"Set-Cookie": f"access_token={access_token}; Path=/; HttpOnly; Max-Age={ACCESS_TOKEN_EXPIRE_MINUTES * 60}"}
        # path를 /로 설정해서 사이트 내 모든 경로에서 유효하다 
        # httponly 설정을 통해 자바스크립트에서 접근할 수 없도록 해서 보안을 강화한다 
    )




# 로그아웃 처리
@app.get("/logout")
async def logout(request: Request, response: Response):
    # access_token 쿠키를 삭제 (로그아웃)
    response = JSONResponse(content={"status": "success", "redirect_url": "/list"})
    response.delete_cookie(key="access_token")  # 쿠키 삭제
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




@app.get("/")
async def main_page():
    print(f'main_page {datetime.now()}')
    # 단순히 static 디렉토리 안에 있는 index.html을 반환
    return FileResponse("static/index.html")






# 외부 API의 URL과 API 키
KOBIS_API_KEY = ""
KOBIS_BASE_URL = "http://www.kobis.or.kr/kobisopenapi/webservice/rest/movie/searchMovieList.json"

# 쿠키에서 access_token을 읽어 로그인 여부 판단
def is_user_logged_in(access_token: Optional[str] = Cookie(None)) -> bool:
    # access_token이 있으면 로그인한 것으로 간주 (여기서 실제 검증 로직 추가 가능)
    return bool(access_token)
# bool()은 Python의 내장 함수로, 주어진 값을 불리언 값(True 또는 False)으로 변환하는 역할을 합니다.

@app.post("/search-request")
async def search_movies(
    title: Optional[str] = Form(None),
    actor: Optional[str] = Form(None),
    director: Optional[str] = Form(None),
    nation: Optional[str] = Form(None),
    access_token: Optional[str] = Cookie(None)  # 쿠키에서 access_token을 받음
): 
    # Optional을 사용하는 이유는 해당 파라미터들이 요청 시에 반드시 존재하지 않아도 되기 때문입니다.
    # 즉, 클라이언트가 title, actor, director, nation 중 일부 또는 전부를 제공하지 않을 수 있다는 점을 반영하는 것입니다.
    
        # 로그인 여부 확인
    if not is_user_logged_in(access_token):
        return JSONResponse(status_code=401, content={"message": "로그인 필요"})
    # 401 Unauthorized 상태 코드는 HTTP 프로토콜에서 "인증되지 않음"
    
    
    
    # 외부 API 요청 파라미터 구성
    external_api_params = {
        "key": KOBIS_API_KEY,
    }

    if title:
        external_api_params["movieNm"] = title
    if actor:
        external_api_params["peopleNm"] = actor
    if director:
        external_api_params["directorNm"] = director
    if nation:
        external_api_params["repNationCd"] = nation

    # 외부 API 요청 URL 구성
    url = f"{KOBIS_BASE_URL}?{requests.compat.urlencode(external_api_params)}"
    print(f"Requesting URL: {url}")

    # 외부 API 호출
    response = requests.get(url)
    data = response.json()

    # 외부 API 응답에서 영화 목록 추출 후 반환
    movie_list = data.get('movieListResult', {}).get('movieList', [])
    
    # 영화 목록 반환
    return JSONResponse(content=movie_list)

@app.get("/check-login")
async def check_login(access_token: Optional[str] = Cookie(None)):
    if is_user_logged_in(access_token):
        return {"isLoggedIn": True}
    return {"isLoggedIn": False}





class UserFav(Base):
    __tablename__ = 'user_fav'

    id = Column(Integer, primary_key=True, index=True)
    movie_title = Column(String, index=True) # 검색 성능 향상을 위해서 
    director = Column(String)
    actor = Column(String)
    nation = Column(Integer)

    user_id = Column(Integer, ForeignKey('users.id'))  # user 테이블과 외래 키 관계 설정

    user = relationship("User", back_populates="favorites")  # User 모델과 연결




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




# # 현재 로그인한 사용자의 정보를 가져오는 api
# @app.get("/users/me", response_model=dict)
# def read_users_me(current_user: User = Depends(get_current_user)):
#     return {"username": current_user.username}
