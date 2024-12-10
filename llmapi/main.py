from fastapi import FastAPI    # FastAPI 는 Starlette 를 직접 상속하는 클래스임.
from fastapi.staticfiles import StaticFiles
import uvicorn

from langchain.chains import LLMChain
from langchain import PromptTemplate
from langchain.llms.ollama import Ollama # ollama LLM모델

llm = Ollama(base_url='http://127.0.0.1:11434', model='kor8b')
prompt = PromptTemplate(
    input_variables = ['description'],
    template=(
        "다음 설명에 어울리는 영화 제목을 콤마로 구분된 문자열로 반환해줘:\n"
        "설명: {description}\n"
        "응답 형식: 영화 제목1, 영화 제목2, ..."
    )
)
chain = LLMChain(llm = llm , prompt = prompt)
chain.run('대한민국')

# 역할을 설정할수있다.
# PROMPT = '''You are a helpful AI assistant. Please answer the user's questions kindly. 당신은 유능한 AI 어시스턴트 입니다. 사용자의 질문에 대해 친절하게 답변해주세요.'''
# instruction = "서울의 유명한 관광 코스를 만들어줄래?"

# messages = [
#     {"role": "system", "content": f"{PROMPT}"},
#     {"role": "user", "content": f"{instruction}"}
#     ]

# FastAPI 애플리케이션 인스턴스 생성
app = FastAPI()

# 기본 경로 "/"에 대한 GET 요청 처리
# @app.get("/")
# async def read_root():
#     return {"message": "Hello, World!"}


# 경로 "/items/{item_id}"에 대한 GET 요청 처리
@app.get("/items/{item_id}")
async def read_item(item_id: int, q: str = None):
    return {"item_id": item_id, "q": q}


@app.get("/text/{text}")
async def read_text(text: str, q: str = None):
    return {"text": text, "q": q}


@app.get("/llm/{text}")
async def read_llm(text: str, q: str = None):
    """
    ex)
    /llm/질의내용
    """
    answer = chain.run(text)
    return {"llm": text, "q": q, "answer" : answer}


# "static" 디렉토리를 정적 파일 제공 경로로 설정
app.mount("/", StaticFiles(directory="static", html=True), name="static")   # / 를 라우팅 할때 다른것들과 충돌 함. 맨 아래로 이동했음. 또는 경로를 /name 명확히 할 수 도 있음. 


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=18000)        #python main.py 로 실행시 작동