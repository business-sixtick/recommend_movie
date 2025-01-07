from app import FastAPI    # FastAPI 는 Starlette 를 직접 상속하는 클래스임.
from app.staticfiles import StaticFiles
import uvicorn
from app.middleware.cors import CORSMiddleware


from langchain.chains import LLMChain
from langchain import PromptTemplate
from langchain.llms.ollama import Ollama # ollama LLM모델

llm = Ollama(base_url='http://127.0.0.1:11434', model='kor8b')
prompt = PromptTemplate(
    input_variables = ['role', 'query'],
    # template=(
    #     "다음 설명에 어울리는 영화 제목을 콤마로 구분된 문자열로 반환해줘:\n"
    #     "설명: {description}\n"
    #     "응답 형식: 영화 제목1, 영화 제목2, ..."
    # )

    template =(
        '''<|start_header_id|> system <|end_header_id|> "{role}"
<|start_header_id|> user <|end_header_id|> "{query}" '''
    )
)
chain = LLMChain(llm = llm , prompt = prompt)
# chain.run('대한민국')

# FastAPI 애플리케이션 인스턴스 생성
app = FastAPI()

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 모든 도메인에서 요청 허용 (개발 환경에서는 "*"을 사용)
    allow_credentials=True,
    allow_methods=["*"],  # 모든 HTTP 메서드 허용 (GET, POST, PUT, DELETE 등)
    allow_headers=["*"],  # 모든 헤더 허용
)
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


@app.get("/llm")
async def read_llm(role: str ="사용자가 제시하는 단어에 연관이 깊은 영화 제목을 콤마로 구분해서 제목만 나열해줘.", query: str = "정우성"):
    """
    ex)
    /llm?role=영화박사&query=정우성
    """
    answer = chain.run({"role":role, "query": query})
    return {"role": role, "query": query, "answer": answer}

@app.post("/llmpost")
async def post_llm(role: str ="사용자가 제시하는 단어에 연관이 깊은 영화 제목을 콤마로 구분해서 제목만 나열해줘.", query: str = "정우성"):
    """
    ex)
    /llm?role=영화박사&query=정우성
    """
    answer = chain.run({"role":role, "query": query})
    return {"role": role, "query": query, "answer": answer}

# "static" 디렉토리를 정적 파일 제공 경로로 설정
app.mount("/", StaticFiles(directory="static", html=True), name="static")   # / 를 라우팅 할때 다른것들과 충돌 함. 맨 아래로 이동했음. 또는 경로를 /name 명확히 할 수 도 있음. 


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=18000)        #python main.py 로 실행시 작동



'''  라마 3.1 특수 토큰의 설명

이 형식은 Llama 모델의 텍스트 생성 및 상호작용을 관리하기 위한 **특수 토큰(Special Tokens)**과 **역할(Roles)**을 정의하는 시스템입니다. 각 토큰은 모델과의 대화 흐름을 제어하고, 여러 단계를 거치는 상호작용을 처리하는 데 도움을 줍니다.

1. 특수 토큰(Special Tokens) 설명
<|begin_of_text|>: 텍스트의 시작을 나타내는 토큰입니다. 모델이 텍스트를 생성하기 시작할 때 사용됩니다.

예시: <|begin_of_text|> 여기에 텍스트가 시작됩니다.
<|end_of_text|>: 텍스트의 끝을 나타내는 토큰입니다. 모델은 이 토큰을 만나면 더 이상 텍스트 생성을 진행하지 않습니다.

예시: 여기서 텍스트가 끝납니다. <|end_of_text|>
<|finetune_right_pad_id|>: 텍스트 시퀀스를 동일한 길이로 맞추는 데 사용되는 패딩 토큰입니다. 모델이 배치 처리 시 모든 입력이 동일한 길이를 갖도록 합니다.

<|start_header_id|>와 <|end_header_id|>: 특정 메시지의 역할을 구분하는 토큰입니다. 이 토큰들로 감싸진 부분은 메시지의 역할을 나타냅니다. 예를 들어, 시스템 메시지, 사용자 메시지 등입니다.

예시: <|start_header_id|> system <|end_header_id|> 시스템 설정 내용
<|eom_id|>: 메시지의 끝을 나타내는 토큰으로, 툴 호출이 필요할 때 모델이 이를 출력합니다. 여러 단계를 거치는 상호작용에서, 예를 들어 툴 호출이 요구될 때 사용됩니다.

예시: <|eom_id|> 툴 호출이 필요한 상황
<|eot_id|>: 대화의 종료를 나타내는 토큰으로, 사용자가 요청한 인터랙션을 모델이 완료했음을 의미합니다.

예시: <|eot_id|> 모델이 답변을 완료했습니다.
<|python_tag|>: 모델의 응답에서 툴 호출을 표시하는 특수 태그입니다. 툴을 호출할 때 사용됩니다.

예시: <|python_tag|> 코드를 실행합니다.
2. 지원되는 역할(Roles) 설명
Llama 텍스트 모델에서는 4가지 역할을 지원합니다. 각 역할은 대화 흐름을 정의하는 데 중요한 역할을 합니다.

system: 시스템 설정을 정의하는 역할입니다. 모델이 어떻게 상호작용할지에 대한 규칙이나 지침을 제공하는 메시지를 포함합니다.

예시: <|start_header_id|> system <|end_header_id|> 시스템은 사용자의 질문에 답하기 전에 적절한 규칙을 따릅니다.
user: 모델과 상호작용하는 인간 사용자 역할입니다. 사용자로부터 입력된 질문이나 명령이 포함됩니다.

예시: <|start_header_id|> user <|end_header_id|> "오늘 날씨는 어때?"
ipython: 툴 호출을 나타내는 역할입니다. 이 역할은 모델이 도구를 호출하고 그 결과를 반환할 때 사용됩니다. Llama 3.1에서 도입된 새로운 역할입니다.

예시: <|start_header_id|> ipython <|end_header_id|> 툴 호출 결과: "오늘의 날씨는 맑음입니다."
assistant: AI 모델이 생성한 응답을 나타내는 역할입니다. 시스템과 사용자로부터 받은 컨텍스트를 기반으로 모델이 생성한 출력입니다.

예시: <|start_header_id|> assistant <|end_header_id|> "오늘 날씨는 맑고 기온은 25도입니다."
3. 예시
시스템 메시지와 사용자 메시지
sql
코드 복사
<|start_header_id|> system <|end_header_id|> "사용자의 질문에 친절하게 답하되, 간단한 문장으로 대답하세요."
<|start_header_id|> user <|end_header_id|> "오늘 날씨는 어때?"
<|start_header_id|> assistant <|end_header_id|> "오늘 날씨는 맑고 기온은 25도입니다."
<|eom_id|> 툴 호출이 필요함
<|python_tag|> "기상 API를 호출하여 날씨 정보를 확인합니다."
<|eot_id|> "모델의 응답이 완료되었습니다."

'''



# 직접 기동시 nginx 없이 https 가 가능하다다
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=443, ssl_keyfile="/etc/letsencrypt/live/sixtick.duckdns.org/privkey.pem", ssl_certfile="/etc/letsencrypt/live/sixtick.duckdns.org/fullchain.pem")
