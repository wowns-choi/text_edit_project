from fastapi import APIRouter, Request, Form
from app.schemas.edit_schemas import OriginalText
import re 
import app.services.edit_service as service 
# html 렌더링을 위함 --
from fastapi.responses import HTMLResponse, PlainTextResponse
from fastapi.templating import Jinja2Templates
# -- html 렌더링을 위함

from app.config import settings

router = APIRouter()

# Jinja2 템플릿 설정
templates = Jinja2Templates(directory="app/templates")

# HTML 렌더링 엔드포인트
@router.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    print("request.method == " + request.method) # 요청 메서드 
    print("request.url == " + str(request.url)) # 전체 URL 
    print("request.headers == " + str(request.headers)) # HTTP 요청 헤더 정보. 딕셔너리 형태 
    print("request.query_params == " + str(request.query_params)) # 쿼리 매개변수 (?key=value 형태)
    print("request.path_params == " + str(request.path_params)) # 경로 매개변수 (/items/{item_id} 에서 item_id 말하는 거임) 
    print("request.body() == " + str(request.body())) # 요청 본문 데이터 
    print("request.client == " + str(request.client)) # client 쪽 ip 주소와 포트 정보 


    return templates.TemplateResponse("index.html", {"request": request, "name": "FastAPI"}) # name 이라는 키로 데이터를 넘길 수 있음. 

# 2가지 버전이 있어야함. 
# 첫번째 버전 : 글 생성부터 저희가 쓴 로직이 주관하는 로직  
@router.post("/edit")
# @router.post("/edit", response_class=PlainTextResponse)
def edit(origin : OriginalText):
# def edit(
#     keyword: str = Form(...),
#     keywordCount: str = Form(...),
#     specialCharacters: str = Form(...)
# ):
    keyword = origin.keyword
    # keywordCount = origin.keywordCount
    sc = origin.specialCharacters
    # sc = specialCharacters

    # gpt assistant 로 글 생성 : 병원 원본 글 생성기 
    # thread Id 얻어오기 
    newThread = service.create_new_thread()
    threadId = newThread.id 

    print("키워드 : " + keyword)
    # print("키워드 개수 : " + keywordCount)
    print("특수문자 : " + sc)

    keywordCount = "5"

    # message 생성 
    msg = service.streamMessage(settings.GENERATOR_ASSISTANT_ID, threadId, "키워드: " + keyword )
    # msg = service.streamMessage("asst_YdB9mgjaIWjqgtmTkq803kh7", threadId, "키워드: " + keyword)
    totalStream = service.stream_run(threadId, settings.GENERATOR_ASSISTANT_ID)

    # 특수문자 사이사이 넣는 GPT (이미지 자리인듯) 호출. : 병원 특수문자 집어넣기
    newThread2 = service.create_new_thread()
    threadId = newThread2.id

    msg = service.streamMessage(settings.STYLING_ASSISTANT_ID, threadId, "특수문자: " + sc +", 글: " + totalStream)
    totalStream = service.stream_run(threadId, settings.STYLING_ASSISTANT_ID)


    # -- 정규표현식 시작 
    # 우선순위 1. (한자) <- 를 제거합니다. 
    # ot = re.sub(r"\([一-龯㐀-䶵豈-頻﨑-鶴]+\)", "", ot)   
    totalStream = re.sub(r"\([\u4E00-\u9FFF\u3400-\u4DBF]+\)", "", totalStream)
    # 우선순위 2. 특수문자를 한글로 바꾸기 by .replace 
    totalStream = totalStream.replace('%', "퍼센트")
    totalStream = totalStream.replace('℃', '도')

    # 우선순위 3. 남아있는 특수문자는 이 안(~!@#$%^&*(){}[]<>-_+=\|`:;'"①ⓟ②ⓑ③ⓤ④⑤ 등)에 있는 것 제외하고 다 제거. 
    # 허용할 특수문자 리스트.
    # , . / ` ' ~ ! @ # $ % ^ & * () {} [] <> _ - + = \ | : ; ' " ① ⓟ ② ⓑ ③ ⓤ ④ ⑤
    allowed_special_chars = r",./`'~!@#$%^&*(){}[]<>_-+=\\|:;\'\"①ⓟ②ⓑ③ⓤ④⑤"
    # 정규식으로 허용되지 않은 문자 제거. 위 특수문자, 영어(대소문자), 한글, 공백(\s) 를 제외하고는 전부 다 삭제합니다. 
    totalStream = re.sub(fr"[^{allowed_special_chars}A-Za-z0-9가-힣\s]", "", totalStream)

    # 우선순위 4. 영어 앞뒤에 숫자가 아닌 경우 공백 추가.
    # ([0-9A-Za-z]+) : 캡쳐 본체. "영어(/포함) + 뒤 숫자붙음" 또는 "영어(/포함)" 을 본체로 함.    
    # 두번째 파라미터인 r" \1 " 에서, \1 은 캡쳐 본체를 의미함. 따라서, 앞뒤로 공백 넣으라는 뜻이됩니다. 
    totalStream = re.sub(r"([A-Za-z/]+[0-9]*|[A-Za-z/])", r" \1 ", totalStream)

    # 단락별로 공백 정리 : 만약, 영단어 사이에 이미 공백이 있었던 경우, 공백이 2개 생기는 것을 방지. 
    totalStream = "\n".join([
        re.sub(r"\s+", " ", paragraph).strip()
        for paragraph in totalStream.split("\n")
    ])

    # 키워드 내에 있는 띄워쓰기를 가끔 없애버리는 문제 해결 

    print("==========================================================")
    print("totalStream==" + totalStream)

    # return totalStream

    return {"returnText" : totalStream}

