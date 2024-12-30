from fastapi import FastAPI, Depends, HTTPException, Request, Form, Response, Cookie, Body
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse         
from passlib.context import CryptContext
from jose import JWTError, jwt
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
from fastapi.templating import Jinja2Templates
from starlette.requests import Request
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.orm import sessionmaker, Session, relationship
from sqlalchemy.dialects.postgresql import ARRAY  # For PostgreSQL support
from typing import Optional
import json
import base64
import requests
from fastapi.middleware.cors import CORSMiddleware
from urllib.parse import urlencode
# .env 파일에서 환경 변수 로드하기
from dotenv import load_dotenv
import os
from fastapi.security import OAuth2PasswordBearer

# OAuth2PasswordBearer는 '/token' 경로를 기본값으로 사용
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")




# .env 파일을 로드합니다.
load_dotenv()

# 환경 변수 사용하기
ID = os.getenv('DB_USER')
PASS = os.getenv('DB_PASS')
HOST = os.getenv('DB_HOST')
PORT = os.getenv('DB_PORT')
DB_NAME = os.getenv('DB_NAME')

print(f"ID: {ID}, PASS: {PASS}, HOST: {HOST}, PORT: {PORT}, DB_NAME: {DB_NAME}")

# if ID:
DATABASE_URL = f"mysql+pymysql://{ID}:{PASS}@{HOST}:{PORT}/movie_fastapi"
print(f'DATABASE_URL : {DATABASE_URL}' )

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
    
    favorites = relationship("UserFav", back_populates="user")  # User와 UserFav 관계 설정
    
class UserFav(Base):
    __tablename__ = 'user_fav'
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'))  # ForeignKey and primary_key order corrected
    code = Column(String(255))  # Movie code added
    title = Column(String(255))
    director = Column(String(255))  # Array of strings for director
    actor = Column(String(255))  # Array of strings for actor
    genre = Column(String(255))  # Array of strings for genre
    nation = Column(String(255))  # Array of strings for nation

    user = relationship("User", back_populates="favorites")

# Pydantic schemas
class UserCreate(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None
    user_id: int | None = None  # 사용자 ID 추가

    
class MovieSaveRequest(BaseModel):
    code: str  # movieCd는 code로 받음
    title: str  # movieNm은 title로 받음
    director: str  # 감독 (쉼표로 구분된 문자열로 받음)
    actor: str  # 배우 (쉼표로 구분된 문자열로 받음)
    genre: str  # 장르 (쉼표로 구분된 문자열로 받음)
    nation: str  # 국가 (쉼표로 구분된 문자열로 받음)

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

def get_current_user(token: str= Depends(oauth2_scheme), db: Session = Depends(get_db)):
    print('get_current_user####################################################')
    print(token)
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        print(payload)
        username: str = payload.get("sub")
        user_id: int = payload.get("id")  # JWT에서 사용자 ID 추출
        if username is None or user_id is None:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
        token_data = TokenData(username=username, user_id=user_id)
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    except Exception as e:  # 모든 다른 예외를 처리
        print(f"예상치 못한 오류가 발생했습니다: {e}")
    
    user = get_user(db, username=token_data.username)
    if user is None or user.id != token_data.user_id:
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

    # db_user에서 id와 username을 포함하여 JWT 생성
    access_token = create_access_token(
        data={"sub": db_user.username, "id": db_user.id},  # username과 id를 포함
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)  # 토큰 만료 시간 설정
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






# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:8000", "http://localhost:8000"],  # 허용할 출처 목록 # 다른 출처에서 요청이 오면 차단된다 
    allow_credentials=True, # 쿠키나 인증 정보가 포함된 요청을 허용한다 
    allow_methods=["*"],  # 모든 HTTP 메서드 허용
    allow_headers=["*"],  # 모든 HTTP 헤더 허용
)

# 외부 API의 URL과 API 키
KOBIS_API_KEY = ""
KOBIS_BASE_URL = "http://www.kobis.or.kr/kobisopenapi/webservice/rest/movie/searchMovieList.json"
    
# DB 세션 생성 함수
def get_db():
    db = SessionLocal() # 데이터베이스 세션을 생성하는 객체 
    try:
        yield db # 의존성 주입 시스템을 활용하여 요청이 있을 때마다 db 세션을 전달 
    finally:
        db.close()
        
# 토큰을 디코딩하여 사용자 정보 추출
def get_user_from_token(access_token: Optional[str] = Cookie(None), db: Session = Depends(get_db)):
    if not access_token:
        raise HTTPException(status_code=401, detail="로그인 필요")
    
    try:
        # JWT 토큰을 디코딩하여 user_id를 추출
        payload = jwt.decode(access_token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("id")  # JWT 토큰에서 user_id 추출 (사용자가 로그인 시 이 정보를 포함시킴)

        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")

        # DB에서 해당 user_id를 가진 사용자 찾기
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=401, detail="User not found")

        return user
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


@app.get("/check-login")
async def check_login(
    access_token: Optional[str] = Cookie(None),
    db: Session = Depends(get_db)  # DB 세션 의존성 추가
):
    print(f"Received access_token: {access_token}")  # 디버깅 로그
    try:
        user = get_user_from_token(access_token, db)
        return {"isLoggedIn": True}
    except HTTPException:
        return {"isLoggedIn": False}
    
 

@app.post("/search-request")
async def search_movies(
    title: Optional[str] = Form(None),
    actor: Optional[str] = Form(None),
    director: Optional[str] = Form(None),
    nation: Optional[str] = Form(None),
    access_token: Optional[str] = Cookie(None),  # 쿠키에서 access_token을 받음
    db: Session = Depends(get_db)  # DB 세션 의존성 추가
):

    # 로그인 여부 확인 및 user 정보 가져오기
    user = get_user_from_token(access_token, db)  # access_token으로 사용자의 정보를 가져오는 함수
    if not user:
        raise HTTPException(status_code=401, detail="로그인이 필요합니다.")  # 로그인되지 않으면 401 에러

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

    try:
        # 외부 API 호출
        response = requests.get(url)
        response.raise_for_status()  # 응답이 정상적인지 확인 (5xx, 4xx 오류 발생 시 예외 처리)
        data = response.json()
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"API 요청 중 오류 발생: {str(e)}")  # API 요청 중 오류 발생 시 처리

    # 외부 API 응답에서 영화 목록 추출
    movie_list = data.get('movieListResult', {}).get('movieList', [])

    if not movie_list:
        return JSONResponse(status_code=200, content={"message": "영화가 없습니다."})

    return JSONResponse(status_code=200, content={"movie_list": movie_list})





# 모달창 열어서 영화 상세 정보 불러오기 
MOVIE_DETAIL_URL =  "http://www.kobis.or.kr/kobisopenapi/webservice/rest/movie/searchMovieInfo.json" 
    
@app.get("/details/{movieCd}")
def get_movie_details(movieCd: str):
    params = {
        "key": KOBIS_API_KEY,
        "movieCd": movieCd
    }
    
    # 요청할 URL을 출력
    request_url = f"{MOVIE_DETAIL_URL}?{urlencode(params)}"
    print(f"Request URL: {request_url}")  # 터미널에 출력
    
    response = requests.get(MOVIE_DETAIL_URL, params=params)
        
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Failed to fetch movie details")
    
    # API 응답 전체 데이터를 그대로 반환
    return response.json()


@app.post("/save/{movieCd}")
async def save_movie(
    movieCd: str,
    movie: MovieSaveRequest, 
    db: Session = Depends(get_db),
    # user: User = Depends(get_current_user),
    access_token: Optional[str] = Cookie(None),  # 쿠키에서 access_token을 받음
    ):
    try:
        user = get_user_from_token(access_token, db)
        print("##########################################################save movie")
        print("received data: ", movie.dict())
        
        # UserFav 객체 생성
        user_fav = UserFav(
            user_id=user.id,  # 사용자 ID (세션 또는 인증을 통해 가져와야 함)
            code=movie.code,  # 영화 코드
            title=movie.title,  # 영화 제목
            director=movie.director,  # 감독 (리스트로 저장)
            actor=movie.actor,  # 배우 (리스트로 저장)
            genre=movie.genre,  # 장르 (리스트로 저장)
            nation=movie.nation,  # 국가 (리스트로 저장)
        )
        print("##########################################################user_fav")
        db.add(user_fav)  # DB에 추가
        print("##########################################################1")
        db.commit()  # 커밋
        print("##########################################################22222")
        db.refresh(user_fav)  # 새로 추가된 데이터 반영
        print("##########################################################svt forever")
        
        
        return {"message": "영화 정보가 저장되었습니다.", "movie_code": movieCd}
    
    except Exception as e:
        db.rollback()  # 오류 발생 시 롤백
        raise HTTPException(status_code=500, detail=f"오류 발생: {str(e)}")



# class UserFav(Base):
#     __tablename__ = 'user_fav'
    
#     user_id = Column(Integer, ForeignKey('users.id'), primary_key=True)  # ForeignKey and primary_key order corrected
#     code = Column(Integer)  # Movie code added
#     title = Column(String(255))
#     director = Column(ARRAY(String))  # Array of strings for director
#     actor = Column(ARRAY(String))  # Array of strings for actor
#     genre = Column(ARRAY(String))  # Array of strings for genre
#     nation = Column(ARRAY(String))  # Array of strings for nation

#     user = relationship("User", back_populates="favorites")





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
