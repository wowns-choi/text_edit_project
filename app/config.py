import os
from dotenv import load_dotenv

# .env 파일에서 환경 변수 로드
load_dotenv()

# 환경 변수 설정을 중앙에서 관리
class Settings:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    GENERATOR_ASSISTANT_ID = os.getenv("GENERATOR_ASSISTANT_ID")
    STYLING_ASSISTANT_ID = os.getenv("STYLING_ASSISTANT_ID")

# 인스턴스를 생성해 다른 곳에서 사용
settings = Settings()