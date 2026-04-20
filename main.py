# main.py
# 역할: FastAPI 앱 진입점 — 정적 파일 서빙, 템플릿, 라우터 연결

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn

from backend.api import router as api_router

app = FastAPI(title="YouTube 키워드 분석기")

# 정적 파일(CSS, JS) 서빙
app.mount("/static", StaticFiles(directory="frontend/static"), name="static")

# Jinja2 템플릿 디렉터리
templates = Jinja2Templates(directory="frontend/templates")

# API 라우터 연결
app.include_router(api_router, prefix="/api")


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
