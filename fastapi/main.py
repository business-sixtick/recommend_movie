from fastapi import FastAPI, Depends, HTTPException, Request, Form
from fastapi.responses import RedirectResponse
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

# Database configuration
# DATABASE_URL = "mysql+pymysql://username:password@localhost/db_name"
DATABASE_URL = "mysql+pymysql://ahncho:dkswh18@192.168.0.26:3306/movie_fastapi"
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
    return RedirectResponse(url="/login", status_code=303)

# 회원 가입 페이지 제공
@app.get("/register", response_class=HTMLResponse)
def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})




# 로그인 페이지 제공 
@app.get("/login")
async def get_login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login")
async def login(username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    db_user = authenticate_user(db, username, password)
    if not db_user:
        raise HTTPException(status_code=401, detail="Incorrect username or password")

    access_token = create_access_token(
        data={"sub": db_user.username}, expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    # 로그인 성공 시 /list로 리다이렉트 (username을 동적으로 포함)
    response = RedirectResponse(url=f"/list/{username}", status_code=303)
    response.set_cookie(key="access_token", value=access_token)
    return response


@app.get("/logout")
async def logout(response: RedirectResponse):
    response.delete_cookie(key="access_token")  # 쿠키 삭제
    return RedirectResponse(url="/list")  # 로그아웃 후 list 페이지로 리다이렉트





# 현재 로그인한 사용자의 정보를 가져오는 api
@app.get("/users/me", response_model=dict)
def read_users_me(current_user: User = Depends(get_current_user)):
    return {"username": current_user.username}




@app.get("/list/{username}", response_class=HTMLResponse)
async def get_list(request: Request, username: str):
    # HTML 템플릿 렌더링
    return templates.TemplateResponse("list.html", {"request": request, "username": username})