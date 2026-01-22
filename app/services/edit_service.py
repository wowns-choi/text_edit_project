from openai import OpenAI
import time
import requests
import json

from app.config import settings

client = OpenAI(api_key=settings.OPENAI_API_KEY)

# 쓰레드 생성 
def create_new_thread():
    thread = client.beta.threads.create()
    print(str(thread))
    return thread 

# 스트림용 메세지 생성 
def streamMessage(assistantId, threadId, message):
    messageResponse = client.beta.threads.messages.create(
    threadId,
    role="user",
    content=message,
    )

    return messageResponse

# GPT 가 응답 생성할 때 까지 기다리기
def wait_on_run(run, thread):
    while run.status == "queued" or run.status == "in_progress":
        run = client.beta.threads.runs.retrieve(
            thread_id=thread,
            run_id=run.id,
        )
        time.sleep(1)
    return run

# 최신 응답 조회 
def get_latest_response(threadId, lastMessageId):
    return client.beta.threads.messages.list(
        thread_id=threadId
        # order="asc", 
        # after=lastMessageId
    )

BASE_URL = "https://api.openai.com/v1"
# 스트림 
def stream_run(thread_id, assistant_id):
    url = f"{BASE_URL}/threads/{thread_id}/runs"
    headers = {
        "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
        "Content-Type": "application/json",
        "OpenAI-Beta": "assistants=v2"
    }
    payload = {
        "assistant_id": assistant_id,
        "stream": True
    }

    returnText = ""

    try:
        # json = payload : "요청" 본문의 바디가 json 형식입니다. 
        # as response : 응답 온 걸 response 라는 변수에 담겠다. 
        with requests.post(url, json=payload, headers=headers, stream=True) as response:
            # 상태코드가 200 이 아닐 경우 
            if response.status_code != 200:
                print(f"Error: {response.status_code}, {response.text}")
                return

            # 상태코드가 200 일 경우 
            print("Streaming response:")
            for line in response.iter_lines():
                if line:
                    # 받은 데이터를 utf-8 로 디코딩 후, 양쪽 공백 제거.
                    event_data = line.decode('utf-8').strip()

                    # 데이터가 "data:"로 시작하는지 확인. "data:"로 시작해야 유효한 데이터임.  
                    if event_data.startswith("data:"):
                        try:
                            # "data:" 이 5글자를 제거하고, json 형식의 문자열 -> 파이썬 딕셔너리로 변환  
                            event_json = json.loads(event_data[5:].strip())
                            # event_json.get() : 파이썬 딕셔너리에 object 라는 키에 들어있는 값 안에 delta 라는 값이 있다면
                            if "delta" in event_json.get("object", ""):
                                # delta 라는 키에 담겨있는 딕셔너리를 가져와. 
                                delta = event_json.get("delta", {})
                                if "content" in delta:
                                    print(delta["content"][0]["text"]["value"], end="")
                                    returnText = returnText + delta["content"][0]["text"]["value"]
                                    # yield delta["content"][0]["text"]["value"]

                        except json.JSONDecodeError:
                            print("Received invalid JSON:", event_data)
                            # yield f"Error decoding JSON: {event_data}\n"
        return returnText
        # return returnText
    except requests.RequestException as e:
        print(f"Request failed: {e}")



# 모든 대화 조회 
def get_all_conversations(thread_id):
    allMessages = []
    next_page = None 

    while True:
        response = client.beta.threads.messages.list(
            thread_id=thread_id,
            order="asc",
            limit=100, 
            after=next_page
        )

        for message in response.data:
            allMessages.append(str(message.role) + ": " + str(message.content[0].text.value))

        print(response.has_more)

        if not response.has_more:
            break
        
        next_page=response.data[99].id

    return allMessages


# -- 
# chatCompletion
def chatCompletion(message):
    completion = client.chat.completions.create(
        model="gpt-4o",
        messages = message
    )
    print(completion.choices[0].message)
    return completion.choices[0].message