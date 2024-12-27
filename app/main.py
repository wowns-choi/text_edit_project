from fastapi import FastAPI
import app.routers.edit_router as edit_router
# FastAPI 애플리케이션 인스턴스 생성
app = FastAPI()

# 라우터 등록
# app.include_router(assistant_router.router)
app.include_router(edit_router.router)