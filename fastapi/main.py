from fastapi import FastAPI, Depends, HTTPException, Request, Form, Response, Cookie, Body, Query, BackgroundTasks
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
import httpx
from urllib.parse import quote
import re
from typing import List
# from fastapi.security import OAuth2PasswordBearer

# # OAuth2PasswordBearer를 사용하여 토큰을 받아오는 방식
# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")




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
ACCESS_TOKEN_EXPIRE_MINUTES = 300

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
    username = Column(String(50), unique=True, index=True, nullable=False)
    hashed_password = Column(String(100), nullable=False)
    
    favorites = relationship("UserFav", back_populates="user")  # User와 UserFav 관계 설정
    
class UserFav(Base):
    __tablename__ = 'user_fav'
    
    # primary key는 고유성과 null이 될 수 없다는 조건을 가진다
    # 그렇기에 중복된 값을 가질 수 있는 user id는 primary key가 될 수 없다 
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'))  # ForeignKey and primary_key order corrected
    code = Column(String(255))  # Movie code added
    title = Column(String(255))
    director = Column(String(255))  # Array of strings for director
    actor = Column(String(500))  # Array of strings for actor
    genre = Column(String(255))  # Array of strings for genre
    nation = Column(String(255))  # Array of strings for nation

    user = relationship("User", back_populates="favorites")

class RecFav(Base):
    __tablename__ = 'rec_fav'
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'))  # ForeignKey and primary_key order corrected
    movie_code = Column(String(255))

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

def get_current_user(token: str, db: Session = Depends(get_db)):
    print('get_current_user')
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
    except Exception as e:
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







# 메인 페이지 설정 
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
KOBIS_API_KEY = "20ddcd10640eb87f69ef2fed167ef9ca"
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
    # raise 사용 시 클라이언트는 500 상태 코드와 함께 오류 메세지를 받는다 


@app.post("/check-login")
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
    llm: Optional[str] = Form(None),
    access_token: Optional[str] = Cookie(None),  # 쿠키에서 access_token을 받음
    db: Session = Depends(get_db)  # DB 세션 의존성 추가
):

    # 로그인 여부 확인 및 user 정보 가져오기
    user = get_user_from_token(access_token, db)  # access_token으로 사용자의 정보를 가져오는 함수
    if not user:
        raise HTTPException(status_code=401, detail="로그인이 필요합니다.")  # 로그인되지 않으면 401 에러

    # 배우 검색 시, 영화 검색을 하지 않고 actor 전용 API로만 처리
    if actor:
        actor_url = f"http://www.kobis.or.kr/kobisopenapi/webservice/rest/people/searchPeopleList.json?key={KOBIS_API_KEY}&peopleNm={actor}"
        print(f"Requesting actor-specific URL: {actor_url}")
        try:
            response = requests.get(actor_url)  # actor-specific URL 요청
            response.raise_for_status()  # 응답 오류 체크
            actor_data = response.json()  # Actor에 대한 결과를 반환
            
            actor_list = actor_data.get('peopleListResult', {}).get('peopleList', [])
            
            return JSONResponse(status_code=200, content={"actor_list": actor_list})  # 배우 데이터 반환
        except requests.exceptions.RequestException as e:
            raise HTTPException(status_code=500, detail=f"배우 검색 실패: {e}")  # 배우 검색 실패 시 처리
    
    if llm:
        role = (
            "사용자가 입력한 문장을 보고 해당하는 자리에 answer를 채워 {'제목': answer, '감독': answer, '배우': answer, '국가': answer} 형식으로 정리해서 보여줘. \
                answer에 마땅한 답이 없으면 null로 표시해줘.\
                꼭 json 형식을 맞춰줘.\
                문장에서 나온 단어만으로 answer를 채워.\
                중괄호 밖에는 어떠한 단어도 작성하지마."
        )
        
        llm_url = f'https://sixtick.duckdns.org/llm'
        # http의 보안 버전이 https # 서버가 https만 지원하면 http를 잘못된 요청으로 간주해 400 에러 
        params = {
            'role': role,
            'query': llm
        }
        
        print(f"Requesting URL: {llm_url}?{requests.compat.urlencode(params)}")
        
        # httpx를 사용하여 외부 API로 요청
        async with httpx.AsyncClient() as client: # httpx를 사용하여 비동기 HTTP 클라이언트를 생성합니다.
            try:
                response = await client.get(llm_url, params=params)
                response.raise_for_status()  # HTTP 상태 확인
                print(response.text)

                # JSON 데이터 파싱
                response_data = response.json()  # 응답 텍스트를 JSON으로 변환
                print(response_data)
                llmAnswer = response_data.get('answer', "결과를 찾을 수 없습니다.")  # answer 키 추출
                print(llmAnswer)
                
                return JSONResponse(content={"llmAnswer": llmAnswer}, status_code=200)  # answer만 반환
            except httpx.HTTPStatusError as http_error:
                print(http_error)
                return JSONResponse(content={"error": f"HTTP Error: {http_error}"}, status_code=400)
            except httpx.RequestError as request_error:
                print(request_error)
                return JSONResponse(content={"error": f"Request Error: {request_error}"}, status_code=400)

    # 외부 API 요청 파라미터 구성 (배우가 아닐 경우에만 영화 검색)
    external_api_params = {
        "key": KOBIS_API_KEY,
        "itemPerPage": 100,
    }    

    if title:
        external_api_params["movieNm"] = title
    if director:
        external_api_params["directorNm"] = director
    if nation:
        external_api_params["repNationCd"] = nation

    # 외부 API 요청 URL 구성
    url = f"{KOBIS_BASE_URL}?{requests.compat.urlencode(external_api_params)}"
    print(f"Requesting movie URL: {url}")

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









ACTOR_DETAIL_URL = "http://www.kobis.or.kr/kobisopenapi/webservice/rest/people/searchPeopleInfo.json"

# 영화인 상세정보 모달창 
@app.get("/actorDetails/{peopleCd}")
def get_actor_details(peopleCd: str):
    params = {
        "key": KOBIS_API_KEY,
        "peopleCd": peopleCd
    }
    
    request_url = f"{ACTOR_DETAIL_URL}?{urlencode(params)}"
    print(f"Request URL: {request_url}")  # 터미널에 출력

    response = requests.get(ACTOR_DETAIL_URL, params=params)
        
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Failed to fetch actor details")
    
    # API 응답 전체 데이터를 그대로 반환
    return response.json()


MOVIE_DETAIL_URL =  "http://www.kobis.or.kr/kobisopenapi/webservice/rest/movie/searchMovieInfo.json" 
    
# 영화 상세정보 모달창 
@app.get("/movieDetails/{movieCd}")
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







# 백그라운드에서 실행할 함수
async def fetch_movie_recommendations(user_id: int, db: Session):

    # 사용자가 고른 영화 목록을 가져오기
    user_fav_movies = db.query(UserFav).filter(UserFav.user_id == user_id).order_by(UserFav.id.desc()).limit(20).all()
    
    movie_titles = [movie.title for movie in user_fav_movies]
    movie_codes = [movie.code for movie in user_fav_movies]
    print(movie_titles)        
    print(movie_codes)
    print()

    # 리스트에서 5개 무작위로 선택
    query = str(movie_titles)
    role = (
        "사용자가 입력한 리스트에서 연관성이 높은 제목 5개를 변경 없이 콤마로 구분해서 리스트 코드 형태로 보여줘. 여기서 1개의 기준은 따옴표 안에 있는 것이야. 꼭 응답 포멧을 ['제목','제목','제목','제목','제목'] 으로 해줘"
    )
    
    rec_url = f'https://sixtick.duckdns.org/llmpost'
    params = {
        'role': role,
        'query': query
    }

    print(f"Requesting URL: {rec_url}?{requests.compat.urlencode(params)}")
    print()

    # httpx를 사용하여 외부 API로 요청
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(rec_url, json=params)
            response.raise_for_status()  # HTTP 상태 확인
            print(response.text)
            print()

            # JSON 데이터 파싱
            response_data = response.json()
            print()

            rec_answer = response_data.get('answer', "결과를 찾을 수 없습니다.")
            print(f"rec_answer: {rec_answer}")
            print()

            # 리스트 부분만 추출 (정규표현식 사용)
            list_match = re.search(r"\[.*?\]", rec_answer)  # 대괄호 포함 문자열 찾기 
            if list_match:
                titles_to_list = eval(list_match.group())  # 문자열을 리스트로 변환
                print(f'titles_to_list: {titles_to_list}')
                print()

                # rec_urls = []  # 여러 개의 URL을 담을 리스트
                movie_code_list = []

                for title in titles_to_list:
                    print("-------------------------------")
                    if title in movie_titles:
                        index = movie_titles.index(title)  # 제목의 인덱스를 찾음
                        movie_code = movie_codes[index]  # 해당 제목에 맞는 movie_code를 가져옴
                        print(movie_code)
                        movie_code_list.append(movie_code)
                        
                try: 
                    rec_fav = RecFav(
                        user_id = user_id,
                        movie_code = str(movie_code_list)
                    )
                    db.add(rec_fav)  # DB에 추가
                    db.commit()
                    db.refresh(rec_fav)
                    print("=======================================complete")
                
                except Exception as e:
                    print(f"디비에 저장 안 됨: {e}")
                
    # class RecFav(Base):
    # __tablename__ = 'rec_fav'
    
    # id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    # user_id = Column(Integer, ForeignKey('users.id'))  # ForeignKey and primary_key order corrected
    # movie_code = Column(Integer, ForeignKey('user_fav.code'))

        except httpx.RequestError as exc:
            print(f"An error occurred: {exc}")



            
            
# # 백그라운드에서 실행할 함수
# async def fetch_movie_recommendations(user_id: int, db: Session):
#     # 사용자가 고른 영화 목록을 가져오기
#     user_fav_movies = db.query(UserFav).filter(UserFav.user_id == user_id).order_by(UserFav.id.desc()).limit(20).all()
    
#     movie_titles = [movie.title for movie in user_fav_movies]
#     movie_codes = [movie.code for movie in user_fav_movies]
#     print(movie_titles)        
#     print(movie_codes)
#     print()

#     # 리스트에서 5개 무작위로 선택
#     query = str(movie_titles)
#     role = (
#         "사용자가 입력한 리스트에서 연관성이 높은 제목 5개를 변경 없이 콤마로 구분해서 리스트 코드 형태로 보여줘. "
#         "여기서 1개의 기준은 따옴표 안에 있는 것이야. 꼭 응답 포멧을 ['제목','제목','제목','제목','제목'] 으로 해줘"
#     )
    
#     rec_url = f'https://sixtick.duckdns.org/llmpost'
#     params = {
#         'role': role,
#         'query': query
#     }

#     print(f"Requesting URL: {rec_url}?{requests.compat.urlencode(params)}")
#     print()

#     # httpx를 사용하여 외부 API로 요청
#     async with httpx.AsyncClient() as client:
#         try:
#             response = await client.post(rec_url, json=params)
#             response.raise_for_status()  # HTTP 상태 확인
#             print(response.text)
#             print()

#             # JSON 데이터 파싱
#             response_data = response.json()
#             print()

#             rec_answer = response_data.get('answer', "결과를 찾을 수 없습니다.")
#             # print(f"rec_answer: {rec_answer}")
#             # print()

#             # 리스트 부분만 추출 (정규표현식 사용)
#             list_match = re.search(r"\[.*?\]", rec_answer)  # 대괄호 포함 문자열 찾기 
#             if list_match:
#                 titles_to_list = eval(list_match.group())  # 문자열을 리스트로 변환
#                 print(f'titles_to_list: {titles_to_list}')
#                 print()

#                 movie_code_list = []

#                 for title in titles_to_list:
#                     print("-------------------------------")
#                     if title in movie_titles:
#                         index = movie_titles.index(title)  # 제목의 인덱스를 찾음
#                         movie_code = movie_codes[index]  # 해당 제목에 맞는 movie_code를 가져옴
#                         print(movie_code)
#                         movie_code_list.append(movie_code)

#                 # 영화 코드 목록을 담은 URL을 만들어서 클라이언트에게 전달할 수 있도록 처리
#                 rec_urls = []  # 추천 URL 리스트

#                 # 영화 코드 리스트로 외부 API를 통해 영화 정보 가져오기
#                 for movie_code in movie_code_list:
#                     api_url = "http://www.kobis.or.kr/kobisopenapi/webservice/rest/movie/searchMovieInfo.json"
#                     params = {
#                         'key': KOBIS_API_KEY,  # API 키
#                         'movieCd': movie_code  # 영화 코드
#                     }

#                     try:
#                         # 외부 API 요청
#                         async with httpx.AsyncClient() as client:
#                             response = await client.get(api_url, params=params)
#                             if response.status_code == 200:
#                                 data = response.json()  # JSON 형식으로 응답 받기
#                                 rec_five_list = data.get('movieInfoList', {}).get('movieInfo', {})
                                
#                                 return JSONResponse(status_code=200, content={"rec_five_list": rec_five_list})
#                             else:
#                                 print(f"API 요청 실패: {response.status_code}")
#                     except Exception as e:
#                         print(f"API 요청 오류: {e}")

#                 try:
#                     # 추천 영화 정보를 DB에 저장
#                     rec_fav = RecFav(
#                         user_id=user_id,
#                         movie_code=str(movie_code_list)
#                     )
#                     db.add(rec_fav)  # DB에 추가
#                     db.commit()
#                     db.refresh(rec_fav)
#                     print("=======================================complete")
#                 except Exception as e:
#                     print(f"fail saving: {e}")

#             # 클라이언트에게 영화 정보를 전달하기 위해 background_tasks를 사용하여 UI 갱신
#             send_movie_recommendations_to_client(rec_urls)

#         except httpx.RequestError as exc:
#             print(f"An error occurred: {exc}")

# # 클라이언트로 영화 추천 정보를 전달하는 함수
# async def send_movie_recommendations_to_client(rec_urls: List[dict]):
#     # 클라이언트로 영화 정보를 보내는 예시 (여기서는 웹소켓이나 다른 메커니즘을 사용할 수 있음)
#     # 예시: 클라이언트에 정보를 보내는 코드 (실제 구현 필요)
#     print("추천 영화 정보:", rec_urls)


# 선택한 영화 데이터를 데이터베이스에 저장
@app.post("/save/{movieCd}")
async def save_movie(
    background_tasks: BackgroundTasks,
    movieCd: str,
    movie: MovieSaveRequest, 
    db: Session = Depends(get_db),
    access_token: Optional[str] = Cookie(None),  # 쿠키에서 access_token을 받음
    ):
    try:
        user = get_user_from_token(access_token, db)
        print("received data: ", movie.dict())
        
        # user_id와 code 조합 중복 체크
        existing_fav = db.query(UserFav).filter_by(user_id=user.id, code=movie.code).first()
        
        background_tasks.add_task(fetch_movie_recommendations, user.id, db)
        # await fetch_movie_recommendations(user.id, db)
        print("good")

        if existing_fav:
            return {"message": "중복된 값이 있습니다.", "user_id": user.id, "movie_code": movieCd}
            # 중복된 값이 있을 경우 메시지를 반환하고 종료
        else:
            # UserFav 객체 생성
            user_fav = UserFav(
                user_id=user.id,  # 사용자 ID
                code=movie.code,  # 영화 코드
                title=movie.title,  # 영화 제목
                director=movie.director,  # 감독 (리스트로 저장)
                actor=movie.actor,  # 배우 (리스트로 저장)
                genre=movie.genre,  # 장르 (리스트로 저장)
                nation=movie.nation,  # 국가 (리스트로 저장)
            )

            db.add(user_fav)  # DB에 추가
            
            try:
                db.commit()

            except Exception as e:
                db.rollback()  # 트랜잭션 롤백
                print(f"Commit failed: {e}") # 설정한 길이보다 데이터의 양이 많으면 저장 오류가 날 수 있다 >> 범위 늘리기 
                return {"message": "데이터 저장 중 문제가 발생했습니다.", "error": str(e)}

            db.refresh(user_fav)  # 새로 추가된 데이터 반영
            
            
            
            # 정상적으로 저장된 경우 메시지 반환
            return {"message": "영화 정보가 저장되었습니다.", "movie_code": movieCd}

    except Exception as e:
        db.rollback()  # 오류 발생 시 롤백
        raise HTTPException(status_code=500, detail=f"오류 발생: {str(e)}")
    
    
    
    
    
    
@app.post("/selected_movies")
async def selected_movies(
    # background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    access_token: Optional[str] = Cookie(None),  # 쿠키에서 access_token을 받음
    ):
        user = get_user_from_token(access_token, db)
        
        # user_id와 code 조합 중복 체크
        rec_fav = db.query(RecFav).filter_by(user_id=user.id).order_by(RecFav.id.desc()).first()
        print(f'========================================={rec_fav.movie_code}')
        rec_fav_list = eval(rec_fav.movie_code)
        print(f'========================================={type(rec_fav_list)}')
        
        movie_list = []
        for fav in rec_fav_list:
            print(fav)
            
            movie= db.query(UserFav).filter_by(code=fav).first()
            print(movie.title)
            movie_list.append(movie)

        
        return movie_list
    
    

    






# # 사용자 아이디로 추천 영화 목록을 가져오는 API
# @app.get("/rec_movies")
# async def rec_movies(
#     db: Session = Depends(get_db),
#     access_token: Optional[str] = Cookie(None),  # 쿠키에서 access_token을 받음
# ):
#     try:
#         # access_token으로 사용자 정보 가져오기
#         user = get_user_from_token(access_token, db)
        
#         if not user:
#             raise HTTPException(status_code=401, detail="Invalid or missing access token.")
        
#         # 사용자가 고른 영화 목록을 가져오기
#         user_fav_movies = db.query(UserFav).filter(UserFav.user_id == user.id).order_by(UserFav.id.desc()).limit(20).all()
#         # db.query(UserFav).order_by(UserFav.id.desc()).limit(20).all()
        
#         movie_titles = [movie.title for movie in user_fav_movies]
#         movie_codes = [movie.code for movie in user_fav_movies]
#         print(movie_titles)        
#         print(movie_codes)
#         print()
        
#         query = str(movie_titles)
#         role = (
#             "사용자가 입력한 리스트에서 랜덤으로 무조건 5개를 뽑아서 글자 변경 없이 그대로 가져와서 대괄호 안에 넣어서 리스트 형태로 보여줘. 여기서 1개의 기준은 따옴표 안에 있는 것이야."
#         )
        
#         rec_url = f'https://sixtick.duckdns.org/llmpost'
#         params = {
#             'role': role,
#             'query': query # 전송할 수 있도록 변환하는 과정인 직렬화 # 파이썬 객체를 문자열로 변환 
#         }
        
#         print(f"Requesting URL: {rec_url}?{requests.compat.urlencode(params)}")
#         # requests.compat.urlencode는 Python 2와 3에서 URL 인코딩을 다르게 처리할 수 있기 때문에, 두 버전에서 모두 동일하게 작동하도록 하기 위해 사용됩니다
#         print()
        
#         # httpx를 사용하여 외부 API로 요청
#         async with httpx.AsyncClient() as client: # httpx를 사용하여 비동기 HTTP 클라이언트를 생성합니다.
#             try:
#                 response = await client.post(rec_url, json=params)
#                 response.raise_for_status()  # HTTP 상태 확인
#                 print(response.text)
#                 print()

#                 # JSON 데이터 파싱
#                 response_data = response.json()  # 응답 텍스트를 JSON으로 변환
#                 # print(response_data)
#                 print()
#                 rec_answer = response_data.get('answer', "결과를 찾을 수 없습니다.")  # answer 키 추출
#                 print(f"rec_answer: {rec_answer}")
#                 print()
                
#                 # 리스트 부분만 추출 (정규표현식 사용)
#                 list_match = re.search(r"\[.*?\]", rec_answer)  # 대괄호 포함 문자열 찾기 
#                 if list_match:
#                     titles_to_list = eval(list_match.group())  # 문자열을 리스트로 변환
#                     print(f'titles_to_list: {titles_to_list}')
#                     print()
                    
#                     rec_urls = []  # 여러 개의 URL을 담을 리스트

#                     for title in titles_to_list:
#                         if title in movie_titles:  # 제목이 movie_titles에 있는지 확인
#                             index = movie_titles.index(title)  # 제목의 인덱스를 찾음
#                             movie_code = movie_codes[index]  # 해당 제목에 맞는 movie_code를 가져옴

#                             # URL 생성
#                             params = {
#                                 "key": KOBIS_API_KEY,
#                                 "movieCd": movie_code
#                             }
#                             rec_url = f"{MOVIE_DETAIL_URL}?{urlencode(params)}"
#                             print(f"Generated URL for movie '{title}': {rec_url}")  # URL 확인용 출력

#                             # movie_code와 일치하는 title을 클라이언트에게 표시 (console.log)
#                             print(f"Movie Code: {movie_code} corresponds to Title: {title}")

#                             rec_urls.append(rec_url)  # 생성된 URL을 리스트에 추가

#                 else:
#                     print("리스트를 찾을 수 없습니다.")
                
#             except httpx.HTTPStatusError as http_error:
#                 print(http_error)
#                 return JSONResponse(content={"error": f"HTTP Error: {http_error}"}, status_code=400)
#             except httpx.RequestError as request_error:
#                 print(request_error)
#                 return JSONResponse(content={"error": f"Request Error: {request_error}"}, status_code=400)
        
#         # 여러 개의 URL을 반환
#         print(f"rec_urls: {rec_urls}")  # 반환 직전에 출력 확인
#         return {"rec_urls": rec_urls}  # rec_urls 리스트 반환
            
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Error occurred-----------------------------: {str(e)}")
