# frontend/templates/index.html

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn

app = FastAPI()

# CSS나 JS 같은 정적 파일을 불러올 수 있도록 static 폴더 연결
# directory 경로를 "frontend/static"으로 변경, URL 경로는 심플하게 "/static" 유지
app.mount("/static", StaticFiles(directory="frontend/static"), name="static")

# HTML 파일을 불러올 수 있도록 templates 폴더 연결
# directory 경로를 "frontend/templates"로 변경
templates = Jinja2Templates(directory="frontend/templates")

# 메인 화면 라우터
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    # 나중에 Supabase DB에서 가져올 샘플 데이터 (임시)
    sample_reports = [
        {
            "id": 1,
            "logo": "/static/twitter.svg", # 임시 파일 (추후 추가)
            "title": "AI Post on X",
            "url": "twitter.com/ai_news/status/123...",
            "status": "Completed",
            "time": "2h ago",
            "tags": ["AI", "News"]
        },
        {
            "id": 2,
            "logo": "/static/insta.svg", # 임시 파일 (추후 추가)
            "title": "Summer Collection Feedback",
            "url": "instagram.com/p/summer2026...",
            "status": "Completed",
            "time": "5h ago",
            "tags": ["Fashion", "Feedback"]
        },
    ]

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "app_logo": "SNS Summary",
            "reports": sample_reports,
        }
    )

# 서버 실행부
if __name__ == "__main__":
    # "main.py" 대신 "main:app"을 사용해야 reload가 작동합니다.
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)